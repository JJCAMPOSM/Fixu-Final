"""Cifrado simétrico (Fernet/AES-128-CBC + HMAC) para datos sensibles en reposo.

Complementa el hasheo de contraseñas (bcrypt, en models.py): el hasheo es
unidireccional (para verificar credenciales sin poder recuperarlas), mientras
que aquí necesitamos poder recuperar el valor original (ej. mostrar el
teléfono del solicitante en el panel), así que se usa cifrado reversible.
"""
from cryptography.fernet import Fernet, InvalidToken
from flask import current_app
from sqlalchemy.types import TypeDecorator, Text


def _fernet() -> Fernet:
    return Fernet(current_app.config['ENCRYPTION_KEY'])


class EncryptedString(TypeDecorator):
    """Columna de texto cifrada con Fernet de forma transparente para el ORM.

    El valor en Python siempre es el texto plano; en la base de datos se
    guarda el token cifrado (base64). Requiere ENCRYPTION_KEY configurada.
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None or value == '':
            return value
        return _fernet().encrypt(value.encode('utf-8')).decode('utf-8')

    def process_result_value(self, value, dialect):
        if value is None or value == '':
            return value
        try:
            return _fernet().decrypt(value.encode('utf-8')).decode('utf-8')
        except InvalidToken:
            # Dato preexistente guardado antes de activar el cifrado, o
            # cifrado con una clave distinta: no truena la petición, pero
            # deja claro que no se pudo leer en vez de mostrar basura.
            return None
