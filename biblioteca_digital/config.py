import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        if os.getenv("FLASK_ENV") == "development":
            SECRET_KEY = "dev_only_key_change_in_prod"
        else:
            raise ValueError("No SECRET_KEY set for production environment!")
            
    DATABASE_PATH = os.getenv("DATABASE_PATH", "app/db/biblioteca.db")
    PROPRIETARIO_EMAIL = os.getenv("PROPRIETARIO_EMAIL", "admin@empresa.com")
    PROPRIETARIO_PASSWORD = os.getenv("PROPRIETARIO_PASSWORD", "senha_segura")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
