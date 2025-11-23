from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Length
from email_validator import validate_email, EmailNotValidError
import re


class SpecialEmail:
    def __init__(self, message=None):
        self.message = message or 'Correo inválido'

    def __call__(self, form, field):
        if not field.data:
            raise ValidationError(self.message)

        email_str = field.data.strip().lower()

        # Permitir dominios .local explícitamente para desarrollo
        if email_str.endswith('.local'):
            if '@' not in email_str or email_str.count('@') != 1:
                raise ValidationError(self.message)
            local_part, domain = email_str.split('@')
            if not local_part or not domain:
                raise ValidationError(self.message)
            field.data = email_str
            return

        # Para otros dominios, usar validación estándar
        try:
            info = validate_email(
                email_str,
                check_deliverability=False
            )
            field.data = info.normalized
        except EmailNotValidError:
            raise ValidationError(self.message)


class PhoneValidator:
    def __init__(self, message=None):
        self.message = message or 'Número de teléfono inválido. Debe contener entre 10 y 20 dígitos.'

    def __call__(self, form, field):
        if not field.data:
            return  # Optional field
        
        phone_str = field.data.strip()
        # Remove common separators
        digits_only = re.sub(r'[\s\-\(\)\+]', '', phone_str)
        
        # Check if it contains only digits (and possibly a leading +)
        if not re.match(r'^\+?\d+$', digits_only):
            raise ValidationError(self.message)
        
        # Remove leading + for length check
        digits_only = digits_only.lstrip('+')
        
        # Check length
        if len(digits_only) < 10 or len(digits_only) > 20:
            raise ValidationError(self.message)


class LoginForm(FlaskForm):
    email = StringField('Correo', validators=[DataRequired(message='Correo requerido'), SpecialEmail()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar sesión')


class RegisterForm(FlaskForm):
    name = StringField('Nombre completo', validators=[
        DataRequired(message='Nombre requerido'), 
        Length(min=2, max=120, message='El nombre debe tener entre 2 y 120 caracteres')
    ])
    email = StringField('Correo', validators=[
        DataRequired(message='Correo requerido'), 
        SpecialEmail(),
        Length(max=255, message='El correo no puede exceder 255 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='Contraseña requerida'),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    submit = SubmitField('Crear cuenta')
