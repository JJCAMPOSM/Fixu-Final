import os
from functools import wraps

import bcrypt
import redis
from flask import current_app, jsonify, request
from prometheus_client import Counter

_redis_client = None

# Hash bcrypt "señuelo": se compara contra él cuando un email de login no
# existe, para que la respuesta tarde lo mismo que cuando sí existe y la
# contraseña es incorrecta (evita enumerar cuentas por diferencia de tiempo).
DUMMY_PASSWORD_HASH = bcrypt.hashpw(b'dummy-password-for-timing', bcrypt.gensalt())

FAILED_LOGIN_LIMIT = 5
FAILED_LOGIN_LOCKOUT_SECONDS = 15 * 60

REQUESTS_TOTAL = Counter(
    'fixu_http_requests_total',
    'Peticiones HTTP procesadas por el rate limiter de Fixu',
    ['endpoint', 'result']  # result: allowed | blocked
)


def get_redis():
    """Cliente Redis compartido (lazy init) para Rate Limiting global."""
    global _redis_client
    if _redis_client is None:
        host = current_app.config.get('REDIS_HOST', os.environ.get('REDIS_HOST', 'redis'))
        port = current_app.config.get('REDIS_PORT', int(os.environ.get('REDIS_PORT', 6379)))
        _redis_client = redis.Redis(host=host, port=port, db=0, decode_responses=True, socket_timeout=2)
    return _redis_client


def _failed_login_key(email):
    return f'failed_login:{email}'


def is_account_locked(email):
    """Bloqueo por cuenta (además del rate limit por IP) tras demasiados
    intentos fallidos de login, para frenar fuerza bruta distribuida en
    varias IPs contra una misma cuenta."""
    try:
        r = get_redis()
        count = r.get(_failed_login_key(email))
        return bool(count) and int(count) >= FAILED_LOGIN_LIMIT
    except redis.RedisError:
        return False


def register_failed_login(email):
    try:
        r = get_redis()
        key = _failed_login_key(email)
        count = r.incr(key)
        if count == 1:
            r.expire(key, FAILED_LOGIN_LOCKOUT_SECONDS)
    except redis.RedisError:
        pass


def clear_failed_login(email):
    try:
        get_redis().delete(_failed_login_key(email))
    except redis.RedisError:
        pass


def rate_limit(limit=6, window=60):
    """Rate Limiting global basado en Redis (máximo `limit` peticiones por `window` segundos por IP/usuario)."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                r = get_redis()
                # request.remote_addr ya refleja la IP real del cliente gracias
                # a ProxyFix (fixu/__init__.py), que confía en el X-Forwarded-For
                # que agrega nginx (único proxy intermedio).
                identity = request.headers.get('Authorization', request.remote_addr or '127.0.0.1')
                key = f"rate_limit:{identity}:{request.endpoint}"

                current = r.get(key)
                if current and int(current) >= limit:
                    REQUESTS_TOTAL.labels(endpoint=request.endpoint, result='blocked').inc()
                    return jsonify({
                        'error': 'Too Many Requests',
                        'message': f'Límite de tasa excedido ({limit} peticiones por {window}s).'
                    }), 429

                pipeline = r.pipeline()
                pipeline.incr(key)
                if not current:
                    pipeline.expire(key, window)
                pipeline.execute()
                REQUESTS_TOTAL.labels(endpoint=request.endpoint, result='allowed').inc()
            except redis.RedisError:
                # Si Redis no está disponible no se bloquea la petición (fail-open)
                current_app.logger.warning('Redis no disponible, rate limiting omitido')

            return f(*args, **kwargs)
        return wrapped
    return decorator
