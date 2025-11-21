# backend/app/create_tables.py
from app.database import Base, engine
from app.models import User, Fingerprint  # les noms exacts que tu utilises

# crée toutes les tables définies par les modèles
Base.metadata.create_all(bind=engine)

print("Tables créées avec succès !")
