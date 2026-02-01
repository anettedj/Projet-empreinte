# backend/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import auth_router
from app.routers import comparison


os.makedirs("uploads/profiles", exist_ok=True)
os.makedirs("uploads/fingerprints", exist_ok=True)
os.makedirs("static/fingerprints", exist_ok=True)
os.makedirs("static/users", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Empreintes API")

# CORS doit être le premier middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(auth_router)

@app.get("/")
def home():
    return {"message": "API Empreintes - Authentification prête"}

app.include_router(comparison.router)
from app.routers import process

app.include_router(process.router)
# backend/app/main.py
from app.routers import search  

app.include_router(search.router)