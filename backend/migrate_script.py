import os
import cv2
from pathlib import Path
from sqlalchemy import create_engine, text

# Configuration
# Adapter si mot de passe root défini
DATABASE_URL = "mysql+pymysql://root:@localhost/empreintes_db"
SOURCE_DIR = Path("images/fvc/DB1_B")
TARGET_EXT = ".jpg"

def run_migration():
    print("--- Démarrage Migration ---")
    
    # 1. Connexion DB
    engine = create_engine(DATABASE_URL)
    
    files_processed = 0
    records_to_insert = []
    
    # 2. Parcours et Conversion
    if not SOURCE_DIR.exists():
        print(f"Erreur: Dossier {SOURCE_DIR} introuvable (lancer depuis racine projet ?)")
        return

    for tiff_file in SOURCE_DIR.glob("*.tif"):
        # Conversion
        img = cv2.imread(str(tiff_file))
        if img is None:
            print(f"Impossible de lire {tiff_file}")
            continue
            
        new_filename = tiff_file.stem + TARGET_EXT
        new_path = tiff_file.parent / new_filename
        
        cv2.imwrite(str(new_path), img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        
        # Préparation Données BDD
        # Nom fichier attendu: 101_1.tif -> user 101 -> id 1
        try:
            parts = tiff_file.stem.split("_")
            code_user = int(parts[0])
            user_id = code_user - 100
        except:
            print(f"Ignoré (nom non standard): {tiff_file}")
            continue
            
        # Chemin relatif CLEAN pour la BDD (compatible frontend via static mount)
        # On suppose que STATIC pointe sur backend/images ou similaire.
        # Mais le frontend use souvent http://localhost:8000/static/... ou uploads
        
        # Ici on va stocker le chemin RELATIF par rapport au dossier backend
        # ex: images/fvc/DB1_B/101_1.jpg
        relative_path = f"images/fvc/DB1_B/{new_filename}"
        
        records_to_insert.append({
            "uid": user_id,
            "path": relative_path,
            "doigt": f"doigt{parts[1] if len(parts)>1 else '1'}"
        })
        files_processed += 1

    print(f"{files_processed} images converties en JPG.")

    # 3. Mise à jour SQL
    with engine.begin() as conn:
        print("Vidage de la table empreinte...")
        conn.execute(text("TRUNCATE TABLE empreinte"))
        
        print(f"Insertion de {len(records_to_insert)} nouvelles entrées...")
        for rec in records_to_insert:
            conn.execute(
                text("INSERT INTO empreinte (utilisateur_id, image_path, doigt) VALUES (:uid, :path, :doigt)"),
                rec
            )
            
    print("--- Migration Terminée avec Succès ! ---")

if __name__ == "__main__":
    run_migration()
