from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField, DateField, DateTimeLocalField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrar = BooleanField('Lembrar de mim')

class AlunoForm(FlaskForm):
    nome = StringField('Nome completo do aluno', validators=[DataRequired(), Length(max=150)])
    endereco = StringField('Endereço', validators=[DataRequired(), Length(max=255)])
    celular = StringField('Número de celular', validators=[DataRequired(), Length(max=20)])
    data_nascimento = DateField('Data de nascimento', validators=[DataRequired()], format='%Y-%m-%d')
    numero = StringField('Número', validators=[
        DataRequired(message="O campo número é obrigatório."),
        Length(max=3, message="O número deve ter no máximo 3 dígitos."),
        Regexp(r'^\d{1,3}$', message="Digite apenas números (máximo 3 digitos).")
    ])

class InstrumentoForm(FlaskForm):
    nome = StringField('Nome do instrumento', validators=[DataRequired(), Length(max=100)])
    tombamento = StringField('Código do instrumento', validators=[DataRequired(), Length(max=50)])
    identificacao = StringField('Identificação do instrumento', validators=[Length(max=100)])
    modelo = StringField('Modelo', validators=[Length(max=100)])
    categoria = SelectField('Categoria', choices=[
        ('', 'Selecione a categoria'),
        ('Sopro', 'Sopro'),
        ('Cordas', 'Cordas'),
        ('Teclas', 'Teclas'),
        ('Percussão', 'Percussão')
    ], validators=[DataRequired()])
    submit = SubmitField('Salvar')

class EmprestimoForm(FlaskForm):
    aluno_id = SelectField('Nome completo do aluno', coerce=int, validators=[DataRequired()])
    instrumento_id = SelectField('Instrumento emprestado', coerce=int, validators=[DataRequired()])
    data_emprestimo = DateTimeLocalField('Data e hora do empréstimo', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    data_devolucao_prevista = DateField('Data de devolução do instrumento', format='%Y-%m-%d', validators=[DataRequired()])

class EventoForm(FlaskForm):
    titulo = StringField('Evento ou atividade', validators=[DataRequired(), Length(max=150)])
    data = DateField('Data', validators=[DataRequired()], format='%Y-%m-%d')
    horario = StringField('Horário', validators=[DataRequired(), Length(max=10)])
    local = StringField('Local', validators=[DataRequired(), Length(max=150)])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    responsavel = StringField('Responsável', default='Coordenação', validators=[DataRequired()])