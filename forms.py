from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField, DateField, DateTimeLocalField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError
from datetime import date


def _validar_data_nascimento(form, field):
    """Exige data de nascimento válida; não pode ser futura."""
    date_value = field.data
    if not date_value:
        return
    if date_value > date.today():
        raise ValidationError('A data de nascimento não pode ser futura.')

def _validar_data_evento(form, field):
    """Exige que a data do evento seja a partir de hoje (sem datas passadas)."""
    date_value = field.data
    if not date_value:
        return
    if date_value < date.today():
        raise ValidationError('A data do evento não pode ser anterior a hoje.')


class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrar = BooleanField('Lembrar de mim')


class AlunoForm(FlaskForm):
    nome = StringField('Nome completo do Aluno', validators=[DataRequired()])
    celular = StringField('Telemóvel/WhatsApp', validators=[
        Regexp(r'^\(\d{2}\) \d{4,5}-\d{4}$',
               message='Use o formato (00) 00000-0000 com apenas números.')
    ])
    data_nascimento = DateField('Data de Nascimento', format='%Y-%m-%d',
                                validators=[DataRequired(), _validar_data_nascimento])
    rua = StringField('Rua')
    numero = StringField('Número', validators=[
        Regexp(r'^\d{0,3}$', message='Apenas números, no máximo 3 dígitos.')
    ])
    bairro = StringField('Bairro')
    submit = SubmitField(' Salvar aluno')


class InstrumentoForm(FlaskForm):
    nome = StringField('Nome do Instrumento', validators=[DataRequired()])
    tombamento = StringField('Código do Instrumento')
    identificacao = StringField('Identificação do instrumento')
    modelo = StringField('Modelo')
    categoria = SelectField('Categoria', choices=[
        ('Sopro', 'Sopro'),
        ('Corda', 'Corda'),
        ('Percussão', 'Percussão'),
        ('Eletrofones', 'Eletrofones'),
        ('Teclas', 'Teclas')
    ], validators=[DataRequired()])
    numero_serie = StringField('Número de Série')
    status = SelectField('Status', choices=[
        ('Disponível', 'Disponível'),
        ('Emprestado', 'Emprestado'),
        ('Manutenção', 'Manutenção')
    ], default='Disponível')
    submit = SubmitField(' Salvar instrumento')


class EmprestimoForm(FlaskForm):
    aluno_id = SelectField('Aluno', coerce=int, validators=[DataRequired()])
    instrumento_id = SelectField('Instrumento', coerce=int, validators=[DataRequired()])
    submit = SubmitField(' Salvar empréstimo')


class EventoForm(FlaskForm):
    titulo = StringField('Nome do Evento', validators=[DataRequired(), Length(max=150)])
    data = DateField('Data', validators=[DataRequired(), _validar_data_evento], format='%Y-%m-%d')
    horario = TimeField('Horário', format='%H:%M', validators=[DataRequired()])
    local = StringField('Local', validators=[DataRequired(), Length(max=150)])
    responsavel = StringField('Responsável', default='Coordenação',
                              validators=[DataRequired(), Length(max=150)])
    memoria = TextAreaField('Descrição', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Agendado', 'Agendado'),
        ('Concluído', 'Concluído'),
        ('Cancelado', 'Cancelado')
    ], default='Agendado')
    submit = SubmitField(' Salvar evento')