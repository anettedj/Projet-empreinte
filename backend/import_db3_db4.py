"""
Script d'importation des bases de données DB3_B et DB4_B
Ajoute les empreintes pour les utilisateurs existants qui n'en ont pas encore.
"""

import mysql.connector
import os
import glob
from datetime import datetime

# Configuration de la base de données
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',  # Modifier si vous avez un mot de passe
    'database': 'empreintes_db'
}

# Chemins des datasets
DB3_PATH = "images/fvc/DB3_B"
DB4_PATH = "images/fvc/DB4_B"

def connect_db():
    """Connexion à la base de données"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Erreur de connexion: {err}")
        return None

def get_users_without_fingerprints(cursor):
    """Récupère les utilisateurs qui n'ont pas encore d'empreintes"""
    cursor.execute("""
        SELECT u.id, u.nom 
        FROM utilisateur u 
        LEFT JOIN empreinte e ON u.id = e.utilisateur_id 
        WHERE e.id IS NULL AND u.id <= 100
        ORDER BY u.id
    """)
    return cursor.fetchall()

def import_dataset(cursor, dataset_path, dataset_name, start_user_id):
    """
    Importe un dataset complet dans la base de données
    
    Args:
        cursor: Curseur MySQL
        dataset_path: Chemin vers le dataset (ex: images/fvc/DB3_B)
        dataset_name: Nom du dataset (ex: DB3_B)
        start_user_id: ID de départ pour les utilisateurs
    """
    print(f"\n📂 Importation de {dataset_name}...")
    
    # Vérifier que le dossier existe
    if not os.path.exists(dataset_path):
        print(f"❌ Le dossier {dataset_path} n'existe pas!")
        return 0
    
    # Lister tous les fichiers .tif
    files = sorted(glob.glob(os.path.join(dataset_path, "*.tif")))
    
    if not files:
        print(f"❌ Aucun fichier .tif trouvé dans {dataset_path}")
        return 0
    
    print(f"✅ {len(files)} fichiers trouvés")
    
    # Grouper les fichiers par personne (101_1.tif, 101_2.tif, etc.)
    person_files = {}
    for file in files:
        basename = os.path.basename(file)
        person_id = basename.split('_')[0]  # Ex: "101" de "101_1.tif"
        finger_num = basename.split('_')[1].split('.')[0]  # Ex: "1" de "101_1.tif"
        
        if person_id not in person_files:
            person_files[person_id] = []
        person_files[person_id].append((finger_num, file))
    
    print(f"✅ {len(person_files)} personnes détectées (IDs: {min(person_files.keys())} à {max(person_files.keys())})")
    
    # Insérer les empreintes
    inserted_count = 0
    
    for person_id in sorted(person_files.keys()):
        # Calculer l'ID utilisateur dans la base
        # 101 -> start_user_id, 102 -> start_user_id+1, etc.
        user_id = start_user_id + (int(person_id) - 101)
        
        # Vérifier que l'utilisateur existe
        cursor.execute("SELECT id, nom FROM utilisateur WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"⚠️  Utilisateur ID {user_id} n'existe pas, ignoré")
            continue
        
        print(f"  👤 {user[1]} (ID {user_id}): ", end="")
        
        # Insérer les empreintes pour cette personne
        for finger_num, file_path in sorted(person_files[person_id]):
            # Chemin relatif pour la base de données
            rel_path = file_path.replace("\\", "/")
            
            # Vérifier si l'empreinte existe déjà
            cursor.execute(
                "SELECT id FROM empreinte WHERE utilisateur_id = %s AND image_path = %s",
                (user_id, rel_path)
            )
            
            if cursor.fetchone():
                print(f".", end="")  # Déjà existant
                continue
            
            # Insérer l'empreinte
            cursor.execute("""
                INSERT INTO empreinte (utilisateur_id, image_path, doigt, date_upload)
                VALUES (%s, %s, %s, %s)
            """, (user_id, rel_path, f"doigt{finger_num}", datetime.now()))
            
            inserted_count += 1
            print(f"{finger_num}", end="")
        
        print()  # Nouvelle ligne après chaque personne
    
    return inserted_count

def main():
    print("=" * 60)
    print("🔧 IMPORTATION DES BASES DE DONNÉES DB3_B ET DB4_B")
    print("=" * 60)
    
    # Connexion
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # Afficher l'état actuel
        cursor.execute("SELECT COUNT(*) FROM utilisateur WHERE id <= 100")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT utilisateur_id) FROM empreinte WHERE utilisateur_id <= 100")
        users_with_fingerprints = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM empreinte WHERE utilisateur_id <= 100")
        total_fingerprints = cursor.fetchone()[0]
        
        print(f"\n📊 État actuel de la base de données:")
        print(f"   • Utilisateurs (ID 1-100): {total_users}")
        print(f"   • Utilisateurs avec empreintes: {users_with_fingerprints}")
        print(f"   • Utilisateurs SANS empreintes: {total_users - users_with_fingerprints}")
        print(f"   • Total d'empreintes: {total_fingerprints}")
        
        # Importer DB3_B (utilisateurs 11-20)
        count_db3 = import_dataset(cursor, DB3_PATH, "DB3_B", start_user_id=11)
        
        # Importer DB4_B (utilisateurs 21-30)
        count_db4 = import_dataset(cursor, DB4_PATH, "DB4_B", start_user_id=21)
        
        # Commit
        conn.commit()
        
        # Afficher le résumé
        print("\n" + "=" * 60)
        print("✅ IMPORTATION TERMINÉE")
        print("=" * 60)
        print(f"   • DB3_B: {count_db3} empreintes ajoutées")
        print(f"   • DB4_B: {count_db4} empreintes ajoutées")
        print(f"   • TOTAL: {count_db3 + count_db4} nouvelles empreintes")
        
        # Nouvel état
        cursor.execute("SELECT COUNT(DISTINCT utilisateur_id) FROM empreinte WHERE utilisateur_id <= 100")
        new_users_with_fingerprints = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM empreinte WHERE utilisateur_id <= 100")
        new_total_fingerprints = cursor.fetchone()[0]
        
        print(f"\n📊 Nouvel état:")
        print(f"   • Utilisateurs avec empreintes: {new_users_with_fingerprints}")
        print(f"   • Total d'empreintes: {new_total_fingerprints}")
        
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
