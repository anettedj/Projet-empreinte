"""
Script d'importation de TOUTES les bases de données FVC disponibles
Importe tous les datasets pour maximiser le nombre de personnes avec empreintes
"""

import mysql.connector
import os
import glob
from datetime import datetime

# Configuration de la base de données
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'empreintes_db'
}

# Définir tous les datasets à importer avec leurs IDs de départ
DATASETS = [
    # Format: (chemin, nom, user_id_start)
    ("images/fvc/DB1_B", "DB1_B", 1),           # Déjà fait mais on vérifie
    ("images/fvc/DB3_B", "DB3_B", 11),          # Déjà fait mais on vérifie
    ("images/fvc/DB4_B", "DB4_B", 21),          # Déjà fait mais on vérifie
    ("images/fvc/DB1_B (1)", "DB1_B(1)", 41),   # NOUVEAU
    ("images/fvc/DB2_B (1)", "DB2_B(1)", 51),   # NOUVEAU
    ("images/fvc/DB3_B (1)", "DB3_B(1)", 61),   # NOUVEAU
    ("images/fvc/DB3_Bj", "DB3_Bj", 71),        # NOUVEAU
    ("images/fvc/DB4_B (1)", "DB4_B(1)", 81),   # NOUVEAU
]

def connect_db():
    """Connexion à la base de données"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Erreur de connexion: {err}")
        return None

def import_dataset(cursor, dataset_path, dataset_name, start_user_id):
    """
    Importe un dataset complet dans la base de données
    """
    print(f"\n📂 {dataset_name}...", end=" ")
    
    # Vérifier que le dossier existe
    if not os.path.exists(dataset_path):
        print(f"❌ Dossier inexistant")
        return 0
    
    # Lister tous les fichiers .tif
    files = sorted(glob.glob(os.path.join(dataset_path, "*.tif")))
    
    if not files:
        print(f"❌ Aucun fichier .tif")
        return 0
    
    # Grouper les fichiers par personne
    person_files = {}
    for file in files:
        basename = os.path.basename(file)
        person_id = basename.split('_')[0]
        finger_num = basename.split('_')[1].split('.')[0]
        
        if person_id not in person_files:
            person_files[person_id] = []
        person_files[person_id].append((finger_num, file))
    
    # Insérer les empreintes
    inserted_count = 0
    skipped_count = 0
    
    for person_id in sorted(person_files.keys()):
        user_id = start_user_id + (int(person_id) - 101)
        
        # Vérifier que l'utilisateur existe
        cursor.execute("SELECT id FROM utilisateur WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            continue
        
        # Insérer les empreintes
        for finger_num, file_path in sorted(person_files[person_id]):
            rel_path = file_path.replace("\\", "/")
            
            # Vérifier si existe déjà
            cursor.execute(
                "SELECT id FROM empreinte WHERE utilisateur_id = %s AND image_path = %s",
                (user_id, rel_path)
            )
            
            if cursor.fetchone():
                skipped_count += 1
                continue
            
            # Insérer
            cursor.execute("""
                INSERT INTO empreinte (utilisateur_id, image_path, doigt, date_upload)
                VALUES (%s, %s, %s, %s)
            """, (user_id, rel_path, f"doigt{finger_num}", datetime.now()))
            
            inserted_count += 1
    
    if inserted_count > 0:
        print(f"✅ {inserted_count} nouvelles empreintes")
    elif skipped_count > 0:
        print(f"⏭️  Déjà importé ({skipped_count} empreintes)")
    else:
        print(f"⚠️  Aucune empreinte ajoutée")
    
    return inserted_count

def main():
    print("=" * 70)
    print("🔧 IMPORTATION COMPLÈTE DE TOUTES LES BASES DE DONNÉES FVC")
    print("=" * 70)
    
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # État initial
        cursor.execute("SELECT COUNT(DISTINCT utilisateur_id) FROM empreinte WHERE utilisateur_id <= 100")
        initial_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM empreinte WHERE utilisateur_id <= 100")
        initial_fingerprints = cursor.fetchone()[0]
        
        print(f"\n📊 État AVANT importation:")
        print(f"   • Utilisateurs avec empreintes: {initial_users}")
        print(f"   • Total d'empreintes: {initial_fingerprints}")
        
        # Importer tous les datasets
        print(f"\n🚀 Importation de {len(DATASETS)} bases de données...")
        print("-" * 70)
        
        total_inserted = 0
        for dataset_path, dataset_name, start_user_id in DATASETS:
            count = import_dataset(cursor, dataset_path, dataset_name, start_user_id)
            total_inserted += count
        
        # Commit
        conn.commit()
        
        # État final
        cursor.execute("SELECT COUNT(DISTINCT utilisateur_id) FROM empreinte WHERE utilisateur_id <= 100")
        final_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM empreinte WHERE utilisateur_id <= 100")
        final_fingerprints = cursor.fetchone()[0]
        
        print("\n" + "=" * 70)
        print("✅ IMPORTATION TERMINÉE")
        print("=" * 70)
        print(f"   • Nouvelles empreintes ajoutées: {total_inserted}")
        print(f"\n📊 État APRÈS importation:")
        print(f"   • Utilisateurs avec empreintes: {final_users} (était {initial_users})")
        print(f"   • Total d'empreintes: {final_fingerprints} (était {initial_fingerprints})")
        print(f"   • Gain: +{final_users - initial_users} utilisateurs, +{final_fingerprints - initial_fingerprints} empreintes")
        
        # Détail par base
        print(f"\n📋 Répartition par base de données:")
        for dataset_path, dataset_name, start_user_id in DATASETS:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM empreinte 
                WHERE image_path LIKE %s
            """, (f"%{dataset_name.replace('(', '%').replace(')', '%')}%",))
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"   • {dataset_name:15} : {count:3} empreintes")
        
    except mysql.connector.Error as err:
        print(f"\n❌ Erreur SQL: {err}")
        conn.rollback()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
