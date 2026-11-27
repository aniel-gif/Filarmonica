import os
import secrets
import time
from datetime import datetime, timedelta, date
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

# Importações dos ficheiros locais
from models import db, Aluno, Instrumento, Emprestimo, Evento, Usuario
from forms import LoginForm, AlunoForm, InstrumentoForm, EmprestimoForm, EventoForm, AlunoRegistroForm, RecuperarSenhaForm, NovaSenhaForm

load_dotenv()

app = Flask(__name__)

# Configurações da Aplicação
db_uri = os.getenv('DATABASE_URL', 'sqlite:///filarmonica.db')
if db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql+psycopg2://', 1)
elif db_uri.startswith('postgresql://'):
    db_uri = db_uri.replace('postgresql://', 'postgresql+psycopg2://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise RuntimeError("SECRET_KEY environment variable must be set")

db.init_app(app)
csrf = CSRFProtect(app)

# Inicialização do Banco de Dados para Produção
with app.app_context():
    db.create_all()

    # Migração automática de colunas para tabelas já existentes
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    if inspector.has_table('usuarios'):
        colunas_usuarios = [c['name'] for c in inspector.get_columns('usuarios')]
        if 'role' not in colunas_usuarios:
            db.session.execute(text("ALTER TABLE usuarios ADD COLUMN role VARCHAR(20) DEFAULT 'usuario' NOT NULL"))
            db.session.commit()
            print("-> Coluna 'role' adicionada à tabela 'usuarios'.")

    if inspector.has_table('alunos'):
        colunas_alunos = [c['name'] for c in inspector.get_columns('alunos')]
        if 'usuario_id' not in colunas_alunos:
            db.session.execute(text("ALTER TABLE alunos ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)"))
            db.session.commit()
            print("-> Coluna 'usuario_id' adicionada à tabela 'alunos'.")

    admin_user = Usuario.query.filter_by(email='admin@filarmonica.org').first()
    if not admin_user:
        senha_admin = os.getenv('ADMIN_DEFAULT_PASSWORD')
        if not senha_admin:
            raise RuntimeError("ADMIN_DEFAULT_PASSWORD environment variable must be set")
        admin = Usuario(
            nome='Administrador',
            email='admin@filarmonica.org',
            senha_hash=generate_password_hash(senha_admin),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("-> Usuário padrão verificado/criado. Senha pré-definida registrada.")
    elif admin_user.role != 'admin':
        admin_user.role = 'admin'
        db.session.commit()
        print("-> Permissão de administrador atualizada para o usuário padrão.")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor, faça login para aceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Por favor, faça login para aceder a esta página.', 'warning')
            return redirect(url_for('login'))
        user = Usuario.query.get(session['usuario_id'])
        if not user or user.role != 'admin':
            flash('Acesso restrito aos administradores.', 'danger')
            # Evita loop de redirecionamento: envia o aluno para o seu painel
            if 'aluno_id' in session:
                return redirect(url_for('aluno_dashboard'))
            session.clear()
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'usuario_id' in session:
        if 'aluno_id' in session:
            return redirect(url_for('aluno_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/cadastro-aluno', methods=['GET', 'POST'])
def cadastro_aluno():
    form = AlunoRegistroForm()
    if form.validate_on_submit():
        # Verifica se o e-mail já está em uso
        existing_user =Usuario.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Este e-mail já está cadastro. Por favor, faça login.', 'danger')
            return redirect(url_for('login'))

        # Cria o Usuário
        user =Usuario(
            nome=form.nome.data,
            email=form.email.data,
            senha_hash=generate_password_hash(form.senha.data)
        )
        db.session.add(user)
        db.session.commit()

        # Cria o perfil de Aluno vinculado ao Usuário
        aluno = Aluno(
            nome=form.nome.data,
            celular=form.celular.data,
            data_nascimento=form.data_nascimento.data,
            rua=form.rua.data,
            numero=form.numero.data,
            bairro=form.bairro.data,
            usuario_id=user.id
        )
        db.session.add(aluno)
        db.session.commit()

        flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro_aluno.html', form=form, today=date.today().isoformat())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.senha_hash, form.senha.data):
            session['usuario_id'] = user.id
            session['usuario_nome'] = user.nome
            session['usuario_role'] = user.role

            # Verifica se é um aluno vinculado
            aluno_perfil = Aluno.query.filter_by(usuario_id=user.id).first()
            if aluno_perfil:
                session['aluno_id'] = aluno_perfil.id
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('aluno_dashboard'))

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

# ==================== RECUPERAÇÃO DE SENHA ====================

# Configuração de rate limiting em memória (simples, sem dependências externas)
# Para produção com múltiplos workers, usar Redis ou banco de dados
MAX_TOKENS_PER_USER = 1  # Máximo 1 ativo por usuário
MAX_TOKENS_GLOBAL = 100  # Limite global para prevenir DoS
recently_used_tokens = set()  # Para evitar reutilização de tokens

# Token de recuperação de senha (em memória - substituir por banco em produção)
# Estrutura: {token: {'user_id': int, 'expiry': float}}
recovery_tokens = {}
TOKEN_EXPIRY_SECONDS = 900  # 15 minutos

@app.route('/esqueci-minha-senha', methods=['GET', 'POST'])
def esqueci_minha_senha():
    form = RecuperarSenhaForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()

        # Sempre mostra mensagem de sucesso para prevenir enumeração de e-mails
        if user:
            # Limpa tokens expirados antigos
            cleanup_tokens()

            # Proteção contra DoS: limite global de tokens
            if len(recovery_tokens) >= MAX_TOKENS_GLOBAL:
                flash('Muitos pedidos de recuperação. Tente novamente mais tarde.', 'warning')
                return render_template('esqueci_senha.html', form=form)

            # Remove tokens antigos do usuário anterior (mantém só 1 ativo)
            old_token = None
            for t, data in list(recovery_tokens.items()):
                if data['user_id'] == user.id:
                    old_token = t
                    break
            if old_token:
                del recovery_tokens[old_token]

            # Gera um token único para recuperação com expiração
            token = secrets.token_urlsafe(32)
            recovery_tokens[token] = {
                'user_id': user.id,
                'expiry': time.time() + TOKEN_EXPIRY_SECONDS
            }
            # Em produção, enviar email real
            # Armazena o token na sessão do usuário (não exposto na URL nem em flash)
            session['recovery_email'] = form.email.data
            session['recovery_token'] = token
            flash('Um código de recuperação foi gerado. Verifique o e-mail cadastrado e cole o código na tela seguinte.', 'info')
            return redirect(url_for('recuperar_senha'))

        flash('Se o e-mail existir na base de dados, um código foi enviado.', 'info')
    return render_template('esqueci_senha.html', form=form)


@app.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    # Uso atômico: get() e remoção em uma operação
    token = session.get('recovery_token')
    if token:
        token_data = recovery_tokens.pop(token, None)
        # Limpa o token da sessão após uso
        session.pop('recovery_token', None)
    else:
        flash('Token inválido ou expirado.', 'danger')
        return redirect(url_for('esqueci_minha_senha'))

    if token_data is None:
        flash('Token inválido ou expirado.', 'danger')
        return redirect(url_for('esqueci_minha_senha'))

    # Verifica se o token expirou após a remoção atômica
    if time.time() > token_data['expiry']:
        flash('Token expirado. Solicite uma nova recuperação de senha.', 'warning')
        return redirect(url_for('esqueci_minha_senha'))

    form = NovaSenhaForm()
    if form.validate_on_submit():
        user_id = token_data['user_id']
        user = Usuario.query.get(user_id)
        if user:
            user.senha_hash = generate_password_hash(form.senha.data)
            db.session.commit()
            flash('Senha alterada com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
    return render_template('nova_senha.html', form=form)


# Limpa tokens expirados periodicamente
@app.before_request
def cleanup_tokens():
    # Limpa tokens expirados (mais de 15 minutos)
    current_time = time.time()
    expired_tokens = [token for token, data in recovery_tokens.items()
                      if current_time > data['expiry']]
    for token in expired_tokens:
        del recovery_tokens[token]


@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_alunos = Aluno.query.count()
    total_instrumentos = Instrumento.query.count()
    instrumentos_disponiveis = Instrumento.query.filter_by(status='Disponível').count()
    emprestimos_ativos = Emprestimo.query.filter_by(status='Em andamento').count()
    proximos_eventos = Evento.query.count()

    emprestimos_recentes = Emprestimo.query.order_by(Emprestimo.data_emprestimo.desc()).limit(5).all()
    eventos_agendados = Evento.query.order_by(Evento.data.asc()).limit(5).all()
    instrumentos_detalhados = Instrumento.query.order_by(Instrumento.nome).all()

    return render_template('dashboard.html',
                           total_alunos=total_alunos,
                           total_instrumentos=total_instrumentos,
                           instrumentos_disponiveis=instrumentos_disponiveis,
                           emprestimos_ativos=emprestimos_ativos,
                           proximos_eventos=proximos_eventos,
                           emprestimos_recentes=emprestimos_recentes,
                           eventos_agendados=eventos_agendados,
                           instrumentos_detalhados=instrumentos_detalhados)

@app.route('/alunos/novo', methods=['GET', 'POST'])
@login_required
@admin_required
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

    # Calcula a data mínima (120 anos atrás)
    today = date.today()
    min_date = date(today.year - 120, today.month, today.day).isoformat()
    return render_template('aluno_form.html', form=form, today=today.isoformat(), min_date=min_date)

@app.route('/alunos')
@login_required
@admin_required
def listar_alunos():
    alunos = Aluno.query.all()
    return render_template('alunos_list.html', alunos=alunos)

@app.route('/alunos/deletar/<int:id>', methods=['POST'])
@login_required
@admin_required
def aluno_deletar(id):
    aluno = Aluno.query.get_or_404(id)
    db.session.delete(aluno)
    db.session.commit()
    flash('Aluno excluído com sucesso!', 'success')
    return redirect(url_for('listar_alunos'))

@app.route('/instrumentos/novo', methods=['GET', 'POST'])
@login_required
@admin_required
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
    user_role = session.get('usuario_role')
    if user_role == 'admin':
        instrumentos = Instrumento.query.all()
    else:
        # Alunos comuns veem apenas instrumentos disponíveis
        instrumentos = Instrumento.query.filter_by(status='Disponível').all()
    return render_template('instrumentos_list.html', instrumentos=instrumentos, is_admin=(user_role == 'admin'))

@app.route('/instrumentos/deletar/<int:id>', methods=['POST'])
@login_required
@admin_required
def instrumento_deletar(id):
    instrumento = Instrumento.query.get_or_404(id)
    db.session.delete(instrumento)
    db.session.commit()
    flash('Instrumento excluído com sucesso!', 'success')
    return redirect(url_for('listar_instrumentos'))

@app.route('/emprestimos/novo', methods=['GET', 'POST'])
@login_required
@admin_required
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
    user_role = session.get('usuario_role')
    # Verify aluno_id from database to prevent session tampering
    aluno_perfil = Aluno.query.filter_by(usuario_id=session.get('usuario_id')).first()
    aluno_id = aluno_perfil.id if aluno_perfil else None

    if user_role == 'admin':
        emprestimos = Emprestimo.query.all()
    else:
        # Alunos comuns veem apenas os próprios empréstimos
        emprestimos = Emprestimo.query.filter_by(aluno_id=aluno_id).all()
    return render_template('emprestimos_list.html', emprestimos=emprestimos, is_admin=(user_role == 'admin'))

@app.route('/eventos/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_evento():
    form = EventoForm()
    if form.validate_on_submit():
        from datetime import datetime as dt
        # O campo agora é um time object vindo do navegador
        h = form.horario.data
        if isinstance(h, str):
             h = dt.strptime(h, '%H:%M').time()

        evt = Evento(
            nome=form.titulo.data,
            data=form.data.data,
            local=form.local.data,
            horario=h,
            descricao=form.memoria.data,
            responsavel=form.responsavel.data,
            status=form.status.data,
            usuario_id=session['usuario_id']
        )
        db.session.add(evt)
        db.session.commit()
        flash('Evento cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_eventos'))
    return render_template('evento_form.html', form=form, min_date=date.today().isoformat())

@app.route('/eventos')
@login_required
@admin_required
def listar_eventos():
    eventos = Evento.query.filter_by(usuario_id=session['usuario_id']).all()
    return render_template('eventos_list.html', eventos=eventos)

@app.route('/aluno/dashboard')
def aluno_dashboard():
    if 'aluno_id' not in session:
        flash('Acesso restrito a alunos.', 'danger')
        return redirect(url_for('login'))

    aluno = Aluno.query.get_or_404(session['aluno_id'])
    emprestimos = Emprestimo.query.filter_by(aluno_id=aluno.id).all()
    hoje = datetime.now().date()
    # Alunos comuns veem apenas eventos próximos (futuro), com detalhes
    eventos = Evento.query.filter(Evento.data >= hoje).order_by(Evento.data.asc()).all()
    # Alunos comuns veem apenas instrumentos disponíveis para empréstimo
    instrumentos_disponiveis = Instrumento.query.filter_by(status='Disponível').all()

    return render_template('aluno_dashboard.html', aluno=aluno, emprestimos=emprestimos, eventos=eventos, instrumentos_disponiveis=instrumentos_disponiveis, now=hoje)

@app.route('/emprestimos/deletar/<int:id>', methods=['POST'])
@login_required
@admin_required
def emprestimo_deletar(id):
    emprestimo = Emprestimo.query.get_or_404(id)
    inst = Instrumento.query.get(emprestimo.instrumento_id)
    if inst:
        inst.status = 'Disponível'
    db.session.delete(emprestimo)
    db.session.commit()
    flash('Empréstimo excluído com sucesso!', 'success')
    return redirect(url_for('listar_emprestimos'))


@app.route('/emprestimos/cancelar/<int:id>', methods=['POST'])
@login_required
def emprestimo_cancelar(id):
    emprestimo = Emprestimo.query.get_or_404(id)
    user_role = session.get('usuario_role')
    # Verify aluno_id from database to prevent session tampering
    aluno_perfil = Aluno.query.filter_by(usuario_id=session.get('usuario_id')).first()
    aluno_id = aluno_perfil.id if aluno_perfil else None

    # Apenas admin ou o próprio dono do empréstimo podem cancelar
    if user_role != 'admin' and emprestimo.aluno_id != aluno_id:
        flash('Você não tem permissão para cancelar este empréstimo.', 'danger')
        return redirect(url_for('listar_emprestimos'))

    # Apenas cancela se estiver em andamento
    if emprestimo.status == 'Em andamento':
        inst = Instrumento.query.get(emprestimo.instrumento_id)
        if inst:
            inst.status = 'Disponível'
        emprestimo.status = 'Cancelado'
        db.session.commit()
        flash('Empréstimo cancelado com sucesso!', 'success')
    else:
        flash('Este empréstimo não pode ser cancelado (já concluído ou em outro status).', 'warning')
    return redirect(url_for('listar_emprestimos'))

if __name__ == '__main__':
    app.run(debug=True)