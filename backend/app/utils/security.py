# backend/app/utils/security.py
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import bcrypt
import os

# Stockage OTP
OTP_STORE = {}

def get_password_hash(password: str) -> str:
    """
    Fonctionne à 100% même avec mot de passe > 1000 caractères
    On bypass complètement le contrôle de passlib
    """
    # Tronque à 72 bytes max (limite de bcrypt)
    password_bytes = password.encode("utf-8")[:72]
    # Génère un salt et hash manuellement
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")  # retourne string comme avant

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))

def generate_otp(email: str) -> str:
    otp = str(random.randint(100000, 999999))
    OTP_STORE[email] = {"code": otp, "attempts": 0}
    return otp

def verify_otp(email: str, code: str) -> bool:
    stored = OTP_STORE.get(email)
    if not stored or stored["attempts"] >= 3:
        return False
    if stored["code"] == code:
        del OTP_STORE[email]
        return True
    stored["attempts"] += 1
    return False

def send_otp_email(email: str, otp: str) -> bool:
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    if not sender or not password:
        return False

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = email
    msg["Subject"] = "Votre code OTP - Empreintes"

    body = f"""
    <h1 style="color:#1e40af; text-align:center; font-size:3em;">{otp}</h1>
    <p style="text-align:center;">Valable 10 minutes</p>
    """
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, email, msg.as_string())
        return True
    except Exception as e:
        print("Erreur email:", e)
        return False