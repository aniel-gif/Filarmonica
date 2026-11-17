import os
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

# Importações dos ficheiros locais
from models import db, Aluno, Instrumento, Emprestimo, Evento, Usuario
from forms import LoginForm, AlunoForm, InstrumentoForm, EmprestimoForm, EventoForm

load_dotenv()

app = Flask(__name__)

# Configurações da Aplicação
db_uri = os.getenv('DATABASE_URL', 'sqlite:///filarmonica.db')
if db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'filarmonica-secret-key-123456')

db.init_app(app)
csrf = CSRFProtect(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor, faça login para aceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_alunos = Aluno.query.count()
    total_instrumentos = Instrumento.query.count()
    instrumentos_disponiveis = Instrumento.query.filter_by(status='Disponível').count()
    emprestimos_ativos = Emprestimo.query.filter_by(status='Em andamento').count()
    proximos_eventos = Evento.query.count()

    emprestimos_recentes = Emprestimo.query.order_by(Emprestimo.data_emprestimo.desc()).limit(5).all()
    eventos_agendados = Evento.query.order_by(Evento.data.asc()).limit(5).all()

    return render_template('dashboard.html',
                           total_alunos=total_alunos,
                           total_instrumentos=total_instrumentos,
                           instrumentos_disponiveis=instrumentos_disponiveis,
                           emprestimos_ativos=emprestimos_ativos,
                           proximos_eventos=proximos_eventos,
                           emprestimos_recentes=emprestimos_recentes,
                           eventos_agendados=eventos_agendados)

@app.route('/alunos/novo', methods=['GET', 'POST'])
@login_required
def novo_aluno():
    form = AlunoForm()
    if form.validate_on_submit():
        aluno = Aluno(
            nome=form.nome.data,
            celular=form.celular.data,
            data_nascimento=form.data_nascimento.data,
            rua=form.rua.data,
            numero=form.numero.data,
            bairro=form.bairro.data
        )
        db.session.add(aluno)
        db.session.commit()
        flash('Aluno cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_alunos'))
    return render_template('aluno_form.html', form=form)

@app.route('/alunos')
@login_required
def listar_alunos():
    alunos = Aluno.query.all()
    return render_template('alunos_list.html', alunos=alunos)

@app.route('/alunos/deletar/<int:id>', methods=['POST'])
@login_required
def aluno_deletar(id):
    aluno = Aluno.query.get_or_404(id)
    db.session.delete(aluno)
    db.session.commit()
    flash('Aluno excluído com sucesso!', 'success')
    return redirect(url_for('listar_alunos'))

@app.route('/instrumentos/novo', methods=['GET', 'POST'])
@login_required
def novo_instrumento():
    form = InstrumentoForm()
    if form.validate_on_submit():
        inst = Instrumento(
            nome=form.nome.data,
            codigo=form.tombamento.data,
            identificacao=form.identificacao.data,
            modelo=form.modelo.data,
            categoria=form.categoria.data,
            status=form.status.data
        )
        db.session.add(inst)
        db.session.commit()
        flash('Instrumento cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_instrumentos'))

    resumo = {
        'disponiveis': Instrumento.query.filter_by(status='Disponível').count(),
        'emprestados': Instrumento.query.filter_by(status='Emprestado').count(),
        'manutencao': Instrumento.query.filter_by(status='Manutenção').count(),
        'total': Instrumento.query.count(),
        'agora': datetime.now()
    }
    return render_template('instrumento_form.html', form=form, **resumo)

@app.route('/instrumentos')
@login_required
def listar_instrumentos():
    instrumentos = Instrumento.query.all()
    return render_template('instrumentos_list.html', instrumentos=instrumentos)

@app.route('/instrumentos/deletar/<int:id>', methods=['POST'])
@login_required
def instrumento_deletar(id):
    instrumento = Instrumento.query.get_or_404(id)
    db.session.delete(instrumento)
    db.session.commit()
    flash('Instrumento excluído com sucesso!', 'success')
    return redirect(url_for('listar_instrumentos'))

@app.route('/emprestimos/novo', methods=['GET', 'POST'])
@login_required
def novo_emprestimo():
    form = EmprestimoForm()
    form.aluno_id.choices = [(a.id, a.nome) for a in Aluno.query.order_by('nome').all()]
    form.instrumento_id.choices = [(i.id, f"{i.nome} ({i.codigo or 'S/N'})")
                                    for i in Instrumento.query.filter_by(status='Disponível').all()]

    if form.validate_on_submit():
        agora = datetime.now()
        data_devolucao = (agora + timedelta(days=15)).date()

        emp = Emprestimo(
            aluno_id=form.aluno_id.data,
            instrumento_id=form.instrumento_id.data,
            data_emprestimo=agora,
            data_devolucao_prevista=data_devolucao,
            status='Em andamento'
        )
        inst = Instrumento.query.get(form.instrumento_id.data)
        if inst:
            inst.status = 'Emprestado'

        db.session.add(emp)
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
        from datetime import datetime as dt
        h = dt.strptime(form.horario.data, '%H:%M').time() if form.horario.data else None

        evt = Evento(
            nome=form.titulo.data,
            data=form.data.data,
            local=form.local.data,
            horario=h,
            descricao=form.memoria.data,
            responsavel=form.responsavel.data,
            status=form.status.data
        )
        db.session.add(evt)
        db.session.commit()
        flash('Evento cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_eventos'))
    return render_template('evento_form.html', form=form)

@app.route('/eventos')
@login_required
def listar_eventos():
    eventos = Evento.query.all()
    return render_template('eventos_list.html', eventos=eventos)

@app.route('/emprestimos/deletar/<int:id>', methods=['POST'])
@login_required
def emprestimo_deletar(id):
    emprestimo = Emprestimo.query.get_or_404(id)
    inst = Instrumento.query.get(emprestimo.instrumento_id)
    if inst:
        inst.status = 'Disponível'
    db.session.delete(emprestimo)
    db.session.commit()
    flash('Empréstimo excluído com sucesso!', 'success')
    return redirect(url_for('listar_emprestimos'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(email='admin@filarmonica.org').first():
            admin = Usuario(
                nome='Administrador',
                email='admin@filarmonica.org',
                senha_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("-> Usuário padrão criado: admin@filarmonica.org / admin123")

    app.run(debug=True)