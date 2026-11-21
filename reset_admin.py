import sys
import os
from werkzeug.security import generate_password_hash

# Add the current directory to sys.path to import local modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from models import db, Usuario

def reset_admin():
    with app.app_context():
        admin = Usuario.query.filter_by(email='admin@filarmonica.org').first()
        if admin:
            admin.senha_hash = generate_password_hash('admin123')
            db.session.commit()
            print("Senha do administrador resetada com sucesso!")
            print("Email: admin@filarmonica.org")
            print("Senha: admin123")
        else:
            print("Usuário administrador não encontrado.")

if __name__ == "__main__":
    reset_admin()
