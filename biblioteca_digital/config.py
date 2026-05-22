import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "app/db/biblioteca.db")
    PROPRIETARIO_EMAIL = os.getenv("PROPRIETARIO_EMAIL", "admin@empresa.com")
    PROPRIETARIO_PASSWORD = os.getenv("PROPRIETARIO_PASSWORD", "senha_segura")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"
