import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-fallback-segura')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_kvd73yIPxpDV@ep-late-brook-bdvsmktn.c-8.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True