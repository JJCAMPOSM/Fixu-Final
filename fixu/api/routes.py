from flask import jsonify, request, current_app, url_for
from datetime import datetime, timedelta
from functools import wraps
from flask_login import login_required, current_user
import os
import re
import hmac
import hashlib
import base64
import uuid
import jwt as pyjwt

from . import bp
from .. import db
from ..extensions import csrf
from ..models import TeamMember, SatisfactionTicket, Ticket, User, Team, Requester, Category, TicketEvent
from ..services.bridge_client import get_bridge_client
from ..rate_limiter import rate_limit, get_redis
import redis as _redis_module


def _public_photo_url(photo_path):
    """Construye una URL de foto alcanzable desde la App Móvil.

    No se usa url_for(..., _external=True): las peticiones móviles llegan a
    Flask vía bridge_api con Host interno (ej. flask_app_1:5000), así que la
    URL externa resultante apuntaría a un hostname de Docker no resoluble
    desde el teléfono. En su lugar se usa PUBLIC_BASE_URL (nginx público).
    """
    if not photo_path:
        return None
    static_path = url_for('static', filename=photo_path)
    return current_app.config['PUBLIC_BASE_URL'].rstrip('/') + static_path


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
@login_required
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


@bp.get('/metrics')
def api_metrics():
    """Métricas Prometheus (peticiones permitidas/bloqueadas por Rate Limiting)."""
    from flask import Response
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


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
@login_required
def check_updates():
    """Retorna el ID del último ticket creado para polling"""
    last_ticket = Ticket.query.order_by(Ticket.id.desc()).first()
    return jsonify({'last_ticket_id': last_ticket.id if last_ticket else 0})


# ============ App Móvil: Autenticación JWT ============

ALLOWED_PHOTO_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_PHOTO_BYTES = 6 * 1024 * 1024  # 6 MB


def _issue_jwt(user: User) -> str:
    payload = {
        'sub': user.id,
        'email': user.email,
        'role': user.role,
        'jti': uuid.uuid4().hex,
        'exp': datetime.utcnow() + timedelta(hours=current_app.config.get('JWT_EXP_HOURS', 12)),
        'iat': datetime.utcnow(),
    }
    return pyjwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')


def _blacklist_key(jti: str) -> str:
    return f'jwt_blacklist:{jti}'


def _blacklist_jwt(payload: dict) -> None:
    """Invalida un JWT antes de su expiración natural (usado en logout)."""
    jti = payload.get('jti')
    if not jti:
        return
    exp = payload.get('exp')
    ttl = max(int(exp - datetime.utcnow().timestamp()), 1) if exp else 3600
    try:
        get_redis().set(_blacklist_key(jti), '1', ex=ttl)
    except _redis_module.RedisError:
        current_app.logger.warning('Redis no disponible, no se pudo invalidar el JWT')


