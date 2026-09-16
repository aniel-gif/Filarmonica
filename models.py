from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Aluno(db.Model):
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False, index=True)
    endereco = db.Column(db.String(255), nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    emprestimos = db.relationship('Emprestimo', backref='aluno', lazy=True, cascade="all, delete-orphan")

class Instrumento(db.Model):
    __tablename__ = 'instrumentos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    identificacao = db.Column(db.String(100), nullable=True)
    modelo = db.Column(db.String(100), nullable=True)
    categoria = db.Column(db.String(50), nullable=False)  # Sopro, Cordas, Teclas, Percussão
    status = db.Column(db.String(30), default='Disponível', nullable=False)  # Disponível, Emprestado, Manutenção
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    emprestimos = db.relationship('Emprestimo', backref='instrumento', lazy=True)

class Emprestimo(db.Model):
    __tablename__ = 'emprestimos'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    instrumento_id = db.Column(db.Integer, db.ForeignKey('instrumentos.id'), nullable=False)
    data_emprestimo = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_devolucao_prevista = db.Column(db.Date, nullable=False)
    data_devolucao_real = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default='No prazo', nullable=False)  # No prazo, Em atraso, Devolvido
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Evento(db.Model):
    __tablename__ = 'eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(10), nullable=False)
    local = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    responsavel = db.Column(db.String(100), nullable=False, default='Coordenação')
    status = db.Column(db.String(30), default='Agendado', nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)