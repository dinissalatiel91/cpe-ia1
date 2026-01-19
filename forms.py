"""
forms.py
--------
Formulários WTForms:
- Login
- Registo
- Chat (pergunta)
- Mudança de password
- Admin (criar/editar QA)
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length


class RegisterForm(FlaskForm):
    full_name = StringField("Nome completo", validators=[DataRequired(), Length(min=3, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=160)])
    password = PasswordField("Palavra-passe", validators=[DataRequired(), Length(min=6, max=72)])
    submit = SubmitField("Criar conta")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=160)])
    password = PasswordField("Palavra-passe", validators=[DataRequired(), Length(min=6, max=72)])
    remember = BooleanField("Manter sessão iniciada")
    submit = SubmitField("Entrar")


class ChatForm(FlaskForm):
    question = StringField("Escreve a tua pergunta", validators=[DataRequired(), Length(min=2, max=300)])
    submit = SubmitField("Perguntar")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Palavra-passe actual", validators=[DataRequired(), Length(min=6, max=72)])
    new_password = PasswordField("Nova palavra-passe", validators=[DataRequired(), Length(min=6, max=72)])
    submit = SubmitField("Actualizar palavra-passe")


class QAForm(FlaskForm):
    qa_id = HiddenField()  # usado para edição (opcional)
    question = TextAreaField("Pergunta", validators=[DataRequired(), Length(min=3)])
    answer = TextAreaField("Resposta", validators=[DataRequired(), Length(min=3)])
    submit = SubmitField("Guardar")
