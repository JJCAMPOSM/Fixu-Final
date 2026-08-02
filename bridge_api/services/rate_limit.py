import redis
from fastapi import Depends, HTTPException, Request, status

from config import Settings, get_settings

_redis_client = None


def _get_redis(settings: Settings) -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0,
            decode_responses=True, socket_timeout=2,
        )
    return _redis_client


def rate_limit_dependency(limit: int = 6, window: int = 60):
    """Rate Limiting global con Redis para endpoints públicos de bridge_api (App Móvil)."""
    async def _dependency(request: Request, settings: Settings = Depends(get_settings)):
        try:
            r = _get_redis(settings)
            identity = request.headers.get("authorization") or (request.client.host if request.client else "unknown")
            key = f"rate_limit:{identity}:{request.url.path}"

            current = r.get(key)
            if current and int(current) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Límite de tasa excedido ({limit} peticiones por {window}s).",
                )
            pipeline = r.pipeline()
            pipeline.incr(key)
            if not current:
                pipeline.expire(key, window)
            pipeline.execute()
        except redis.RedisError:
            # Fail-open: si Redis no está disponible no se bloquea la petición
            pass

    return _dependency