def jwt_required(f):
    """Protege endpoints de la App Móvil con JSON Web Token (Bearer)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Falta el token JWT (Authorization: Bearer <token>)'}), 401
        token = auth_header.split(' ', 1)[1]
        try:
            payload = pyjwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        except pyjwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401

        try:
            if payload.get('jti') and get_redis().exists(_blacklist_key(payload['jti'])):
                return jsonify({'error': 'Token inválido'}), 401
        except _redis_module.RedisError:
            current_app.logger.warning('Redis no disponible, se omitió el chequeo de blacklist de JWT')

        user = User.query.get(payload.get('sub'))
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 401
        request.jwt_user = user
        request.jwt_payload = payload
        return f(*args, **kwargs)
    return decorated


@bp.post('/mobile/login')
@csrf.exempt
@rate_limit(limit=6, window=60)
def mobile_login():
    """Login para la App Móvil (Herramienta de Campo). Devuelve un JWT."""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'email y password son requeridos'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Credenciales inválidas'}), 401

    if user.role != 'requester':
        return jsonify({'error': 'Esta app es solo para solicitantes. Usa la versión web para administrar o dar soporte.'}), 403

    token = _issue_jwt(user)
    return jsonify({
        'token': token,
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}
    })


MOBILE_EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


@bp.post('/mobile/register')
@csrf.exempt
@rate_limit(limit=6, window=60)
def mobile_register():
    """Registro de solicitantes desde la App Móvil. Devuelve un JWT (autologin)."""
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not name or len(name) < 2 or len(name) > 120:
        return jsonify({'error': 'El nombre debe tener entre 2 y 120 caracteres'}), 400
    if not email or not MOBILE_EMAIL_REGEX.match(email):
        return jsonify({'error': 'Ingresa un correo válido'}), 400
    if not password or len(password) < 8:
        return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'El correo ya está registrado. Inicia sesión.'}), 409

    user = User(name=name, email=email, role='requester')
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    requester = Requester(name=user.name, email=user.email, phone='')
    db.session.add(requester)
    db.session.commit()

    token = _issue_jwt(user)
    return jsonify({
        'token': token,
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}
    }), 201


@bp.get('/mobile/me')
@jwt_required
def mobile_me():
    user = request.jwt_user
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role})


@bp.post('/mobile/logout')
@csrf.exempt
@jwt_required
def mobile_logout():
    """Invalida el JWT actual (logout real, no solo borrarlo del teléfono)."""
    _blacklist_jwt(request.jwt_payload)
    return jsonify({'success': True})


def _save_ticket_photo(photo_b64: str) -> str:
    """Decodifica y guarda una foto en base64 (data URL o crudo). Devuelve la ruta relativa guardada."""
    if ',' in photo_b64 and photo_b64.strip().startswith('data:'):
        header, photo_b64 = photo_b64.split(',', 1)
        ext = 'jpg'
        if 'png' in header:
            ext = 'png'
        elif 'webp' in header:
            ext = 'webp'
    else:
        ext = 'jpg'

    if ext not in ALLOWED_PHOTO_EXTENSIONS:
        raise ValueError('Formato de imagen no permitido')

    try:
        raw = base64.b64decode(photo_b64, validate=True)
    except Exception:
        raise ValueError('La foto no es un base64 válido')

    if len(raw) > MAX_PHOTO_BYTES:
        raise ValueError('La foto supera el tamaño máximo permitido (6 MB)')

    upload_dir = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(upload_dir, filename), 'wb') as fh:
        fh.write(raw)

    return f"uploads/tickets/{filename}"


@bp.post('/mobile/tickets')
@csrf.exempt
@jwt_required
@rate_limit(limit=6, window=60)
def mobile_create_ticket():
    """Crea un ticket de campo desde la App Móvil (con foto). Queda visible al instante en la Web."""
    user = request.jwt_user
    data = request.get_json(silent=True) or {}

    title = (data.get('title') or '').strip()
    body = (data.get('body') or '').strip()
    priority = data.get('priority', 'medium')

    if not title or len(title) > 200:
        return jsonify({'error': 'title es requerido (máx. 200 caracteres)'}), 400
    if not body:
        return jsonify({'error': 'body (descripción) es requerido'}), 400
    if priority not in ('low', 'medium', 'high'):
        return jsonify({'error': 'priority debe ser low, medium o high'}), 400

    requester = Requester.query.filter_by(email=user.email).first()
    if not requester:
        requester = Requester(name=user.name, email=user.email)
        db.session.add(requester)
        db.session.flush()

    photo_path = None
    if data.get('photo_base64'):
        try:
            photo_path = _save_ticket_photo(data['photo_base64'])
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    ticket = Ticket(
        title=title,
        body=body,
        requester_id=requester.id,
        status='open',
        priority=priority,
        photo_path=photo_path,
        source='mobile',
    )
    db.session.add(ticket)
    db.session.flush()
    db.session.add(TicketEvent(ticket_id=ticket.id, user_id=user.id, body='Ticket creado desde la App Móvil'))
    db.session.commit()

    try:
        bridge = get_bridge_client()
        bridge.sync_ticket('create', {
            'id': ticket.id,
            'title': ticket.title,
            'body': ticket.body,
            'requester_id': ticket.requester_id,
            'status': ticket.status,
            'priority': ticket.priority,
            'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
        }, source='flask')
    except Exception as e:
        current_app.logger.error(f"Error syncing mobile ticket to bridge: {e}")

    return jsonify({
        'id': ticket.id,
        'title': ticket.title,
        'status': ticket.status,
        'priority': ticket.priority,
        'photo_url': _public_photo_url(photo_path),
        'created_at': ticket.created_at.isoformat(),
    }), 201


@bp.get('/mobile/tickets')
@jwt_required
def mobile_list_tickets():
    """Lista los tickets creados por el usuario autenticado de la App Móvil."""
    user = request.jwt_user
    requester = Requester.query.filter_by(email=user.email).first()

    if requester:
        tickets = Ticket.query.filter_by(requester_id=requester.id).order_by(Ticket.created_at.desc()).all()
    else:
        tickets = []

    return jsonify([{
        'id': t.id,
        'title': t.title,
        'body': t.body,
        'status': t.status,
        'priority': t.priority,
        'photo_url': _public_photo_url(t.photo_path),
        'created_at': t.created_at.isoformat(),
    } for t in tickets])


@bp.post('/tickets/<int:ticket_id>/feedback')
@login_required
def submit_feedback(ticket_id):
    """Calificación de satisfacción (Web). Solo el solicitante dueño del ticket, y solo si está cerrado."""
    if current_user.role != 'requester':
        return jsonify({'error': 'Solo los solicitantes pueden calificar tickets.'}), 403

    ticket = Ticket.query.get_or_404(ticket_id)
    requester = Requester.query.filter_by(email=current_user.email).first()
    if not requester or ticket.requester_id != requester.id:
        return jsonify({'error': 'No autorizado.'}), 403

    if ticket.status != 'closed':
        return jsonify({'error': 'Solo se puede calificar un ticket cerrado.'}), 400

    if SatisfactionTicket.query.filter_by(ticket_id=ticket.id).first():
        return jsonify({'error': 'Ya se envió feedback para este ticket.'}), 409

    data = request.get_json(silent=True) or {}
    calificacion = data.get('calificacion')
    if not isinstance(calificacion, int) or calificacion < 1 or calificacion > 5:
        return jsonify({'error': 'calificacion debe ser un entero entre 1 y 5.'}), 400
    comentario = (data.get('comentario') or '').strip()[:2000] or None

    feedback = SatisfactionTicket(
        ticket_id=ticket.id,
        user_id=current_user.id,
        calificacion=calificacion,
        comentario=comentario,
    )
    ticket.rating = calificacion
    db.session.add(feedback)
    db.session.commit()
    return jsonify({'success': True}), 201

