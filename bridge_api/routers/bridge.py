from fastapi import APIRouter, HTTPException, Depends, Header, status, Request
from fastapi.security import HTTPBearer
from typing import Optional, List, Dict, Any
import httpx

from config import get_settings, Settings
from schemas import SyncResponse
from services.bridge_service import BridgeService

router = APIRouter()
security = HTTPBearer()


async def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings)
) -> bool:
    """Verifica el API key interno."""
    if not x_api_key or x_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida"
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


@router.post("/flask/proxy/{path:path}")
async def proxy_to_flask(
    path: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Proxy de requests hacia Flask."""
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
    """Proxy de requests hacia Laravel."""
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
