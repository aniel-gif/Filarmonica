from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField, DateField, DateTimeLocalField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrar = BooleanField('Lembrar de mim')

class AlunoForm(FlaskForm):
    nome = StringField('Nome completo do Aluno', validators=[DataRequired()])
    celular = StringField('Telemóvel/WhatsApp')
    data_nascimento = DateField('Data de Nascimento', format='%Y-%m-%d', validators=[DataRequired()])
    rua = StringField('Rua')
    numero = StringField('Número')
    bairro = StringField('Bairro')
    submit = SubmitField('Salvar aluno')

class InstrumentoForm(FlaskForm):
    nome = StringField('Nome do Instrumento', validators=[DataRequired()])
    tipo = StringField('Tipo / Categoria')
    numero_serie = StringField('Número de Série')
    status = SelectField('Status', choices=[
        ('Disponível', 'Disponível'),
        ('Emprestado', 'Emprestado'),
        ('Manutenção', 'Manutenção')
    ], default='Disponível')
    submit = SubmitField('Salvar instrumento')

class EmprestimoForm(FlaskForm):
    aluno_id = SelectField('Aluno', coerce=int, validators=[DataRequired()])
    instrumento_id = SelectField('Instrumento', coerce=int, validators=[DataRequired()])
    data_emprestimo = DateField('Data do Empréstimo', format='%Y-%m-%d', validators=[DataRequired()])
    data_devolucao_prevista = DateField('Data de Devolução', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Salvar empréstimo')
    
class EventoForm(FlaskForm):
    titulo = StringField('Evento ou atividade', validators=[DataRequired(), Length(max=150)])
    data = DateField('Data', validators=[DataRequired()], format='%Y-%m-%d')
    horario = StringField('Horário', validators=[DataRequired(), Length(max=10)])
    local = StringField('Local', validators=[DataRequired(), Length(max=150)])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    responsavel = StringField('Responsável', default='Coordenação', validators=[DataRequired()])