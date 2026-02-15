# backend/app/routers/process.py
from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import io
import base64
from app.utils.manual_algo import (
    manual_grayscale, normalize_image, enhance_contrast, 
    segment_fingerprint, manual_median_filter, manual_binarize, 
    morphological_operations, manual_thinning, manual_gabor
)

router = APIRouter(prefix="/process", tags=["Traitement"])

def process_fingerprint(img_bgr: np.ndarray, stage: str):
    if stage == "original": return img_bgr

    # 1. Grayscale
    gray = manual_grayscale(img_bgr)
    if stage == "grayscale": return gray

    # 2. Normalisation
    norm = normalize_image(gray)
    if stage == "normalize": return norm

    # 3. CLAHE
    enhanced = enhance_contrast(norm)
    if stage == "enhanced" or stage == "clahe": return enhanced

    # 4. Segmentation (ROI)
    mask = segment_fingerprint(enhanced)
    if stage == "mask": return mask
    
    # 5. Application masque
    segmented = cv2.bitwise_and(enhanced, enhanced, mask=mask)
    if stage == "segmented": return segmented

    # 6. Médian
    filtered = manual_median_filter(segmented)
    if stage == "filtered": return filtered

    # 6b. Gabor (Renforcement crêtes)
    if stage == "gabor":
        return manual_gabor(segmented)

    # 7. Binaire
    binary = manual_binarize(filtered, invert=True)
    if stage == "binary": return binary
    
    # 8. Morphologie
    morphed = morphological_operations(binary)
    if stage == "morphed": return morphed

    # 9. Squelette
    skel = manual_thinning(morphed)
    if stage == "skeleton": return skel

    # Par défaut on retourne l'original si le stage n'est pas reconnu
    return img_bgr

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
def analyze_fingerprints(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    stage: str = Form("skeleton")
):
    # 1. Lire les images (synchrone)
    c1 = file1.file.read()
    c2 = file2.file.read()
    nparr1 = np.frombuffer(c1, np.uint8)
    nparr2 = np.frombuffer(c2, np.uint8)
    img1 = cv2.imdecode(nparr1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imdecode(nparr2, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        return {"error": "Une des images est invalide"}

    # NOTE: Pour l'analyse, on utilise désormais le matcher MANUEL
    # On passe les images brutes au pipeline complet.
    from app.utils.manual_algo import complete_preprocessing_pipeline, manual_match
    
    m1, _ = complete_preprocessing_pipeline(img1)
    m2, _ = complete_preprocessing_pipeline(img2)
    
    if m1 is None or m2 is None:
         return {"error": "Impossible d'extraire les minuties"}

    # Comparaison
    score, matches = manual_match(m1, m2)
    # print(f"DEBUG: Process Score={score}, Matches={matches}")
    
    match_result = "CORRESPONDANCE CONFIRMÉE" if score > 15 else "AUCUNE CORRESPONDANCE"
    
    # On récupère aussi les images traitées juste pour l'affichage visuel "proc1/proc2"
    proc1 = process_fingerprint(img1, stage)
    proc2 = process_fingerprint(img2, stage)

    # 6. Génération de l'explication (Pédagogie)
    explanation = (
        f"Analyse effectuée avec la méthode Manuelle (Minuties).\n\n"
        f"1. **Minuties Trouvées :** {len(m1[0])} (Img1) vs {len(m2[0])} (Img2).\n"
        f"2. **Correspondances Géométriques :** {matches} points s'alignent parfaitement.\n"
        f"3. **Score :** {score:.2f}%.\n\n"
    )

    # 7. Encoder en Base64 pour le frontend
    def to_b64(cv_img):
        _, buf = cv2.imencode(".jpg", cv_img)
        return "data:image/jpeg;base64," + base64.b64encode(buf).decode("utf-8")

    return {
        "image1_processed": to_b64(proc1),
        "image2_processed": to_b64(proc2),
        "match_visualization": to_b64(proc1), # Visualisation simple pour l'instant
        "explanation": explanation,
        "stats": {
            "keypoints_img1": len(m1[0]),
            "keypoints_img2": len(m2[0]),
            "matches": matches,
            "score": score
        }
    }
