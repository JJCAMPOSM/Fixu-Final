from functools import wraps
from flask import jsonify
from flask_login import current_user

def login_required(f):
    """
    Decorador para proteger rutas que requieren autenticación.
    Si el usuario no está autenticado, devuelve un error 401.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Se requiere autenticación'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorador para proteger rutas que requieren privilegios de administrador.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Se requiere autenticación'}), 401
        if current_user.role != 'admin':
            return jsonify({'error': 'No tiene permisos suficientes'}), 403
        return f(*args, **kwargs)
    return decorated_function
