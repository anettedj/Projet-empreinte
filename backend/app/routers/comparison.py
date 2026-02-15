# backend/app/routers/comparison.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import os
import base64
from app.utils.manual_algo import complete_preprocessing_pipeline, manual_match
import json

router = APIRouter(prefix="/compare", tags=["Comparaison Biométrique"])

# Charger le seuil optimal (par défaut 20% si non calculé)
CONFIG_PATH = "config/optimal_threshold.json"
def get_threshold():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f).get("threshold", 20.0)
        except:
            return 20.0
    return 20.0

# Dossier temporaire pour les uploads
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/")
def compare_fingerprints(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    # Sauvegarde temporaire
    path1 = os.path.join(TEMP_DIR, f"temp1_{file1.filename}")
    path2 = os.path.join(TEMP_DIR, f"temp2_{file2.filename}")

    try:
        # Écriture des fichiers (synchrone)
        with open(path1, "wb") as f:
            f.write(file1.file.read())
        with open(path2, "wb") as f:
            f.write(file2.file.read())

        # Chargement images
        img1 = cv2.imread(path1)
        img2 = cv2.imread(path2)
        
        if img1 is None or img2 is None:
            raise HTTPException(400, "Image invalide ou format non supporté")

        # PIPELINE BIOMÉTRIQUE MANUEL (OFFICIEL)
        minutiae1, skel1 = complete_preprocessing_pipeline(img1)
        minutiae2, skel2 = complete_preprocessing_pipeline(img2)
        
        # Matching robuste
        score, matches = manual_match(minutiae1, minutiae2)
        
        # Décision basée sur le seuil optimal
        threshold = get_threshold()
        
        if score >= threshold:
            verdict = "Identité confirmée"
            decision_code = "MATCH"
        else:
            verdict = "Identité rejetée"
            decision_code = "NO_MATCH"

        # Conversion squelette en base64 pour affichage
        def to_b64(img):
            _, buf = cv2.imencode(".jpg", img)
            return "data:image/jpeg;base64," + base64.b64encode(buf).decode("utf-8")

        return {
            "similarity": score,
            "matches_found": matches,
            "minutiae_img1": len(minutiae1[0]) + len(minutiae1[1]),
            "minutiae_img2": len(minutiae2[0]) + len(minutiae2[1]),
            "verdict": verdict,
            "decision": decision_code,
            "threshold_used": threshold,
            "visualization": to_b64(skel1), # On montre le squelette de l'img1
            "details": {
                "algo": "Manual Pipeline (Preprocessing + CN + Triplet Validation)",
                "steps": "Normalisation -> CLAHE -> Segmentation -> Filtrage -> Binarisation -> Morphologie -> Squelettisation -> Crossing Number -> Filtrage"
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
