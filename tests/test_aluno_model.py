import unittest
from app import app
from models import db, Aluno, Usuario

class TestAlunoModel(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_aluno_has_usuario_id_and_relationship(self):
        user = Usuario(nome="João Aluno", email="joao@teste.com", senha_hash="hash")
        db.session.add(user)
        db.session.commit()

        aluno = Aluno(nome="João Aluno", usuario_id=user.id)
        db.session.add(aluno)
        db.session.commit()

        aluno_db = Aluno.query.get(aluno.id)
        self.assertEqual(aluno_db.usuario_id, user.id)
        self.assertEqual(aluno_db.usuario.email, "joao@teste.com")

if __name__ == '__main__':
    unittest.main()
