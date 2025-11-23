from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class TicketForm(FlaskForm):
    title = StringField('Título', validators=[
        DataRequired(message='El título es requerido'), 
        Length(min=3, max=200, message='El título debe tener entre 3 y 200 caracteres')
    ])
    body = TextAreaField('Descripción', validators=[
        DataRequired(message='La descripción es requerida'), 
        Length(min=10, message='La descripción debe tener al menos 10 caracteres')
    ])
    requester_id = SelectField('Solicitante', coerce=int, validators=[Optional()])
    category_id = SelectField('Categoría', coerce=int, validators=[Optional()])
    team_id = SelectField('Equipo', coerce=int, validators=[Optional()])
    assignee_team_member_id = SelectField('Asignado a', coerce=int, validators=[Optional()])
    status = SelectField('Estado', choices=[('open','Abierto'), ('pending','Pendiente'), ('solved','Resuelto'), ('closed','Cerrado')], validators=[Optional()])
    priority = SelectField('Prioridad', choices=[('low','Baja'), ('medium','Media'), ('high','Alta')], validators=[Optional()])
    submit = SubmitField('Guardar')


class CommentForm(FlaskForm):
    body = TextAreaField('Comentario', validators=[
        DataRequired(message='El comentario no puede estar vacío'), 
        Length(min=1, message='El comentario debe tener al menos 1 carácter')
    ])
    private = BooleanField('Privado (visible solo a agentes y admins)')
    submit = SubmitField('Agregar comentario')
