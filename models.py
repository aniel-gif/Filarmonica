from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabela Aluno[cite: 1]
class Aluno(db.Model):
    __tablename__ = 'aluno'
    
    id_aluno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_completo = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date)
    
    # Relacionamento com Empréstimos[cite: 1]
    emprestimos = db.relationship('Emprestimo', backref='aluno', lazy=True)

# Tabela Instrumento[cite: 1]
class Instrumento(db.Model):
    __tablename__ = 'instrumento'
    
    id_instrumento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    numero_serie = db.Column(db.String(100))
    estado = db.Column(db.String(50))
    situacao = db.Column(db.String(50))
    
    # Relacionamento com Empréstimos[cite: 1]
    emprestimos = db.relationship('Emprestimo', backref='instrumento', lazy=True)

# Tabela Empréstimo[cite: 1]
class Emprestimo(db.Model):
    __tablename__ = 'emprestimo'
    
    id_emprestimo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('aluno.id_aluno'), nullable=False)
    id_instrumento = db.Column(db.Integer, db.ForeignKey('instrumento.id_instrumento'), nullable=False)
    data_hora_emprestimo = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_devolucao = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(30))

# Tabela Evento[cite: 1]
class Evento(db.Model):
    __tablename__ = 'evento'
    
    id_evento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    data = db.Column(db.Date, nullable=False)
    local = db.Column(db.String(150))
    horario = db.Column(db.Time)
    descricao = db.Column(db.Text)

# Tabela Usuário[cite: 1]
class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)