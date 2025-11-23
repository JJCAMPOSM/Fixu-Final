from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from ..auth.forms import SpecialEmail, PhoneValidator


class RequesterForm(FlaskForm):
    name = StringField('Nombre', validators=[
        DataRequired(message='Nombre requerido'), 
        Length(min=2, max=120, message='El nombre debe tener entre 2 y 120 caracteres')
    ])
    email = StringField('Correo', validators=[
        DataRequired(message='Correo requerido'), 
        SpecialEmail(),
        Length(max=255, message='El correo no puede exceder 255 caracteres')
    ])
    phone = StringField('Teléfono', validators=[
        Optional(), 
        PhoneValidator()
    ])
    submit = SubmitField('Guardar')
