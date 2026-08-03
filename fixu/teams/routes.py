from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from . import bp
from .forms import TeamForm
from ..extensions import db
from ..models import Team, TeamMember, User


def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'


def is_admin_or_agent():
    return current_user.is_authenticated and current_user.role in ('admin', 'agent')


@bp.route('/')
@login_required
def index():
    # El solicitante no administra equipos (igual que categorías/agentes);
    # antes solo exigía login, así que cualquier solicitante podía ver el
    # listado completo de equipos y sus agentes.
    if not is_admin():
        flash('No autorizado. Solo administradores pueden acceder a esta sección.', 'danger')
        return redirect(url_for('tickets.index'))

    query = Team.query.order_by(Team.created_at.desc())
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=10)
    agents = User.query.filter_by(role='agent').all()
    return render_template('teams/index.html', pagination=pagination, teams=pagination.items, agents=agents)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role != 'admin':
        flash('Solo admin puede crear equipos.', 'danger')
        return redirect(url_for('teams.index'))

    form = TeamForm()
    if form.validate_on_submit():
        team = Team(name=form.name.data.strip())
        db.session.add(team)
        db.session.commit()
        flash('Equipo creado.', 'success')
        return redirect(url_for('teams.index'))
    return render_template('teams/form.html', form=form, mode='create')


@bp.route('/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(team_id):
    if current_user.role != 'admin':
        flash('Solo admin puede editar equipos.', 'danger')
        return redirect(url_for('teams.index'))

    team = Team.query.get_or_404(team_id)
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        team.name = form.name.data.strip()
        db.session.commit()
        flash('Equipo actualizado.', 'success')
        return redirect(url_for('teams.index'))
    return render_template('teams/form.html', form=form, mode='edit', team=team)


@bp.route('/<int:team_id>/members/add', methods=['POST'])
@login_required
def add_member(team_id):
    if current_user.role != 'admin':
        flash('Solo admin puede asignar miembros.', 'danger')
        return redirect(url_for('teams.index'))

    team = Team.query.get_or_404(team_id)
    user_id = request.form.get('user_id', type=int)
    if not user_id:
        flash('Usuario inválido', 'danger')
        return redirect(url_for('teams.index'))

    user = User.query.get_or_404(user_id)
    if user.role != 'agent':
        flash('Solo usuarios con rol agente pueden ser miembros.', 'danger')
        return redirect(url_for('teams.index'))

    existing = TeamMember.query.filter_by(team_id=team.id, user_id=user.id).first()
    if existing:
        flash('El usuario ya es miembro del equipo.', 'warning')
        return redirect(url_for('teams.index'))

    db.session.add(TeamMember(user_id=user.id, team_id=team.id))
    db.session.commit()
    flash('Miembro agregado.', 'success')
    return redirect(url_for('teams.index'))


@bp.route('/<int:team_id>/members/<int:member_id>/remove', methods=['POST'])
@login_required
def remove_member(team_id, member_id):
    if current_user.role != 'admin':
        flash('Solo admin puede remover miembros.', 'danger')
        return redirect(url_for('teams.index'))

    member = TeamMember.query.filter_by(id=member_id, team_id=team_id).first_or_404()
    db.session.delete(member)
    db.session.commit()
    flash('Miembro removido.', 'success')
    return redirect(url_for('teams.index'))


@bp.route('/<int:team_id>/members/api', methods=['GET'])
@login_required
def get_team_members_api(team_id):
    """API endpoint to get team members as JSON for dynamic dropdown filtering.

    Solo admin/agente: es usado para el selector de asignación de tickets,
    que el solicitante no usa; sin este chequeo, cualquier solicitante podía
    enumerar team_id y obtener nombres/emails de todos los agentes."""
    from flask import jsonify

    if not is_admin_or_agent():
        return jsonify({'error': 'No autorizado'}), 403

    team = Team.query.get_or_404(team_id)
    members = TeamMember.query.filter_by(team_id=team_id).all()
    
    members_data = [
        {
            'id': m.id,
            'user_id': m.user.id,
            'name': m.user.name,
            'team_name': team.name
        }
        for m in members
    ]
    
    return jsonify(members_data)


@bp.route('/<int:team_id>/delete', methods=['POST'])
@login_required
def delete(team_id):
    if current_user.role != 'admin':
        flash('Solo admin puede eliminar equipos.', 'danger')
        return redirect(url_for('teams.index'))

    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    flash('Equipo eliminado.', 'warning')
    return redirect(url_for('teams.index'))
