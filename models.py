from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabela Usuário
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)

# Tabela Evento
class Evento(db.Model):
    __tablename__ = 'eventos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    data = db.Column(db.Date, nullable=False)
    local = db.Column(db.String(150))
    horario = db.Column(db.Time)
    descricao = db.Column(db.Text)
    responsavel = db.Column(db.String(150))
    status = db.Column(db.String(30), default='Agendado')
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario = db.relationship('Usuario', backref='eventos', lazy=True)

# Adicionando campo usuario_id na tabela Aluno para o Perfil do Aluno
class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    celular = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    rua = db.Column(db.String(150), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    usuario = db.relationship('Usuario', backref='aluno_perfil', lazy=True)
    emprestimos = db.relationship('Emprestimo', backref='aluno', lazy=True)

    @property
    def endereco(self):
        partes = [p for p in [self.rua, self.numero, self.bairro] if p]
        return ', '.join(partes) if partes else 'Sem endereço'