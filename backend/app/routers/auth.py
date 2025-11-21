# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from typing import Optional
from app.utils import (
    OTP_STORE,
    get_password_hash,
    generate_otp,
    send_otp_email,
    verify_otp
)
import os
import shutil
import uuid

router = APIRouter(prefix="/auth", tags=["Auth"])

UPLOAD_DIR = "uploads"
PROFILE_DIR = os.path.join(UPLOAD_DIR, "profiles")
FINGERPRINT_DIR = os.path.join(UPLOAD_DIR, "fingerprints")
os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(FINGERPRINT_DIR, exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def save_file(file: UploadFile, folder: str) -> str:
    ext = file.filename.split(".")[-1]
    name = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(folder, name)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return f"/{UPLOAD_DIR}/{os.path.basename(folder)}/{name}"

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(401, "Utilisateur non trouvé")
    return user

@router.post("/register")
async def register(
    nom: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    photo_profil: Optional[UploadFile] = File(None),
    empreinte_1: Optional[UploadFile] = File(None), doigt_1: Optional[str] = Form(None),
    empreinte_2: Optional[UploadFile] = File(None), doigt_2: Optional[str] = Form(None),
    empreinte_3: Optional[UploadFile] = File(None), doigt_3: Optional[str] = Form(None),
    empreinte_4: Optional[UploadFile] = File(None), doigt_4: Optional[str] = Form(None),
    empreinte_5: Optional[UploadFile] = File(None), doigt_5: Optional[str] = Form(None),
    empreinte_6: Optional[UploadFile] = File(None), doigt_6: Optional[str] = Form(None),
    empreinte_7: Optional[UploadFile] = File(None), doigt_7: Optional[str] = Form(None),
    empreinte_8: Optional[UploadFile] = File(None), doigt_8: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:  # <-- début du bloc try correctement indenté
    
        if db.query(models.User).filter(models.User.email == email).first():
            raise HTTPException(400, "Email déjà utilisé")

        hashed = get_password_hash(password)
        photo_path = None
        if photo_profil and photo_profil.filename:
            photo_path = save_file(photo_profil, PROFILE_DIR)

        user = models.User(nom=nom, email=email, password=hashed, photo_profil=photo_path)
        db.add(user)
        db.commit()
        db.refresh(user)

        empreintes = [
            (empreinte_1, doigt_1), (empreinte_2, doigt_2),
            (empreinte_3, doigt_3), (empreinte_4, doigt_4),
            (empreinte_5, doigt_5), (empreinte_6, doigt_6),
            (empreinte_7, doigt_7), (empreinte_8, doigt_8),
        ]

        for file, doigt in empreintes:
            if file and file.filename:
                path = save_file(file, FINGERPRINT_DIR)
                fp = models.Fingerprint(
                    utilisateur_id=user.id,
                    image_path=path,
                    doigt=doigt
                )
                db.add(fp)

        db.commit()

        otp = generate_otp(email)
        if not send_otp_email(email, otp):
            raise HTTPException(500, "Échec envoi OTP")

        return {"message": "Inscription réussie. OTP envoyé.", "email": email}

    except Exception as e:  # <-- fin du bloc try
        print("Erreur backend:", e)
        raise HTTPException(500, f"Erreur serveur: {str(e)}")
    
    # ==================== CONNEXION ====================
@router.post("/login")
async def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(401, "Email ou mot de passe incorrect")
    if not verify_password(password, user.password):  # ← TU DOIS AVOIR CETTE FONCTION
        raise HTTPException(401, "Email ou mot de passe incorrect")

    # Génère et envoie un nouvel OTP
    otp = generate_otp(email)
    send_otp_email(email, otp)
    return {"message": "Code OTP envoyé", "email": email}

# ==================== VÉRIFICATION OTP → RENVOIE LE VRAI PROFIL ====================
@router.post("/verify-otp")
async def verify_otp_login(email: str = Form(...), code: str = Form(...), db: Session = Depends(get_db)):
    if not verify_otp(email, code):
        raise HTTPException(400, "Code OTP incorrect")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(404, "Utilisateur introuvable")

    return {
        "id": user.id,
        "nom": user.nom,
        "email": user.email,
        "photo_profil": f"http://127.0.0.1:8000{user.photo_profil}" if user.photo_profil else "https://via.placeholder.com/120",
        "message": "Connexion réussie"
    }
