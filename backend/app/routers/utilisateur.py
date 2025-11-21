# backend/app/routers/utilisateur.py
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
import shutil

router = APIRouter()

@router.post("/photo")
async def upload_photo(
    utilisateur_id: int,
    file: UploadFile,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == utilisateur_id).first()
    if not user:
        raise HTTPException(404, "Utilisateur non trouvé")

    filename = f"{utilisateur_id}_{file.filename}"
    raw_path = f"uploads/profiles/{filename}"
    public_path = f"static/users/{filename}"
    public_url = f"/static/users/{filename}"

    with open(raw_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    shutil.copy2(raw_path, public_path)

    user.photo_profil = public_url
    db.commit()

    return {"photo_url": f"http://127.0.0.1:8000{public_url}"}