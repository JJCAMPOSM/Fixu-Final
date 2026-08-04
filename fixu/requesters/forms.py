from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, EqualTo
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
        DataRequired(message='Teléfono requerido'),
        PhoneValidator()
    ])
    password = PasswordField('Contraseña', validators=[
        Optional(),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    password_confirm = PasswordField('Confirmar contraseña', validators=[
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Guardar')
