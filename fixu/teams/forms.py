from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class TeamForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=120)])
    submit = SubmitField('Guardar')
