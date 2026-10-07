import os
from datetime import datetime, date
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

# Importações dos ficheiros locais
from models import db, Aluno, Instrumento, Emprestimo, Evento, Usuario
from forms import LoginForm, AlunoForm, InstrumentoForm, EmprestimoForm, EventoForm

# 1. Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# 2. Configurações da Aplicação (Fallback para SQLite caso PostgreSQL não esteja configurado)
db_uri = os.getenv('DATABASE_URL', 'sqlite:///filarmonica.db')
if db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'filarmonica-secret-key-123456')

# 3. Inicialização das Extensões
db.init_app(app)
csrf = CSRFProtect(app)

# ==========================================
# DECORADORES E AUXILIARES
# ==========================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor, faça login para aceder a esta página.', 'warning')
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
    total_emprestimos = Emprestimo.query.filter_by(status='Em andamento').count()
    return render_template('dashboard.html', 
                           total_alunos=total_alunos, 
                           total_instrumentos=total_instrumentos, 
                           total_emprestimos=total_emprestimos)

@app.route('/alunos/novo', methods=['GET', 'POST'])
@login_required
def novo_aluno():
    form = AlunoForm()
    if form.validate_on_submit():
        novo_aluno = Aluno(
            nome=form.nome.data,
            celular=form.celular.data,
            data_nascimento=form.data_nascimento.data,
            rua=form.rua.data,
            numero=form.numero.data,
            bairro=form.bairro.data
        )
        db.session.add(novo_aluno)
        db.session.commit()
        flash('Aluno cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_alunos'))
    return render_template('aluno_form.html', form=form)

@app.route('/alunos')
@login_required
def listar_alunos():
    alunos = Aluno.query.all()
    return render_template('alunos_list.html', alunos=alunos)

@app.route('/instrumentos/novo', methods=['GET', 'POST'])
@login_required
def novo_instrumento():
    form = InstrumentoForm()
    if form.validate_on_submit():
        novo_inst = Instrumento(
            nome=form.nome.data,
            tipo=form.tipo.data,
            numero_serie=form.numero_serie.data,
            status=form.status.data
        )
        db.session.add(novo_inst)
        db.session.commit()
        flash('Instrumento cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_instrumentos'))

    disponiveis = Instrumento.query.filter_by(status='Disponível').count()
    emprestados = Instrumento.query.filter_by(status='Emprestado').count()
    manutencao = Instrumento.query.filter_by(status='Manutenção').count()
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

@app.route('/instrumentos')
@login_required
def listar_instrumentos():
    instrumentos = Instrumento.query.all()
    return render_template('instrumentos_list.html', instrumentos=instrumentos)

@app.route('/emprestimos/novo', methods=['GET', 'POST'])
@login_required
def novo_emprestimo():
    form = EmprestimoForm()
    
    if hasattr(form, 'aluno_id'):
        form.aluno_id.choices = [(a.id, a.nome) for a in Aluno.query.order_by('nome').all()]
    if hasattr(form, 'instrumento_id'):
        form.instrumento_id.choices = [(i.id, f"{i.nome} ({i.numero_serie or 'S/N'})") for i in Instrumento.query.filter_by(status='Disponível').all()]

    if form.validate_on_submit():
        emprestimo = Emprestimo(
            aluno_id=form.aluno_id.data,
            instrumento_id=form.instrumento_id.data,
            data_emprestimo=form.data_emprestimo.data,
            data_devolucao_prevista=form.data_devolucao_prevista.data,
            status='Em andamento'
        )
        instrumento = Instrumento.query.get(form.instrumento_id.data)
        if instrumento:
            instrumento.status = 'Emprestado'

        db.session.add(emprestimo)
        db.session.commit()
        flash('Empréstimo registrado com sucesso!', 'success')
        return redirect(url_for('listar_emprestimos'))

    return render_template('emprestimo_form.html', form=form)

@app.route('/emprestimos')
@login_required
def listar_emprestimos():
    emprestimos = Emprestimo.query.all()
    return render_template('emprestimos_list.html', emprestimos=emprestimos)

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
        db.create_all()
        
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