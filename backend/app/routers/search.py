# backend/app/routers/search.py
from fastapi import APIRouter, File, UploadFile, HTTPException
import cv2
import numpy as np
import os
from pathlib import Path
from sqlalchemy import create_engine, text

router = APIRouter(prefix="/search", tags=["Recherche"])

# Connexion MySQL
DATABASE_URL = "mysql+pymysql://root:@localhost/empreintes_db"
engine = create_engine(DATABASE_URL)

def preprocess_image(path):
    # Lecture en niveau de gris
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None, None
        
    # Amélioration CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    img = clahe.apply(img)
    
    # ORB Detector
    orb = cv2.ORB_create(nfeatures=2000)
    kp, desc = orb.detectAndCompute(img, None)
    return kp, desc

def compare_descriptors(desc1, desc2):
    if desc1 is None or desc2 is None or len(desc1) < 5 or len(desc2) < 5:
        return 0.0

    # BFMatcher avec NORM_HAMMING
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False) # On utilise kNN
    matches = bf.knnMatch(desc1, desc2, k=2)

    good_matches = []
    for match in matches:
        if len(match) == 2:
            m, n = match
            # Lowe's ratio test stricter (0.7)
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)
    
    # Calcul score basé sur le nombre de matches vs le nombre total de features du query
    # C'est plus robuste que de diviser par une constante
    
    score = 0
    if len(desc1) > 0:
        score = (len(good_matches) / len(desc1)) * 100.0
        
    # Bonus pour le nombre absolu de matches (pour éviter les faux positifs sur très peu de features)
    if len(good_matches) < 10:
        score = 0 # Trop peu de correspondance pour être fiable
        
    # Scale le score pour qu'il soit plus lisible (ex: 20% de features matchées = tres bon score)
    # On va dire que 40% de match = 100% score affiché
    final_similarity = min(100.0, score * 2.5) 
    
    return final_similarity

@router.post("/")
async def search_fingerprint(fingerprint: UploadFile = File(...)):
    import uuid
    import traceback

    # Sauvegarde temporaire avec UUID pour éviter les conflits
    file_ext = fingerprint.filename.split(".")[-1]
    unique_id = str(uuid.uuid4())
    temp_filename = f"temp_{unique_id}.{file_ext}"

    try:
        with open(temp_filename, "wb") as f:
            f.write(await fingerprint.read())

        # Extraction query
        kp_q, desc_q = preprocess_image(temp_filename)
        
        if desc_q is None:
            return {"matches": []}

        best_results = []

        # 1. Récupérer toutes les empreintes de la BDD
        with engine.connect() as conn:
            # On joint pour avoir les infos user direct
            # CORRECTION: Suppression de u.prenom qui n'existe pas
            query = text("""
                SELECT e.image_path, e.utilisateur_id, u.nom, u.photo_profil
                FROM empreinte e
                JOIN utilisateur u ON e.utilisateur_id = u.id
            """)
            rows = conn.execute(query).fetchall()

        print(f"Search: Found {len(rows)} fingerprints in DB")

        # 2. Comparer avec chaque empreinte
        user_scores = {} # Max score par user

        for row in rows:
            db_path = row.image_path
            
            # Correction des chemins absolue/relatif si nécessaire
            full_path = db_path
            if not os.path.isabs(full_path):
                # Essayer de résoudre par rapport au dossier courant ou static
                candidates = [
                    os.path.abspath(db_path),
                    os.path.join(os.getcwd(), db_path),
                    os.path.join(os.getcwd(), "uploads", "fingerprints", os.path.basename(db_path)),
                    db_path.replace("//", "/")
                ]
                
                full_path = None
                for c in candidates:
                    if os.path.exists(c):
                        full_path = c
                        break
                
                if full_path is None:
                    # print(f"DEBUG: File not found {db_path}")
                    continue

            if not os.path.exists(full_path):
                # print(f"DEBUG: File not found {full_path}")
                continue # Fichier introuvable

            kp_db, desc_db = preprocess_image(full_path)
            if desc_db is None:
                # print(f"DEBUG: Failed to process {full_path}")
                continue

            similarity = compare_descriptors(desc_q, desc_db)

            if similarity > 5: # Filtre mini
                uid = row.utilisateur_id
                if uid not in user_scores or similarity > user_scores[uid]["similarity"]:
                    user_scores[uid] = {
                        "nom": row.nom,
                        # "prenom": getattr(row, 'prenom', ''), # REMOVED
                        "photo_profil": row.photo_profil,
                        "similarity": similarity
                    }

        # 3. Formatter résultats
        results = list(user_scores.values())
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Mapper pour le frontend
        final_output = []
        for r in results[:10]:
            photo = r["photo_profil"]
            if photo and not photo.startswith("http"):
                 photo = f"http://127.0.0.1:8000{photo}"
                 
            final_output.append({
                "nom": r["nom"],
                "prenom": "", # Frontend expects it, send empty
                "photo_profil": photo,
                "similarity": round(r["similarity"], 2)
            })

        return {"matches": final_output}

    except Exception as e:
        print("ERROR processing search:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Nettoyage
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except:
                pass