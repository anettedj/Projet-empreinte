import pymysql
import os

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='empreintes_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("✅ Connexion réussie à 'empreintes'")
    with conn.cursor() as cursor:
        cursor.execute("SELECT image_path, utilisateur_id FROM empreinte LIMIT 5")
        rows = cursor.fetchall()
        print("Sample rows from 'empreinte':")
        for r in rows:
            print(f"- {r['image_path']} (User ID: {r['utilisateur_id']})")
            
        cursor.execute("DESCRIBE utilisateur")
        cols = cursor.fetchall()
        print("\nColumns in 'utilisateur':", [c['Field'] for c in cols])
        
    conn.close()
except Exception as e:
    print(f"❌ Erreur DB: {e}")
