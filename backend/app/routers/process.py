# backend/app/routers/process.py
from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import io
import base64
from app.utils.fingerprint_matcher import align_and_match_fingerprints

router = APIRouter(prefix="/process", tags=["Traitement"])

def process_fingerprint(img_gray: np.ndarray, stage: str):
    if stage == "original":
        return img_gray

    # 1. CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(img_gray)

    if stage == "clahe":
        return enhanced

    # 2. Gabor (Correction: Utilisation de float32 pour accumuler sans saturation)
    gabor_accum = np.zeros_like(enhanced, dtype=np.float32)
    for i in range(16):
        theta = np.pi * i / 16
        kernel = cv2.getGaborKernel((31, 31), 4.0, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)
        fimg = cv2.filter2D(enhanced, cv2.CV_32F, kernel)
        np.maximum(gabor_accum, fimg, gabor_accum)

    # Normalisation 0-255
    gabor = cv2.normalize(gabor_accum, None, 0, 255, cv2.NORM_MINMAX)
    gabor = gabor.astype(np.uint8)

    if stage == "gabor":
        return gabor

    # 3. Binaire
    # Otsu fonctionne mieux sur l'image normalisée
    _, binary = cv2.threshold(gabor, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Nettoyage morphologique (Fermeture)
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close)
    
    # [CRITICAL STEP] Inversion Intelligente pour Squelettisation
    # La squelettisation de OpenCV (ximgproc) suppose que le FOND est NOIR (0) et l'OBJET est BLANC (255).
    if cv2.countNonZero(binary) > (binary.size / 2):
         binary = cv2.bitwise_not(binary)

    if stage == "binary":
        return binary

    # 4. Squelette (Algorithme de Zhang-Suen explicite)
    img = binary.copy()
    img = img // 255 
    
    changed = True
    while changed:
        changed = False
        pixels_to_remove = []

        # SOUS-ÉTAPE 1 
        #B = le nombre de voisins “blancs” (crêtes) autour du pixel central P1
        # On itère sur tous les pixels (sauf bords)
        rows, cols = img.shape
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                P1 = img[i, j]
                if P1 != 1: continue

                P2, P3, P4 = img[i-1, j], img[i-1, j+1], img[i, j+1]
                P5, P6, P7 = img[i+1, j+1], img[i+1, j], img[i+1, j-1]
                P8, P9 = img[i, j-1], img[i-1, j-1]

                neighbors = [P2, P3, P4, P5, P6, P7, P8, P9]
                B = sum(neighbors)
                # Count 0->1 transitions
                A = 0
                for k in range(len(neighbors)):
                    if neighbors[k] == 0 and neighbors[(k + 1) % 8] == 1:
                        A += 1

                if (2 <= B <= 6) and (A == 1) and (P2 * P4 * P6 == 0) and (P4 * P6 * P8 == 0):
                    pixels_to_remove.append((i, j))

        if pixels_to_remove:
            changed = True
            for i, j in pixels_to_remove:
                img[i, j] = 0

        pixels_to_remove = []

        # SOUS-ÉTAPE 2
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                P1 = img[i, j]
                if P1 != 1: continue

                P2, P3, P4 = img[i-1, j], img[i-1, j+1], img[i, j+1]
                P5, P6, P7 = img[i+1, j+1], img[i+1, j], img[i+1, j-1]
                P8, P9 = img[i, j-1], img[i-1, j-1]

                neighbors = [P2, P3, P4, P5, P6, P7, P8, P9]
                B = sum(neighbors)
                A = 0
                for k in range(len(neighbors)):
                    if neighbors[k] == 0 and neighbors[(k + 1) % 8] == 1:
                        A += 1

                if (2 <= B <= 6) and (A == 1) and (P2 * P4 * P8 == 0) and (P2 * P6 * P8 == 0):
                    pixels_to_remove.append((i, j))

        if pixels_to_remove:
            changed = True
            for i, j in pixels_to_remove:
                img[i, j] = 0

    skel = (img * 255).astype(np.uint8)
    
    return skel

@router.post("/")
async def process_image(
    file: UploadFile = File(...),
    stage: str = Form("skeleton")  # "original" | "clahe" | "gabor" | "binary" | "skeleton"
):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"error": "Image invalide"}

    result = process_fingerprint(img, stage)

    _, buffer = cv2.imencode(".jpg", result)
    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/jpeg")

@router.post("/analyze")
async def analyze_fingerprints(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    stage: str = Form("skeleton")
):
    # 1. Lire les images
    c1 = await file1.read()
    c2 = await file2.read()
    nparr1 = np.frombuffer(c1, np.uint8)
    nparr2 = np.frombuffer(c2, np.uint8)
    img1 = cv2.imdecode(nparr1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imdecode(nparr2, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        return {"error": "Une des images est invalide"}

    # NOTE: Pour l'analyse, on utilise désormais le matcher UNIFIÉ ROBUSTE 
    # au lieu d'une réimplémentation locale. Cela garantit la cohérence.
    # On passe les images brutes au matcher qui gère son propre prétraitement.
    
    match_result = align_and_match_fingerprints(img1, img2)
    
    # On récupère aussi les images traitées juste pour l'affichage visuel "proc1/proc2"
    proc1 = process_fingerprint(img1, stage)
    proc2 = process_fingerprint(img2, stage)

    vis_img = match_result["image"] if match_result["image"] is not None else proc1

    # 6. Génération de l'explication (Pédagogie)
    explanation = (
        f"Analyse effectuée avec la méthode Officielle (ORB + RANSAC).\n\n"
        f"1. **Minuties Trouvées :** {match_result['kp1_count']} (Img1) vs {match_result['kp2_count']} (Img2).\n"
        f"2. **Correspondances Géométriques :** {match_result['match_count']} points s'alignent parfaitement.\n"
        f"3. **Score :** {match_result['score']}% (Calculé sur la zone visible commune).\n\n"
        "Si l'image est coupée, le score reste élevé car on ignore les parties manquantes."
    )

    # 7. Encoder en Base64 pour le frontend
    def to_b64(cv_img):
        _, buf = cv2.imencode(".jpg", cv_img)
        return "data:image/jpeg;base64," + base64.b64encode(buf).decode("utf-8")

    return {
        "image1_processed": to_b64(proc1),
        "image2_processed": to_b64(proc2),
        "match_visualization": to_b64(vis_img),
        "explanation": explanation,
        "stats": {
            "keypoints_img1": match_result['kp1_count'],
            "keypoints_img2": match_result['kp2_count'],
            "matches": match_result['match_count'],
            "score": match_result['score']
        }
    }
