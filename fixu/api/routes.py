from flask import jsonify, request, current_app
from datetime import datetime
from functools import wraps
from flask_login import login_required, current_user
import os
import hmac
import hashlib

from . import bp
from .. import db
from ..models import TeamMember, SatisfactionTicket, Ticket, User, Team, Requester, Category
from ..services.bridge_client import get_bridge_client


def require_api_key(f):
    """Decorador para proteger endpoints de API interna con API Key y firma HMAC."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        hmac_sig = request.headers.get('X-HMAC-Signature')
        if hmac_sig:
            secret = os.getenv('HMAC_SECRET_KEY', 'internal-hmac-secret-key')
            expected = hmac.new(secret.encode('utf-8'), request.get_data(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(hmac_sig, expected):
                return jsonify({'error': 'Invalid HMAC signature'}), 401
        else:
            api_key = request.headers.get('X-API-Key')
            expected_key = os.getenv('INTERNAL_API_KEY', 'internal-bridge-secret-key')
            if api_key != expected_key:
                return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


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


# ============ Endpoints de Sincronización desde Bridge API ============

@bp.post('/sync/user')
@require_api_key
def sync_user():
    """Recibe sincronización de usuario desde Bridge API."""
    data = request.get_json()
    action = data.get('action')
    user_data = data.get('data', {})
    
    try:
        if action == 'create':
            user = User(
                name=user_data.get('name'),
                email=user_data.get('email'),
                role=user_data.get('role', 'requester'),
                avatar=user_data.get('avatar')
            )
            if user_data.get('password'):
                user.set_password(user_data['password'])
            db.session.add(user)
            db.session.commit()
            return jsonify({'success': True, 'id': user.id}), 201
            
        elif action == 'update':
            user = User.query.get(user_data.get('id'))
            if not user:
                return jsonify({'error': 'User not found'}), 404
            user.name = user_data.get('name', user.name)
            user.email = user_data.get('email', user.email)
            user.role = user_data.get('role', user.role)
            db.session.commit()
            return jsonify({'success': True, 'id': user.id})
            
        elif action == 'delete':
            user = User.query.get(user_data.get('id'))
            if user:
                db.session.delete(user)
                db.session.commit()
            return jsonify({'success': True})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Unknown action'}), 400


@bp.post('/sync/ticket')
@require_api_key
def sync_ticket():
    """Recibe sincronización de ticket desde Bridge API."""
    data = request.get_json()
    action = data.get('action')
    ticket_data = data.get('data', {})
    
    try:
        if action == 'create':
            ticket = Ticket(
                title=ticket_data.get('title'),
                body=ticket_data.get('body'),
                requester_id=ticket_data.get('requester_id'),
                team_id=ticket_data.get('team_id'),
                assignee_team_member_id=ticket_data.get('assignee_team_member_id'),
                category_id=ticket_data.get('category_id'),
                status=ticket_data.get('status', 'open'),
                priority=ticket_data.get('priority', 'medium')
            )
            db.session.add(ticket)
            db.session.commit()
            return jsonify({'success': True, 'id': ticket.id}), 201
            
        elif action == 'update':
            ticket = Ticket.query.get(ticket_data.get('id'))
            if not ticket:
                return jsonify({'error': 'Ticket not found'}), 404
            ticket.title = ticket_data.get('title', ticket.title)
            ticket.body = ticket_data.get('body', ticket.body)
            ticket.status = ticket_data.get('status', ticket.status)
            ticket.priority = ticket_data.get('priority', ticket.priority)
            db.session.commit()
            return jsonify({'success': True, 'id': ticket.id})
            
        elif action == 'delete':
            ticket = Ticket.query.get(ticket_data.get('id'))
            if ticket:
                db.session.delete(ticket)
                db.session.commit()
            return jsonify({'success': True})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Unknown action'}), 400


@bp.post('/sync/team')
@require_api_key
def sync_team():
    """Recibe sincronización de equipo desde Bridge API."""
    data = request.get_json()
    action = data.get('action')
    team_data = data.get('data', {})
    
    try:
        if action == 'create':
            team = Team(name=team_data.get('name'))
            db.session.add(team)
            db.session.commit()
            return jsonify({'success': True, 'id': team.id}), 201
            
        elif action == 'update':
            team = Team.query.get(team_data.get('id'))
            if not team:
                return jsonify({'error': 'Team not found'}), 404
            team.name = team_data.get('name', team.name)
            db.session.commit()
            return jsonify({'success': True, 'id': team.id})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Unknown action'}), 400


@bp.post('/sync/requester')
@require_api_key
def sync_requester():
    """Recibe sincronización de solicitante desde Bridge API."""
    data = request.get_json()
    action = data.get('action')
    requester_data = data.get('data', {})
    
    try:
        if action == 'create':
            requester = Requester(
                name=requester_data.get('name'),
                email=requester_data.get('email'),
                phone=requester_data.get('phone')
            )
            db.session.add(requester)
            db.session.commit()
            return jsonify({'success': True, 'id': requester.id}), 201
            
        elif action == 'update':
            requester = Requester.query.get(requester_data.get('id'))
            if not requester:
                return jsonify({'error': 'Requester not found'}), 404
            requester.name = requester_data.get('name', requester.name)
            requester.email = requester_data.get('email', requester.email)
            requester.phone = requester_data.get('phone', requester.phone)
            db.session.commit()
            return jsonify({'success': True, 'id': requester.id})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Unknown action'}), 400


@bp.post('/sync/category')
@require_api_key
def sync_category():
    """Recibe sincronización de categoría desde Bridge API."""
    data = request.get_json()
    action = data.get('action')
    category_data = data.get('data', {})
    
    try:
        if action == 'create':
            category = Category(
                name=category_data.get('name'),
                description=category_data.get('description'),
                color=category_data.get('color', '#6366f1')
            )
            db.session.add(category)
            db.session.commit()
            return jsonify({'success': True, 'id': category.id}), 201
            
        elif action == 'update':
            category = Category.query.get(category_data.get('id'))
            if not category:
                return jsonify({'error': 'Category not found'}), 404
            category.name = category_data.get('name', category.name)
            category.description = category_data.get('description', category.description)
            category.color = category_data.get('color', category.color)
            db.session.commit()
            return jsonify({'success': True, 'id': category.id})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Unknown action'}), 400


# ============ Health Check ============

@bp.get('/health')
def api_health():
    """Health check para el Bridge API."""
    return jsonify({'status': 'ok', 'service': 'flask-api'})


# ============ Endpoints de Webhooks ============

@bp.post('/webhooks/user-created')
@require_api_key
def webhook_user_created():
    """Webhook para creación de usuario desde Laravel."""
    data = request.get_json()
    # Lógica para procesar webhook
    return jsonify({'success': True, 'message': 'Webhook procesado'})


@bp.post('/webhooks/ticket-created')
@require_api_key
def webhook_ticket_created():
    """Webhook para creación de ticket desde Laravel."""
    data = request.get_json()
    # Lógica para procesar webhook
    return jsonify({'success': True, 'message': 'Webhook procesado'})


@bp.get('/tickets/check-updates')
def check_updates():
    """Retorna el ID del último ticket creado para polling"""
    last_ticket = Ticket.query.order_by(Ticket.id.desc()).first()
    return jsonify({'last_ticket_id': last_ticket.id if last_ticket else 0})

