import base64
import hashlib
import hmac
import json
import secrets
import time

import bcrypt
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user

from . import bp
from .forms import LoginForm, RegisterForm
from ..extensions import db
from ..models import User, Requester
from ..rate_limiter import (
    rate_limit, is_account_locked, register_failed_login,
    clear_failed_login, DUMMY_PASSWORD_HASH,
)


def _admin_handoff_token(user):
    """Token firmado (HMAC compartido) de corta duración para que Laravel
    verifique que Flask ya autenticó a un admin antes de dejarlo entrar
    a /admin. Sin esto, cualquiera podía entrar a /admin sin loguearse.

    Incluye un nonce aleatorio: Laravel lo marca como consumido en su cache
    al validar el token, así una URL con ?admin_token=... capturada en logs
    no sirve para un segundo acceso una vez usada (protección contra replay
    dentro de la ventana de 60s de validez del token)."""
    secret = current_app.config['HMAC_SECRET_KEY']
    nonce = secrets.token_urlsafe(16)
    payload = json.dumps({
        'role': user.role,
        'email': user.email,
        'exp': int(time.time()) + 60,
        'nonce': nonce,
    }).encode()
    payload_b64 = base64.urlsafe_b64encode(payload).decode().rstrip('=')
    signature = hmac.new(secret.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f'{payload_b64}.{signature}'


@bp.route('/login', methods=['GET', 'POST'])
@rate_limit(limit=6, window=60)
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(f'/admin?admin_token={_admin_handoff_token(current_user)}')
        return redirect(url_for('tickets.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        if is_account_locked(email):
            flash('Demasiados intentos fallidos. Intenta de nuevo en unos minutos.', 'danger')
            return render_template('auth/login.html', form=form)

        user = User.query.filter_by(email=email).first()
        if user:
            password_ok = user.check_password(form.password.data)
        else:
            # Ejecutar un bcrypt.checkpw "señuelo" para que la respuesta tarde
            # lo mismo que cuando el email sí existe y la contraseña es
            # incorrecta (evita filtrar por timing si un email está registrado).
            bcrypt.checkpw(form.password.data.encode('utf-8'), DUMMY_PASSWORD_HASH)
            password_ok = False

        if user and password_ok:
            clear_failed_login(email)
            login_user(user, remember=form.remember.data)
            # Admin → redirigir a Laravel Admin Panel (ruta relativa, nginx la enruta a Laravel)
            if user.role == 'admin':
                return redirect(f'/admin?admin_token={_admin_handoff_token(user)}')
            # Asegurar perfil de solicitante si aplica
            if user.role == 'requester':
                req = Requester.query.filter_by(email=user.email).first()
                if not req:
                    req = Requester(name=user.name or 'Solicitante', email=user.email, phone='')
                    db.session.add(req)
                    db.session.commit()
            flash('Bienvenido a Fixu', 'success')
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/') or next_page.startswith('//'):
                next_page = url_for('tickets.index')
            return redirect(next_page)
        register_failed_login(email)
        flash('Credenciales inválidas', 'danger')
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tickets.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('El correo ya está registrado. Inicia sesión o usa otro correo.', 'danger')
            return render_template('auth/register.html', form=form)

        # Crear usuario con rol 'requester'
        user = User(
            name=form.name.data.strip(),
            email=email,
            role='requester'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        # Crear perfil de solicitante
        requester = Requester(
            name=user.name,
            email=user.email,
            phone=''
        )
        db.session.add(requester)
        db.session.commit()

        flash('Cuenta creada exitosamente. Inicia sesión para continuar.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)
