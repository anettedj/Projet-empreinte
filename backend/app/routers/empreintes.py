# backend/app/routers/empreintes.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Fingerprint, User
import shutil
import os

router = APIRouter()

@router.post("/upload")
async def upload_empreinte(
    utilisateur_id: int,
    doigt: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == utilisateur_id).first()
    if not user:
        raise HTTPException(404, "Utilisateur non trouvé")

    # 1. Sauvegarde brute
    filename = f"{utilisateur_id}_{doigt}_{file.filename}"
    raw_path = f"uploads/fingerprints/{filename}"
    with open(raw_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 2. Copie publique
    public_path = f"static/fingerprints/{filename}"
    shutil.copy2(raw_path, public_path)

    # 3. URL publique
    public_url = f"/static/fingerprints/{filename}"

    # 4. Sauvegarde en BDD
    emp = Fingerprint(
        utilisateur_id=utilisateur_id,
        image_path=public_url,
        doigt=doigt
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)

    return {
        "message": "Empreinte uploadée",
        "raw_path": raw_path,
        "public_url": f"http://127.0.0.1:8000{public_url}",
        "empreinte_id": emp.id
    }