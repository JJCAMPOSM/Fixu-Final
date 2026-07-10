from fastapi import APIRouter, HTTPException, Depends, Header, status, Request
from fastapi.security import HTTPBearer
import httpx
from typing import Optional, List

from config import get_settings, Settings
from schemas import (
    UserResponse, UserCreate, UserUpdate,
    TicketResponse, TicketCreate, TicketUpdate,
    TeamResponse, TeamCreate, TeamUpdate,
    RequesterResponse, RequesterCreate, RequesterUpdate,
    CategoryResponse, CategoryCreate, CategoryUpdate,
    SyncRequest, SyncResponse
)
from services.sync_service import SyncService

router = APIRouter()
security = HTTPBearer()


import hmac
import hashlib

def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_hmac_signature: Optional[str] = Header(None, alias="X-HMAC-Signature"),
    settings: Settings = Depends(get_settings)
) -> bool:
    """Verifica el API key interno o firma HMAC."""
    if not x_api_key or x_api_key != settings.INTERNAL_API_KEY:
        if not x_hmac_signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de API key o firma HMAC inválidas"
            )
    return True


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Obtiene el cliente HTTP compartido desde el estado de la app."""
    return request.app.state.http_client


@router.post("/user", response_model=SyncResponse)
async def sync_user(
    data: SyncRequest,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Sincroniza un usuario entre Laravel y Flask."""
    sync_service = SyncService(http_client, settings)
    result = await sync_service.sync_user(data)
    return result


@router.post("/ticket", response_model=SyncResponse)
async def sync_ticket(
    data: SyncRequest,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Sincroniza un ticket entre Laravel y Flask."""
    sync_service = SyncService(http_client, settings)
    result = await sync_service.sync_ticket(data)
    return result


@router.post("/team", response_model=SyncResponse)
async def sync_team(
    data: SyncRequest,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Sincroniza un equipo entre Laravel y Flask."""
    sync_service = SyncService(http_client, settings)
    result = await sync_service.sync_team(data)
    return result


@router.post("/requester", response_model=SyncResponse)
async def sync_requester(
    data: SyncRequest,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Sincroniza un solicitante entre Laravel y Flask."""
    sync_service = SyncService(http_client, settings)
    result = await sync_service.sync_requester(data)
    return result


@router.post("/category", response_model=SyncResponse)
async def sync_category(
    data: SyncRequest,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Sincroniza una categoría entre Laravel y Flask."""
    sync_service = SyncService(http_client, settings)
    result = await sync_service.sync_category(data)
    return result


@router.post("/batch", response_model=List[SyncResponse])
async def sync_batch(
    items: List[SyncRequest],
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    authorized: bool = Depends(verify_api_key)
):
    """Sincronización en batch múltiples entidades."""
    sync_service = SyncService(http_client, settings)
    results = []
    for item in items:
        if item.entity == "users":
            result = await sync_service.sync_user(item)
        elif item.entity == "tickets":
            result = await sync_service.sync_ticket(item)
        elif item.entity == "teams":
            result = await sync_service.sync_team(item)
        elif item.entity == "requesters":
            result = await sync_service.sync_requester(item)
        elif item.entity == "categories":
            result = await sync_service.sync_category(item)
        else:
            result = SyncResponse(
                success=False,
                message=f"Entidad desconocida: {item.entity}"
            )
        results.append(result)
    return results
