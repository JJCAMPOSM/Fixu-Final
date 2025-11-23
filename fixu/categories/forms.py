from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Optional


class CategoryForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    color = StringField('Color', validators=[
        Optional(),
        Length(min=7, max=7),
        Regexp(r'^#[0-9A-Fa-f]{6}$', message='Debe ser un color hexadecimal válido (ej: #6366f1)')
    ])
    submit = SubmitField('Guardar')
