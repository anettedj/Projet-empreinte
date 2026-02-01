# backend/app/routers/comparison.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import os
import base64
from app.utils.fingerprint_matcher import align_and_match_fingerprints

router = APIRouter(prefix="/compare", tags=["Comparaison Biométrique"])

# Dossier temporaire pour les uploads
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/")
async def compare_fingerprints(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    if not file1.filename.lower().endswith(('png', 'jpg', 'jpeg', 'bmp')) or \
       not file2.filename.lower().endswith(('png', 'jpg', 'jpeg', 'bmp')):
        raise HTTPException(400, "Format d'image non supporté")

    # Sauvegarde temporaire
    path1 = os.path.join(TEMP_DIR, f"temp1_{file1.filename}")
    path2 = os.path.join(TEMP_DIR, f"temp2_{file2.filename}")

    try:
        # Écriture des fichiers
        with open(path1, "wb") as f:
            f.write(await file1.read())
        with open(path2, "wb") as f:
            f.write(await file2.read())

        # UTILISATION DU MATCHING UNIFIÉ (OFFICIEL)
        result = align_and_match_fingerprints(path1, path2)
        
        similarity = result["score"]
        matches = result["match_count"]
        
        # Interprétation - C'est ici qu'on fait la nuance
        # Si le score est faible (ex: 40%) MAIS qu'il y a beaucoup de correspondances (>15),
        # c'est une "Correspondance Partielle (Identité Probable)".
        
        if similarity > 80:
            verdict = "Identité confirmée (Image Identique)"
        elif matches > 15: # Forensic Standard : 12-15 points suffisent
            verdict = "Identité confirmée (Image Partielle/Modifiée)"
        elif similarity > 50:
            verdict = "Correspondance Probable"
        elif similarity > 25:
            verdict = "Correspondance Faible"
        else:
            verdict = "Pas de correspondance"

        # Conversion image visu en base64 pour affichage optionnel
        vis_b64 = ""
        if result["image"] is not None:
            _, buf = cv2.imencode(".jpg", result["image"])
            vis_b64 = "data:image/jpeg;base64," + base64.b64encode(buf).decode("utf-8")

        return {
            "similarity": similarity,
            "matches_found": result["match_count"],
            "total_keypoints": result["kp1_count"] + result["kp2_count"],
            "minutiae_img1": result["kp1_count"],
            "minutiae_img2": result["kp2_count"],
            "verdict": verdict,
            "message": f"{verdict} ({similarity}%)",
            "visualization": vis_b64,
            "details": {
                "algo": "ORB + RANSAC (Geometric Verification)",
                "description": "Analyse des minuties assistée par vérification géométrique (invariante rotation/échelle)."
            }
        }

    except Exception as e:
        print(f"Error in comparison: {e}")
        raise HTTPException(500, f"Erreur lors de la comparaison: {str(e)}")
    finally:
        # Nettoyage
        for p in [path1, path2]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass
