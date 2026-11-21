import unittest
from app import app, recovery_tokens
from models import db, Usuario
from werkzeug.security import check_password_hash, generate_password_hash

class TestRecuperacaoSenha(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Cria um usuário de teste
        self.user = Usuario(
            nome="Usuario Teste",
            email="teste@filarmonica.org",
            senha_hash=generate_password_hash("senha123")
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        recovery_tokens.clear()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_esqueci_minha_senha_sucesso(self):
        # Envia formulário com e-mail cadastrado
        response = self.client.post('/esqueci-minha-senha', data={
            'email': 'teste@filarmonica.org'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'C\xc3\xb3digo de recupera\xc3\xa7\xc3\xa3o:', response.data)
        # Deve ter gerado um token no dicionário
        self.assertEqual(len(recovery_tokens), 1)

    def test_esqueci_minha_senha_email_nao_encontrado(self):
        # Envia formulário com e-mail não cadastrado
        response = self.client.post('/esqueci-minha-senha', data={
            'email': 'naoexiste@filarmonica.org'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'E-mail n\xc3\xa3o encontrado', response.data)
        self.assertEqual(len(recovery_tokens), 0)

    def test_recuperar_senha_token_invalido(self):
        # Tenta acessar com token que não existe
        response = self.client.get('/recuperar-senha/token_invalido', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Token inv\xc3\xa1lido ou expirado', response.data)

    def test_recuperar_senha_sucesso(self):
        # Adiciona um token válido manualmente
        token = "token_de_teste_valido"
        recovery_tokens[token] = self.user.id

        # Envia formulário de nova senha
        response = self.client.post(f'/recuperar-senha/{token}', data={
            'senha': 'novasenha123',
            'confirmar_senha': 'novasenha123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Senha alterada com sucesso', response.data)

        # Verifica se a senha foi alterada no banco
        user_atualizado = Usuario.query.get(self.user.id)
        self.assertTrue(check_password_hash(user_atualizado.senha_hash, 'novasenha123'))
        # O token deve ser removido após o uso
        self.assertNotIn(token, recovery_tokens)

if __name__ == '__main__':
    unittest.main()
