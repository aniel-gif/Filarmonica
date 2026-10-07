from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Tabela Usuário
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)

# Tabela Aluno
class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    celular = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    rua = db.Column(db.String(150), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    emprestimos = db.relationship('Emprestimo', backref='aluno', lazy=True)

# Tabela Instrumento
class Instrumento(db.Model):
    __tablename__ = 'instrumentos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=True)
    numero_serie = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(30), default='Disponível')
    emprestimos = db.relationship('Emprestimo', backref='instrumento', lazy=True)

# Tabela Empréstimo
class Emprestimo(db.Model):
    __tablename__ = 'emprestimos'
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    instrumento_id = db.Column(db.Integer, db.ForeignKey('instrumentos.id'), nullable=False)
    data_emprestimo = db.Column(db.DateTime, default=datetime.utcnow)
    data_devolucao_prevista = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), default='Em andamento')

# Tabela Evento
class Evento(db.Model):
    __tablename__ = 'evento'
    id_evento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    data = db.Column(db.Date, nullable=False)
    local = db.Column(db.String(150))
    horario = db.Column(db.Time)
    descricao = db.Column(db.Text)