from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import httpx
import os
from typing import Optional

from config import Settings, get_settings
from routers import sync, bridge, webhooks, mobile

MAX_BODY_SIZE = 8 * 1024 * 1024  # 8 MB, igual que MAX_CONTENT_LENGTH en Flask


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación."""
    # Startup
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    yield
    # Shutdown
    await app.state.http_client.aclose()


app = FastAPI(
    title="Fixu Bridge API",
    description="API de comunicación entre Laravel Admin y Flask App",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # Sin credenciales: la API usa Bearer tokens (JWT/HMAC/API-key), no
    # cookies, así que no hay nada que proteger con CORS credenciado.
    # allow_origins="*" + allow_credentials=True permitiría a cualquier sitio
    # hacer peticiones autenticadas con cookies del navegador del usuario.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from fastapi.responses import JSONResponse
import ipaddress

@app.middleware("http")
async def body_size_limit_middleware(request: Request, call_next):
    """Límite de tamaño de body como defensa en profundidad: nginx ya limita
    client_max_body_size, pero si bridge_api llegara a exponerse sin pasar
    por nginx (ej. acceso directo en la red interna), esto evita payloads
    gigantes."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BODY_SIZE:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Payload demasiado grande"}
        )
    return await call_next(request)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Cabeceras de seguridad HTTP (defensa en profundidad): esta es una API
    JSON, no debería renderizarse embebida en un iframe ni ser sniffeada
    como HTML/script por el navegador de un cliente."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.middleware("http")
async def ip_whitelist_middleware(request: Request, call_next):
    """Middleware de Whitelisting IP para asegurar que peticiones provienen de red interna Docker/Local."""
    client_host = request.client.host if request.client else "127.0.0.1"
    if client_host in ("testclient", "localhost", "127.0.0.1", "::1"):
        return await call_next(request)
    try:
        ip = ipaddress.ip_address(client_host)
        if not ip.is_private and not ip.is_loopback:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": f"Acceso denegado desde IP pública no autorizada: {client_host}"}
            )
    except ValueError:
        pass
    return await call_next(request)

# Routers
app.include_router(sync.router, prefix="/sync", tags=["sincronización"])
app.include_router(bridge.router, prefix="/bridge", tags=["bridge"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(mobile.router, prefix="/mobile", tags=["app-móvil"])


@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "ok", "service": "fixu-bridge"}


@app.get("/")
async def root():
    """Raíz de la API."""
    return {
        "service": "Fixu Bridge API",
        "version": "1.0.0",
        "endpoints": {
            "sync": "/sync",
            "bridge": "/bridge",
            "webhooks": "/webhooks",
            "mobile": "/mobile",
            "health": "/health",
            "docs": "/docs"
        }
    }
