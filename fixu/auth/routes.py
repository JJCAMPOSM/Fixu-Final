from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from . import bp
from .forms import LoginForm, RegisterForm
from ..extensions import db
from ..models import User, Requester


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            from flask import current_app
            return redirect(current_app.config.get('LARAVEL_ADMIN_URL', 'http://localhost:8000') + '/admin')
        return redirect(url_for('tickets.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            # Admin → redirigir a Laravel Admin Panel
            if user.role == 'admin':
                from flask import current_app
                return redirect(current_app.config.get('LARAVEL_ADMIN_URL', 'http://localhost:8000') + '/admin')
            # Asegurar perfil de solicitante si aplica
            if user.role == 'requester':
                req = Requester.query.filter_by(email=user.email).first()
                if not req:
                    req = Requester(name=user.name or 'Solicitante', email=user.email, phone='')
                    db.session.add(req)
                    db.session.commit()
            flash('Bienvenido a Fixu', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('tickets.index'))
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
