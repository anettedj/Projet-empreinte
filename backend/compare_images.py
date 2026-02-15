
import pymysql
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

def get_hash(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def check_users():
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            # Get users info
            query = "SELECT id, nom FROM utilisateur WHERE nom IN ('Blaise', 'Oumar', 'Adjo')"
            cursor.execute(query)
            users = cursor.fetchall()
            
            user_data = {}
            for u in users:
                query = "SELECT image_path FROM empreinte WHERE utilisateur_id = %s"
                cursor.execute(query, (u['id'],))
                fps = cursor.fetchall()
                hashes = []
                for fp in fps:
                    full_path = os.path.join(os.getcwd(), fp['image_path'])
                    h = get_hash(full_path)
                    if h:
                        hashes.append((fp['image_path'], h))
                user_data[u['nom']] = hashes

            for name, hashes in user_data.items():
                print(f"\n--- {name} ---")
                for path, h in hashes:
                    print(f"{path} -> {h}")

            # Find common hashes
            all_hashes = {}
            for name, hashes in user_data.items():
                for path, h in hashes:
                    if h not in all_hashes:
                        all_hashes[h] = []
                    all_hashes[h].append((name, path))

            print("\nShared images (same content):")
            for h, owners in all_hashes.items():
                if len(set(o[0] for o in owners)) > 1:
                    print(f"Hash {h} shared by:")
                    for owner in owners:
                        print(f"  {owner[0]} ({owner[1]})")

    finally:
        connection.close()

if __name__ == "__main__":
    check_users()
