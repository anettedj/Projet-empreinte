
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

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
            names = ['Blaise', 'Oumar', 'Adjo']
            query = "SELECT id, nom FROM utilisateur WHERE nom LIKE %s OR nom LIKE %s OR nom LIKE %s"
            cursor.execute(query, ('%Blaise%', '%Oumar%', '%Adjo%'))
            users = cursor.fetchall()
            
            print("Users found:", users)
            
            if not users:
                print("No users found with those names.")
                return

            user_ids = [u['id'] for u in users]
            format_strings = ','.join(['%s'] * len(user_ids))
            
            # Get fingerprints for these users
            query = f"SELECT utilisateur_id, image_path, doigt FROM empreinte WHERE utilisateur_id IN ({format_strings})"
            cursor.execute(query, tuple(user_ids))
            fingerprints = cursor.fetchall()
            
            print("\nFingerprints associated with these users:")
            for fp in fingerprints:
                user_name = [u['nom'] for u in users if u['id'] == fp['utilisateur_id']][0]
                print(f"User: {user_name}, Image Path: {fp['image_path']}, Finger: {fp['doigt']}")

            # Check for duplicates across ALL users
            print("\nChecking for duplicate image paths across the entire database:")
            query = "SELECT image_path, COUNT(*) as count FROM empreinte GROUP BY image_path HAVING count > 1"
            cursor.execute(query)
            duplicates = cursor.fetchall()
            
            if duplicates:
                print("Duplicate image paths found:")
                for d in duplicates:
                    print(f"Image: {d['image_path']} is used {d['count']} times.")
                    # Find which users share this image
                    query = "SELECT u.nom FROM utilisateur u JOIN empreinte e ON u.id = e.utilisateur_id WHERE e.image_path = %s"
                    cursor.execute(query, (d['image_path'],))
                    shared_users = cursor.fetchall()
                    names = [su['nom'] for su in shared_users]
                    print(f"  Shared by: {', '.join(names)}")
            else:
                print("No duplicate image paths found.")

    finally:
        connection.close()

if __name__ == "__main__":
    check_users()
