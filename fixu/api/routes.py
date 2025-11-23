from flask import jsonify, request
from datetime import datetime
from flask_login import login_required, current_user

from . import bp
from .. import db
from ..models import TeamMember, SatisfactionTicket, Ticket


@bp.get('/teams/<int:team_id>/members')
def team_members(team_id: int):
    members = TeamMember.query.filter_by(team_id=team_id).all()
    data = [
        {
            'id': m.id,
            'user_id': m.user_id,
            'name': m.user.name,
            'email': m.user.email,
        }
        for m in members
    ]
    return jsonify(data)


@bp.get('/tickets/<int:ticket_id>/has-feedback')
@login_required
def has_feedback(ticket_id: int):
    """Verifica si un ticket ya tiene feedback"""
    feedback = SatisfactionTicket.query.filter_by(ticket_id=ticket_id).first()
    return jsonify({'has_feedback': feedback is not None})


@bp.post('/tickets/<int:ticket_id>/feedback')
@login_required
def submit_feedback(ticket_id: int):
    """Envía feedback para un ticket"""
    
    # Verificar si el ticket existe y está cerrado
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.status != 'closed':
        return jsonify({'error': 'Solo se puede enviar feedback para tickets cerrados'}), 400
    
    # Verificar si ya existe feedback para este ticket
    existing_feedback = SatisfactionTicket.query.filter_by(ticket_id=ticket_id).first()
    if existing_feedback:
        return jsonify({'error': 'Ya se ha enviado feedback para este ticket'}), 400
    
    # Validar datos del formulario
    data = request.get_json()
    if not data or 'calificacion' not in data:
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    calificacion = data.get('calificacion')
    comentario = data.get('comentario', '')
    
    # Validar rango de calificación
    if not isinstance(calificacion, int) or calificacion < 1 or calificacion > 5:
        return jsonify({'error': 'La calificación debe ser un número entre 1 y 5'}), 400
    
    # Crear y guardar el feedback
    feedback = SatisfactionTicket(
        ticket_id=ticket_id,
        user_id=current_user.id,
        calificacion=calificacion,
        comentario=comentario,
        fecha_envio=datetime.utcnow()
    )
    
    db.session.add(feedback)
    ticket.rating = calificacion
    db.session.commit()
    
    return jsonify({
        'message': 'Feedback enviado correctamente',
        'feedback_id': feedback.id
    }), 201
