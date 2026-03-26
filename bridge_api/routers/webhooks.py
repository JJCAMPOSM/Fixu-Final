from fastapi import APIRouter, HTTPException, Depends, Header, status, Request
from fastapi.security import HTTPBearer
from typing import Optional, Dict, Any
import hmac
import hashlib

from config import get_settings, Settings
from schemas import WebhookPayload, SyncResponse
from services.webhook_service import WebhookService

router = APIRouter()
security = HTTPBearer()


async def verify_webhook_signature(
    request: Request,
    x_signature: Optional[str] = Header(None),
    settings: Settings = Depends(get_settings)
) -> bool:
    """Verifica la firma del webhook."""
    if not x_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma requerida"
        )
    
    body = await request.body()
    expected_signature = hmac.new(
        settings.INTERNAL_API_KEY.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(x_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma inválida"
        )
    return True


async def get_request_body(request: Request) -> Dict[str, Any]:
    """Obtiene el body de la request."""
    return await request.json()


@router.post("/laravel")
async def handle_laravel_webhook(
    payload: WebhookPayload,
    request: Request,
    settings: Settings = Depends(get_settings),
    verified: bool = Depends(verify_webhook_signature)
):
    """Recibe webhooks desde Laravel."""
    webhook_service = WebhookService(settings)
    result = await webhook_service.handle_laravel_webhook(payload)
    return result


@router.post("/flask")
async def handle_flask_webhook(
    payload: WebhookPayload,
    request: Request,
    settings: Settings = Depends(get_settings),
    verified: bool = Depends(verify_webhook_signature)
):
    """Recibe webhooks desde Flask."""
    webhook_service = WebhookService(settings)
    result = await webhook_service.handle_flask_webhook(payload)
    return result


@router.get("/config/laravel")
async def get_laravel_webhook_config(
    settings: Settings = Depends(get_settings),
    x_api_key: Optional[str] = Header(None)
):
    """Retorna configuración para webhooks en Laravel."""
    if x_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    return {
        "endpoint": f"http://bridge_api:8000/webhooks/laravel",
        "secret": settings.INTERNAL_API_KEY,
        "events": [
            "user.created",
            "user.updated",
            "user.deleted",
            "ticket.created",
            "ticket.updated",
            "ticket.deleted",
            "team.created",
            "team.updated",
            "requester.created",
            "requester.updated",
            "category.created",
            "category.updated"
        ]
    }


@router.get("/config/flask")
async def get_flask_webhook_config(
    settings: Settings = Depends(get_settings),
    x_api_key: Optional[str] = Header(None)
):
    """Retorna configuración para webhooks en Flask."""
    if x_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    return {
        "endpoint": f"http://bridge_api:8000/webhooks/flask",
        "secret": settings.INTERNAL_API_KEY,
        "events": [
            "ticket.created",
            "ticket.updated",
            "ticket.status_changed",
            "comment.created",
            "user.created",
            "user.updated"
        ]
    }
