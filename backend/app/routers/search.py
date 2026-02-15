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

from app.utils.manual_algo import complete_preprocessing_pipeline, manual_match
import json

# Charger le seuil (par défaut 20%)
CONFIG_PATH = "config/optimal_threshold.json"
def get_threshold():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f).get("threshold", 20.0)
        except:
            return 20.0
    return 20.0

# Charger le cache des minuties pour accélérer la recherche
MINUTIAE_CACHE_FILE = "config/minutiae_cache.json"
minutiae_cache = {}

if os.path.exists(MINUTIAE_CACHE_FILE):
    try:
        with open(MINUTIAE_CACHE_FILE, "r") as f:
            raw_cache = json.load(f)
            # Normaliser les clés du cache pour une recherche insensible aux séparateurs
            for k, v in raw_cache.items():
                norm_k = os.path.normpath(k).replace("\\", "/")
                minutiae_cache[norm_k] = v
        print(f"✅ Cache minuties chargé et normalisé: {len(minutiae_cache)} images")
    except Exception as e:
        print(f"⚠️ Erreur chargement cache: {e}")

def get_minutiae_for_search(path):
    """Extrait les minuties (depuis le cache si dispo, sinon calcul)."""
    # Normalisation du chemin input
    norm_path = os.path.normpath(path).replace("\\", "/")
    
    # Stratégies de recherche dans le cache
    keys_to_try = [norm_path, os.path.basename(norm_path)]
    parts = norm_path.split("/")
    if len(parts) >= 2:
        heuristic = f"images/fvc/{parts[-2]}/{parts[-1]}"
        keys_to_try.append(heuristic)
        
    # Essayer de changer l'extension (.jpg -> .tif) pour le cache
    base, ext = os.path.splitext(norm_path)
    if ext.lower() == '.jpg':
        keys_to_try.append(base + '.tif')
        if len(parts) >= 2:
             keys_to_try.append(heuristic.replace('.jpg', '.tif'))
    
    # 1. Recherche exacte ou relative
    if norm_path in minutiae_cache:
        return minutiae_cache[norm_path]
    
    # 2. Recherche par suffixe (pour gérer les différences abs/rel)
    for k in minutiae_cache:
        if norm_path.endswith(k) or k.endswith(norm_path):
            return minutiae_cache[k]

    print(f"⚠️ Cache miss pour: {path} (Norm: {norm_path}), calcul en cours...")
    
    # Si pas dans le cache, on calcule
    img = cv2.imread(path)
    if img is None: 
        print(f"❌ Erreur lecture image: {path}")
        return None
        
    try:
        minutiae, _ = complete_preprocessing_pipeline(img)
        return minutiae
    except Exception as e:
        print(f"❌ Erreur pipeline pour {path}: {e}")
        return None

@router.post("/")
def search_fingerprint(file: UploadFile = File(...)):
    import uuid
    import traceback

    # NOTE: On utilise 'def' au lieu de 'async def' pour ne pas bloquer l'évent loop
    # avec les calculs CPU intensifs (matching de 800 images). FastAPI gérera ça dans un pool.

    # Sauvegarde temporaire avec UUID pour éviter les conflits
    file_ext = file.filename.split(".")[-1]
    unique_id = str(uuid.uuid4())
    temp_filename = f"temp_{unique_id}.{file_ext}"

    try:
        with open(temp_filename, "wb") as f:
            # On lit en synchrone via .file.read()
            f.write(file.file.read())

        # Extraction query
        m_q = get_minutiae_for_search(temp_filename)
        threshold = get_threshold()
        
        if m_q is None:
            return {"matches": []}

        best_results = []

        # 1. Récupérer toutes les empreintes de la BDD
        with engine.connect() as conn:
            # On joint pour avoir les infos user direct
            # CORRECTION: On utilise empreintes_db (le .env dit ça, et le test confirme)
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
            # ET gestion de l'extension (.jpg dans la DB vs .tif sur le disque)
            candidates = [db_path]
            if db_path.endswith('.jpg'): candidates.append(db_path.replace('.jpg', '.tif'))
            if db_path.endswith('.tif'): candidates.append(db_path.replace('.tif', '.jpg'))
            
            full_path = None
            for cand in candidates:
                # Tester plusieurs racines
                test_paths = [
                    cand,
                    os.path.abspath(cand),
                    os.path.join(os.getcwd(), cand),
                    os.path.join(os.getcwd(), "app", cand),
                    os.path.join(os.getcwd(), "images", "fvc", os.path.basename(cand)) 
                ]
                for tp in test_paths:
                    if os.path.exists(tp):
                        full_path = tp
                        break
                if full_path: break
                
                if full_path is None:
                    # print(f"DEBUG: File not found {db_path}")
                    continue

            if not os.path.exists(full_path):
                # print(f"DEBUG: File not found {full_path}")
                continue # Fichier introuvable

            if not os.path.exists(full_path):
                # print(f"DEBUG: File not found {full_path}")
                continue # Fichier introuvable

            # Utiliser la nouvelle fonction d'extraction
            m_db = get_minutiae_for_search(full_path)
            if m_db is None:
                # print(f"SKIP: No minutiae for {full_path}")
                continue

            # Utiliser le nouveau matching manuel
            score, _ = manual_match(m_q, m_db)
            
            # DEBUG
            # if score > 0: print(f"MATCH: {db_path} => {score}%")

            if score >= 5: # Filtre mini (très bas pour laisser passer les candidats)
                uid = row.utilisateur_id
                if uid not in user_scores or score > user_scores[uid]["similarity"]:
                    user_scores[uid] = {
                        "nom": row.nom,
                        # "prenom": getattr(row, 'prenom', ''), 
                        "photo_profil": row.photo_profil,
                        "similarity": score
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