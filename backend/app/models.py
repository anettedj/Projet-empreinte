# backend/app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "utilisateur"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    photo_profil = Column(String(255), nullable=True)
    date_creation = Column(DateTime, server_default=func.now(), nullable=False)

    empreintes = relationship("Fingerprint", back_populates="user")


class Fingerprint(Base):
    __tablename__ = "empreinte"
    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=False, index=True)
    image_path = Column(String(255), nullable=False)
    date_upload = Column(DateTime, server_default=func.now(), nullable=False)
    doigt = Column(String(20), nullable=True)
    minutiae_data = Column(Text, nullable=True)
    match_percentage = Column(Float, nullable=True)

    user = relationship("User", back_populates="empreintes")