import sys
import os
import secrets
from werkzeug.security import generate_password_hash

# Add the current directory to sys.path to import local modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from models import db, Usuario

def reset_admin():
    with app.app_context():
        admin = Usuario.query.filter_by(email='admin@filarmonica.org').first()
        if admin:
            # Generate a strong, random password
            new_password = secrets.token_urlsafe(16)
            admin.senha_hash = generate_password_hash(new_password)
            db.session.commit()

            # Save the new password to a file with restricted permissions
            password_file = 'admin_password.txt'
            with open(password_file, 'w') as f:
                f.write(f"Email: admin@filarmonica.org\nSenha: {new_password}")

            print(f"Senha do administrador resetada com sucesso!")
            print(f"A nova senha foi salva em '{password_file}'.")
            print("Por favor, mova este arquivo para um local seguro.")
        else:
            print("Usuário administrador não encontrado.")

if __name__ == "__main__":
    reset_admin()
