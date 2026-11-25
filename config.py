import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable must be set")
    # Default to local SQLite for development. In production, set DATABASE_URL env var.
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///filarmonica.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True