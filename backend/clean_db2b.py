
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def clean_db():
    print("🧹 Cleaning database (Removing DB2_B)...")
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            # Check how many to delete
            cursor.execute("SELECT COUNT(*) as count FROM empreinte WHERE image_path LIKE '%DB2_B/%' OR image_path LIKE '%\\\\DB2_B\\\\%'")
            count = cursor.fetchone()['count']
            print(f"Items to delete: {count}")
            
            if count > 0:
                cursor.execute("DELETE FROM empreinte WHERE image_path LIKE '%DB2_B/%' OR image_path LIKE '%\\\\DB2_B\\\\%'")
                connection.commit()
                print(f"✅ Deleted {count} fingerprints.")
            else:
                print("No DB2_B fingerprints found.")

    finally:
        connection.close()

if __name__ == "__main__":
    clean_db()
