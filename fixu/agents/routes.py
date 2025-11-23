from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from . import bp
from .forms import AgentForm
from ..extensions import db
from ..models import User


def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'


@bp.route('/')
@login_required
def index():
    if not is_admin():
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    query = User.query.filter_by(role='agent').order_by(User.name)
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=15, error_out=False)

    return render_template('agents/index.html', pagination=pagination, agents=pagination.items)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not is_admin():
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    form = AgentForm()
    if form.validate_on_submit():
        # Validar contraseña requerida en creación
        if not form.password.data:
            flash('La contraseña es requerida al crear un agente.', 'danger')
            return render_template('agents/form.html', form=form, mode='create')

        # Verificar si el email ya existe
        existing_user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if existing_user:
            flash('Este email ya está registrado.', 'danger')
            return render_template('agents/form.html', form=form, mode='create')

        agent = User(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            role='agent'  # Asignar automáticamente el rol de agente
        )
        agent.set_password(form.password.data)
        db.session.add(agent)
        db.session.commit()
        flash('Agente creado con éxito.', 'success')
        return redirect(url_for('agents.index'))

    return render_template('agents/form.html', form=form, mode='create')


@bp.route('/<int:agent_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(agent_id):
    if not is_admin():
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    agent = User.query.get_or_404(agent_id)

    # Verificar que sea un agente
    if agent.role != 'agent':
        flash('Este usuario no es un agente.', 'danger')
        return redirect(url_for('agents.index'))

    form = AgentForm(obj=agent)

    if form.validate_on_submit():
        # Verificar si el email ya existe (excepto el actual)
        existing_user = User.query.filter(
            User.email == form.email.data.strip().lower(),
            User.id != agent_id
        ).first()
        if existing_user:
            flash('Este email ya está registrado.', 'danger')
            return render_template('agents/form.html', form=form, mode='edit', agent=agent)

        agent.name = form.name.data.strip()
        agent.email = form.email.data.strip().lower()

        # Solo actualizar contraseña si se proporcionó una nueva
        if form.password.data:
            agent.set_password(form.password.data)

        db.session.commit()
        flash('Agente actualizado con éxito.', 'success')
        return redirect(url_for('agents.index'))

    return render_template('agents/form.html', form=form, mode='edit', agent=agent)


@bp.route('/<int:agent_id>/delete', methods=['POST'])
@login_required
def delete(agent_id):
    if not is_admin():
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    agent = User.query.get_or_404(agent_id)

    # Verificar que sea un agente
    if agent.role != 'agent':
        flash('Este usuario no es un agente.', 'danger')
        return redirect(url_for('agents.index'))

    # No permitir eliminar si hay membresías activas en equipos
    if agent.team_members:
        flash(f'No se puede eliminar. El agente está asignado a {len(agent.team_members)} equipo(s).', 'danger')
        return redirect(url_for('agents.index'))

    db.session.delete(agent)
    db.session.commit()
    flash('Agente eliminado.', 'warning')
    return redirect(url_for('agents.index'))
