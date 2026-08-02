import os
from functools import wraps

import redis
from flask import current_app, jsonify, request
from prometheus_client import Counter

_redis_client = None

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


def rate_limit(limit=6, window=60):
    """Rate Limiting global basado en Redis (máximo `limit` peticiones por `window` segundos por IP/usuario)."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                r = get_redis()
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
