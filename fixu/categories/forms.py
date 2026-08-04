from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class CategoryForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Guardar')
