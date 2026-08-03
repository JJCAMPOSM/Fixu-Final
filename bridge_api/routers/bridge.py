from fastapi import APIRouter, HTTPException, Depends, Header, status, Request
from fastapi.security import HTTPBearer
from typing import Optional, List, Dict, Any
import httpx

from config import get_settings, Settings
from schemas import SyncResponse
from services.bridge_service import BridgeService

router = APIRouter()
security = HTTPBearer()


import hmac
import hashlib

async def verify_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_hmac_signature: Optional[str] = Header(None, alias="X-HMAC-Signature"),
    settings: Settings = Depends(get_settings)
) -> bool:
    """Verifica el API key interno o firma HMAC para endpoints de proxy y conciliación."""
    if not x_api_key or x_api_key != settings.INTERNAL_API_KEY:
        if not x_hmac_signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de API key o firma HMAC inválidas en el bridge"
            )
        body = await request.body()
        expected = hmac.new(
            settings.HMAC_SECRET_KEY.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(x_hmac_signature, expected):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firma HMAC inválida en el bridge"
            )
    return True


async def get_http_client(request: Request) -> httpx.AsyncClient:
    """Obtiene el cliente HTTP compartido desde el estado de la app."""
    return request.app.state.http_client


@router.get("/flask/health")
async def check_flask_health(
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Verifica la salud del servicio Flask."""
    bridge = BridgeService(http_client, settings)
    health = await bridge.check_flask_health()
    return health


@router.get("/laravel/health")
async def check_laravel_health(
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Verifica la salud del servicio Laravel."""
    bridge = BridgeService(http_client, settings)
    health = await bridge.check_laravel_health()
    return health


@router.get("/stats")
async def get_system_stats(
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Obtiene estadísticas de ambos sistemas."""
    bridge = BridgeService(http_client, settings)
    stats = await bridge.get_combined_stats()
    return stats


# Whitelist de prefijos permitidos en el proxy genérico: sin esto, cualquiera
# con el INTERNAL_API_KEY/HMAC podía usar este endpoint para alcanzar
# CUALQUIER ruta interna de Flask/Laravel (no solo las pensadas para
# consultarse combinadas), incluyendo rutas administrativas no diseñadas
# para exponerse vía proxy.
_FLASK_PROXY_ALLOWED_PREFIXES = ("api/users", "api/tickets")
_LARAVEL_PROXY_ALLOWED_PREFIXES = ("users", "tickets")


def _check_proxy_path_allowed(path: str, allowed_prefixes: tuple) -> None:
    if not any(path == p or path.startswith(p + "?") for p in allowed_prefixes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ruta no permitida en el proxy interno"
        )


@router.post("/flask/proxy/{path:path}")
async def proxy_to_flask(
    path: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Proxy de requests hacia Flask (solo rutas de solo-lectura en whitelist)."""
    _check_proxy_path_allowed(path, _FLASK_PROXY_ALLOWED_PREFIXES)
    bridge = BridgeService(http_client, settings)
    result = await bridge.proxy_to_flask(path, method, data)
    return result


@router.post("/laravel/proxy/{path:path}")
async def proxy_to_laravel(
    path: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Proxy de requests hacia Laravel (solo rutas de solo-lectura en whitelist)."""
    _check_proxy_path_allowed(path, _LARAVEL_PROXY_ALLOWED_PREFIXES)
    bridge = BridgeService(http_client, settings)
    result = await bridge.proxy_to_laravel(path, method, data)
    return result


@router.get("/users/merged")
async def get_merged_users(
    page: int = 1,
    limit: int = 50,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Obtiene usuarios combinados de ambos sistemas."""
    bridge = BridgeService(http_client, settings)
    users = await bridge.get_merged_users(page, limit)
    return users


@router.get("/tickets/merged")
async def get_merged_tickets(
    page: int = 1,
    limit: int = 50,
    status: Optional[str] = None,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Obtiene tickets combinados de ambos sistemas."""
    bridge = BridgeService(http_client, settings)
    tickets = await bridge.get_merged_tickets(page, limit, status)
    return tickets
