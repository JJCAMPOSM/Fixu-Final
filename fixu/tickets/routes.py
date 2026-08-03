from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from . import bp
from .forms import TicketForm, CommentForm
from ..extensions import db
from ..models import Ticket, Requester, Team, TeamMember, Comment, TicketEvent, Category, SatisfactionTicket, User
from ..services.bridge_client import get_bridge_client
from ..ticket_catalog import (
    BUILDINGS, CLASSROOMS, EQUIPMENT_TYPES,
    STATUS_ADMIN_CHOICES, STATUS_AGENT_CHOICES, CANCELABLE_BY_REQUESTER,
)


def is_admin_or_agent():
    return current_user.is_authenticated and current_user.role in ('admin', 'agent')


def is_agent():
    return current_user.is_authenticated and current_user.role == 'agent'


def current_team_member():
    return TeamMember.query.filter_by(user_id=current_user.id).first()


def _mark_resolved_if_needed(ticket, new_status):
    if new_status == 'resolved' and ticket.status != 'resolved':
        ticket.resolved_at = datetime.utcnow()


@bp.route('/')
@login_required
def index():
    query = Ticket.query.options(
        joinedload(Ticket.requester),
        joinedload(Ticket.team),
        joinedload(Ticket.assignee).joinedload(TeamMember.user)
    ).order_by(Ticket.created_at.desc())

    status = request.args.get('status', type=str)
    priority = request.args.get('priority', type=str)
    team_id = request.args.get('team_id', type=int)
    assignee_id = request.args.get('assignee_id', type=int)

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if team_id:
        query = query.filter(Ticket.team_id == team_id)
    if assignee_id:
        query = query.filter(Ticket.assignee_team_member_id == assignee_id)

    if current_user.role == 'requester':
        requester = Requester.query.filter_by(email=current_user.email).first()
        if requester:
            query = query.filter(Ticket.requester_id == requester.id)
        else:
            query = query.filter(False)
    elif current_user.role == 'agent':
        # El agente solo ve los tickets que tiene asignados (mismo criterio
        # que la App Móvil), no todo el sistema.
        tm = current_team_member()
        if tm:
            query = query.filter(Ticket.assignee_team_member_id == tm.id)
        else:
            query = query.filter(False)

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=10, error_out=False)

    teams = Team.query.order_by(Team.name).all() if current_user.role == 'admin' else []

    return render_template('tickets/index.html', pagination=pagination, tickets=pagination.items, teams=teams)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Registrar una incidencia: solo el solicitante puede crear tickets."""
    if current_user.role != 'requester':
        flash('Solo un solicitante puede crear tickets.', 'danger')
        return redirect(url_for('tickets.index'))

    form = TicketForm()
    form.requester_id.choices = [(0, '')]
    form.category_id.choices = [(0, '')]
    form.team_id.choices = [(0, '')]
    form.assignee_team_member_id.choices = [(0, '')]
    form.status.choices = [('pending', 'Pendiente')]

    if form.validate_on_submit():
        req = Requester.query.filter_by(email=current_user.email).first()
        if not req:
            flash('Error: No se encontró perfil de solicitante.', 'danger')
            return redirect(url_for('tickets.index'))

        if form.building.data not in BUILDINGS:
            flash('Debe seleccionar un edificio.', 'danger')
            return render_template('tickets/form.html', form=form, mode='create')
        if form.classroom.data not in CLASSROOMS:
            flash('Debe seleccionar un aula.', 'danger')
            return render_template('tickets/form.html', form=form, mode='create')
        if form.equipment_type.data not in EQUIPMENT_TYPES:
            flash('Debe seleccionar un tipo de equipo.', 'danger')
            return render_template('tickets/form.html', form=form, mode='create')

        ticket = Ticket(
            title=form.title.data.strip(),
            body=form.body.data.strip(),
            requester_id=req.id,
            category_id=None,
            team_id=None,
            assignee_team_member_id=None,
            status='pending',
            priority=form.priority.data,
            building=form.building.data,
            classroom=form.classroom.data,
            equipment_type=form.equipment_type.data,
        )

        db.session.add(ticket)
        db.session.flush()
        db.session.add(TicketEvent(ticket_id=ticket.id, user_id=current_user.id, body='Ticket creado'))
        db.session.commit()

        # Sincronizar con Laravel a través del Bridge API
        try:
            bridge = get_bridge_client()
            ticket_data = {
                'id': ticket.id,
                'title': ticket.title,
                'body': ticket.body,
                'requester_id': ticket.requester_id,
                'team_id': ticket.team_id,
                'assignee_team_member_id': ticket.assignee_team_member_id,
                'category_id': ticket.category_id,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
            }
            result = bridge.sync_ticket('create', ticket_data, source='flask')
            if not result.get('success'):
                current_app.logger.warning(f"Sync ticket to bridge failed: {result}")
        except Exception as e:
            current_app.logger.error(f"Error syncing ticket to bridge: {e}")

        flash('Ticket creado con éxito.', 'success')
        return redirect(url_for('tickets.show', ticket_id=ticket.id))

    return render_template('tickets/form.html', form=form, mode='create')


@bp.route('/<int:ticket_id>')
@login_required
def show(ticket_id):
    ticket = Ticket.query.options(
        joinedload(Ticket.requester),
        joinedload(Ticket.team),
        joinedload(Ticket.assignee).joinedload(TeamMember.user),
        joinedload(Ticket.comments).joinedload(Comment.team_member).joinedload(TeamMember.user),
        joinedload(Ticket.events)
    ).get_or_404(ticket_id)

    if current_user.role == 'requester':
        req = Requester.query.filter_by(email=current_user.email).first()
        if not req or ticket.requester_id != req.id:
            flash('No autorizado.', 'danger')
            return redirect(url_for('tickets.index'))
    elif current_user.role == 'agent':
        tm = current_team_member()
        if not tm or ticket.assignee_team_member_id != tm.id:
            flash('No autorizado.', 'danger')
            return redirect(url_for('tickets.index'))

    comment_form = CommentForm()
    has_feedback = SatisfactionTicket.query.filter_by(ticket_id=ticket_id).first() is not None
    can_cancel = current_user.role == 'requester' and ticket.status in CANCELABLE_BY_REQUESTER
    return render_template(
        'tickets/show.html', ticket=ticket, comment_form=comment_form, has_feedback=has_feedback,
        can_cancel=can_cancel,
    )


@bp.route('/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not is_admin_or_agent():
            flash('Solo agentes o admins pueden comentar.', 'danger')
            return redirect(url_for('tickets.show', ticket_id=ticket.id))
        tm = TeamMember.query.filter_by(user_id=current_user.id).first()
        if not tm:
            flash('No estás asignado a un equipo.', 'danger')
            return redirect(url_for('tickets.show', ticket_id=ticket.id))
        if is_agent() and ticket.assignee_team_member_id != tm.id:
            flash('Solo podés comentar en tickets que tenés asignados.', 'danger')
            return redirect(url_for('tickets.show', ticket_id=ticket.id))
        comment = Comment(ticket_id=ticket.id, team_member_id=tm.id, private=bool(form.private.data), body=form.body.data.strip())
        db.session.add(comment)
        db.session.add(TicketEvent(ticket_id=ticket.id, user_id=current_user.id, body='Comentario agregado'))
        db.session.commit()
        flash('Comentario agregado.', 'success')
    else:
        flash('Error al agregar comentario.', 'danger')
    return redirect(url_for('tickets.show', ticket_id=ticket.id))


@bp.route('/<int:ticket_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if not is_admin_or_agent():
        flash('No autorizado.', 'danger')
        return redirect(url_for('tickets.show', ticket_id=ticket.id))

    tm = current_team_member() if is_agent() else None
    if is_agent() and (not tm or ticket.assignee_team_member_id != tm.id):
        flash('Solo podés editar tickets que tenés asignados.', 'danger')
        return redirect(url_for('tickets.show', ticket_id=ticket.id))

    form = TicketForm(obj=ticket)

    if is_agent():
        # El agente solo puede cambiar el estado (y agregar observaciones vía
        # comentarios): no reasigna, no cambia el equipo/solicitante ni elimina.
        form.status.choices = STATUS_AGENT_CHOICES
    else:
        form.status.choices = STATUS_ADMIN_CHOICES

        requesters = Requester.query.order_by(Requester.name).all()
        form.requester_id.choices = [(r.id, f"{r.name} <{r.email}>") for r in requesters]

        categories = Category.query.order_by(Category.name).all()
        form.category_id.choices = [(0, '— Ninguna —')] + [(c.id, c.name) for c in categories]

        teams = Team.query.order_by(Team.name).all()
        form.team_id.choices = [(0, '— Ninguno —')] + [(t.id, t.name) for t in teams]

        # Populate assignee dropdown
        if ticket.team_id:
            # If ticket has a team, show only members from that team
            members = TeamMember.query.filter_by(team_id=ticket.team_id).all()
        else:
            # If no team assigned, show ALL team members from ALL teams
            members = TeamMember.query.join(User).order_by(User.name).all()

        form.assignee_team_member_id.choices = [(0, '— Ninguno —')] + [
            (m.id, f"{m.user.name} ({m.team.name})") for m in members
        ]

        # Pre-validación: sincronizar opciones de assignee con el team_id seleccionado en el POST
        if request.method == 'POST' and form.team_id.data:
            team_id_from_form = form.team_id.data
            if team_id_from_form and team_id_from_form != 0:
                # Recargar los miembros del equipo seleccionado en el formulario
                members_from_selected_team = TeamMember.query.filter_by(team_id=team_id_from_form).all()
                form.assignee_team_member_id.choices = [(0, '— Ninguno —')] + [
                    (m.id, f"{m.user.name} ({m.team.name})") for m in members_from_selected_team
                ]
            else:
                # Si no hay equipo seleccionado, mostrar TODOS los miembros de TODOS los equipos
                all_members = TeamMember.query.join(User).order_by(User.name).all()
                form.assignee_team_member_id.choices = [(0, '— Ninguno —')] + [
                    (m.id, f"{m.user.name} ({m.team.name})") for m in all_members
                ]

    if form.validate_on_submit():
        if is_agent():
            # Un agente comprometido no puede tocar nada más que el estado.
            new_status = form.status.data
            _mark_resolved_if_needed(ticket, new_status)
            ticket.status = new_status
            db.session.add(TicketEvent(ticket_id=ticket.id, user_id=current_user.id, body='Ticket actualizado'))
            db.session.commit()
            flash('Ticket actualizado.', 'success')
            return redirect(url_for('tickets.show', ticket_id=ticket.id))

        # El admin solo asigna equipo/agente: no reasigna solicitante/categoría,
        # no edita el contenido del ticket (eso lo define el solicitante al
        # crearlo) ni el estado (eso lo maneja el agente una vez asignado).
        assignee_value = form.assignee_team_member_id.data or 0
        team_value = form.team_id.data or 0
        new_assignee = assignee_value if assignee_value != 0 else None

        # Al asignar un agente a un ticket que seguía "pendiente", el estado
        # avanza automáticamente a "asignado".
        if new_assignee is not None and ticket.status == 'pending':
            new_status = 'assigned'
        else:
            new_status = ticket.status

        _mark_resolved_if_needed(ticket, new_status)

        ticket.team_id = team_value if team_value != 0 else None
        ticket.assignee_team_member_id = new_assignee
        ticket.status = new_status
        db.session.add(TicketEvent(ticket_id=ticket.id, user_id=current_user.id, body='Ticket actualizado'))
        db.session.commit()
        flash('Ticket actualizado.', 'success')
        return redirect(url_for('tickets.show', ticket_id=ticket.id))

    return render_template('tickets/form.html', form=form, mode='edit', ticket=ticket)


@bp.route('/<int:ticket_id>/cancel', methods=['POST'])
@login_required
def cancel(ticket_id):
    """El solicitante cancela su propio ticket, solo si aún no ha sido atendido."""
    ticket = Ticket.query.get_or_404(ticket_id)

    if current_user.role != 'requester':
        flash('No autorizado.', 'danger')
        return redirect(url_for('tickets.show', ticket_id=ticket.id))

    req = Requester.query.filter_by(email=current_user.email).first()
    if not req or ticket.requester_id != req.id:
        flash('No autorizado.', 'danger')
        return redirect(url_for('tickets.index'))

    if ticket.status not in CANCELABLE_BY_REQUESTER:
        flash('Este ticket ya está siendo atendido y no se puede cancelar.', 'danger')
        return redirect(url_for('tickets.show', ticket_id=ticket.id))

    ticket.status = 'cancelled'
    db.session.add(TicketEvent(ticket_id=ticket.id, user_id=current_user.id, body='Ticket cancelado por el solicitante'))
    db.session.commit()
    flash('Ticket cancelado.', 'success')
    return redirect(url_for('tickets.show', ticket_id=ticket.id))


@bp.route('/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete(ticket_id):
    """Solo el administrador puede eliminar tickets."""
    ticket = Ticket.query.get_or_404(ticket_id)
    if current_user.role != 'admin':
        flash('No autorizado.', 'danger')
        return redirect(url_for('tickets.show', ticket_id=ticket.id))
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket eliminado.', 'warning')
    return redirect(url_for('tickets.index'))
