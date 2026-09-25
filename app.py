import os
from wtforms.validators import DataRequired, Optional, Regexp, ValidationError
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TextAreaField, BooleanField
os.environ['PGCLIENTENCODING'] = 'utf-8'
os.environ['PGTZ'] = 'UTC'
from datetime import datetime, date
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TextAreaField, BooleanField
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, AlunoForm,InstrumentoForm, EmprestimoForm, EventoForm
from models import db, Aluno, Instrumento, Emprestimo, Evento, Usuario

# 1. Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# 2. Configurações da Aplicação
db_uri = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/filarmonica_db')
if db_uri and 'client_encoding' not in db_uri:
    db_uri += '?client_encoding=utf8' if '?' not in db_uri else '&client_encoding=utf8'

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'filarmonica-secret-key-123456')

# 3. Inicialização das Extensões
db.init_app(app)
csrf = CSRFProtect(app)

# 4. Criação automática das tabelas no PostgreSQL
with app.app_context():
    db.create_all()


# ==========================================
# MODELOS (BANCO DE DADOS)
# ==========================================

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    instrumento_estudo = db.Column(db.String(50))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

class Instrumento(db.Model):
    __tablename__ = 'instrumentos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Sopro, Percussão, Cordas
    numero_serie = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='Disponível')  # Disponível, Emprestado, Manutenção



class Evento(db.Model):
    __tablename__ = 'eventos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    data_evento = db.Column(db.DateTime, nullable=False)
    local = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)

# ==========================================
# FORMULÁRIOS (WTFORMS)
# ==========================================

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrar = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')

def validar_idade_minima(form, field):
    if field.data:
        hoje = date.today()
        # Calcula a idade exata considerando mês e dia
        idade = hoje.year - field.data.year - ((hoje.month, hoje.day) < (field.data.month, field.data.day))
        if idade < 15:
            raise ValidationError("O aluno deve ter no mínimo 15 anos de idade.")

def get_data_maxima_15_anos():
    hoje = date.today()
    try:
        return hoje.replace(year=hoje.year - 15).isoformat()
    except ValueError: # Trata ano bissexto (29 de fevereiro)
        return hoje.replace(year=hoje.year - 15, day=28).isoformat()


class AlunoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(message="O nome é obrigatório")])
    cpf = StringField('CPF')
    email = StringField('E-mail')
    celular = StringField(
        'Celular',
        validators=[
            DataRequired(message="O celular é obrigatório."),
            Regexp(r'^\(d{2}\)\d{8,9}$', message="O celular deve estar no formato (84)9XXXXXXX.")
        ],
        render_kw={
            "maxlength": "13",
            "oninput": r"this.value = this.value.replace(/\D/g, '').replace(/^(\d{2})(\d)/, '($1)$2').substring(0, 13)",
            "placeholder": "Ex: (00)999998888"
        }
        )
    data_nascimento = DateField(
        'Data de Nascimento', 
        validators=[
            DataRequired(message="A data de nascimento é obrigatória."),
            validar_idade_minima
            ],
        render_kw={
            "max": get_data_maxima_15_anos(),
            "min": "1900-01-01"
        }
        )
    rua = StringField('Rua')
    numero = StringField(
        'Número',
        validators=[
            Optional(),
            Regexp(r'^\d+$',message="Digite apenas números")
        ],
        render_kw={
            "type": "number",
            "min": "0",
            "oninput": "this.value = this.value.replace(/[^0-9]/g, '')",
            "placeholder": "Ex: 123"
        }
    )
    bairro = StringField('Bairro')
    submit = SubmitField('Salvar')


# ==========================================
# DECORADORES E AUXILIARES
# ==========================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# ROTAS DA APLICAÇÃO
# ==========================================

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.senha_hash, form.senha.data):
            session['usuario_id'] = user.id
            session['usuario_nome'] = user.nome
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        flash('E-mail ou senha incorretos.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_alunos = Aluno.query.count()
    total_instrumentos = Instrumento.query.count()
    total_emprestimos = Emprestimo.query.filter_by(status='Ativo').count()
    return render_template('dashboard.html', 
                           total_alunos=total_alunos, 
                           total_instrumentos=total_instrumentos, 
                           total_emprestimos=total_emprestimos)

@app.route('/alunos')
@login_required
def listar_alunos():
    alunos = Aluno.query.all()
    return render_template('alunos.html', alunos=alunos)

@app.route('/alunos/novo', methods=['GET', 'POST'])
@login_required
def novo_aluno():
    form = AlunoForm()
    if form.validate_on_submit():
        aluno = Aluno(
            nome=form.nome.data,
            cpf=form.cpf.data,
            telefone=form.telefone.data,
            instrumento_estudo=form.instrumento_estudo.data
        )
        db.session.add(aluno)
        db.session.commit()
        flash('Aluno cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_alunos'))
    return render_template('aluno_form.html', form=form)

@app.route('/instrumentos')
@login_required
def listar_instrumentos():
    instrumentos = Instrumento.query.all()
    return render_template('instrumentos.html', instrumentos=instrumentos)

@app.route('/instrumentos/novo', methods=['GET', 'POST'])
@login_required
def novo_instrumento():
    form = InstrumentoForm()
    if form.validate_on_submit():
        instrumento = Instrumento(
            nome=form.nome.data,
            tipo=form.tipo.data,
            numero_serie=form.numero_serie.data,
            status=form.status.data
        )
        db.session.add(instrumento)
        db.session.commit()
        flash('Instrumento cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_instrumentos'))
    disponiveis = Instrumento.query.filter_by(status='Disponível').count() if hasattr(Instrumento, 'status') else 0
    emprestados = Instrumento.query.filter_by(status='Emprestado').count() if hasattr(Instrumento, 'status') else 0
    manutencao = Instrumento.query.filter_by(status='Manutenção').count() if hasattr(Instrumento, 'status') else 0
    total = Instrumento.query.count()
    return render_template(
        'instrumento_form.html',
        form=form,
        disponiveis=disponiveis,
        emprestados=emprestados,
        manutencao=manutencao,
        total=total,
        agora=datetime.now()
    )

@app.route('/emprestimos')
@login_required
def listar_emprestimos():
    return render_template('emprestimos_list.html')

@app.route('/emprestimos/novo', methods=['GET', 'POST'])
@login_required
def novo_emprestimo():
    form = EmprestimoForm()
    if form.validate_on_submit():
        pass
    return render_template('emprestimo_form.html', form=form)

@app.route('/eventos/novo', methods=['GET', 'POST'])
@login_required
def novo_evento():
    form = EventoForm()
    if form.validate_on_submit():
        pass
    return render_template('evento_form.html', form=form)

# ==========================================
# INICIALIZAÇÃO AUTOMÁTICA
# ==========================================

if __name__ == '__main__':
    with app.app_context():
        # Cria todas as tabelas caso não existam
        db.create_all()
        
        # Cria o usuário admin padrão caso não exista
        if not Usuario.query.filter_by(email='admin@filarmonica.org').first():
            admin_padrao = Usuario(
                nome='Administrador',
                email='admin@filarmonica.org',
                senha_hash=generate_password_hash('admin123')
            )
            db.session.add(admin_padrao)
            db.session.commit()
            print("-> Usuário padrão criado: admin@filarmonica.org / admin123")
            
    app.run(debug=True)