from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request, status
from typing import Optional
import httpx

from config import get_settings, Settings
from services.rate_limit import rate_limit_dependency

router = APIRouter()


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


async def _forward_to_flask(
    http_client: httpx.AsyncClient,
    settings: Settings,
    method: str,
    path: str,
    authorization: Optional[str],
    json_body: Optional[dict],
    params: Optional[dict] = None,
):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization
    try:
        response = await http_client.request(
            method, f"{settings.FLASK_APP_URL}/api/mobile/{path}",
            json=json_body, headers=headers, params=params,
        )
    except httpx.HTTPError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="No se pudo contactar al backend Flask")

    if response.status_code >= 400:
        try:
            detail = response.json().get("error", response.text)
        except ValueError:
            detail = response.text
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json()


@router.post("/login", dependencies=[Depends(rate_limit_dependency(limit=6, window=60))])
async def mobile_login(
    payload: dict = Body(...),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    """Login de la App Móvil (Herramienta de Campo). Entrada pública vía Nginx :8080."""
    return await _forward_to_flask(http_client, settings, "POST", "login", None, payload)


@router.post("/register", dependencies=[Depends(rate_limit_dependency(limit=6, window=60))])
async def mobile_register(
    payload: dict = Body(...),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    """Registro de solicitantes desde la App Móvil. Entrada pública vía Nginx :8080."""
    return await _forward_to_flask(http_client, settings, "POST", "register", None, payload)


@router.get("/me")
async def mobile_me(
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    return await _forward_to_flask(http_client, settings, "GET", "me", authorization, None)


@router.post("/logout")
async def mobile_logout(
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    """Invalida el JWT actual (logout real vía blacklist en Redis)."""
    return await _forward_to_flask(http_client, settings, "POST", "logout", authorization, {})


@router.post("/tickets", dependencies=[Depends(rate_limit_dependency(limit=6, window=60))])
async def mobile_create_ticket(
    payload: dict = Body(...),
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    """Crea un ticket de campo (con foto) desde la App Móvil."""
    return await _forward_to_flask(http_client, settings, "POST", "tickets", authorization, payload)


@router.get("/tickets")
async def mobile_list_tickets(
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    return await _forward_to_flask(http_client, settings, "GET", "tickets", authorization, None)


@router.post("/tickets/{ticket_id}/resolution-photo", dependencies=[Depends(rate_limit_dependency(limit=20, window=60))])
async def mobile_upload_resolution_photo(
    ticket_id: int,
    payload: dict = Body(...),
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    """Sube la foto de resolución de un ticket (agente). Antes esta ruta no
    existía en el bridge, así que la App Móvil recibía 404 al intentarlo pese
    a que Flask ya soportaba el endpoint."""
    return await _forward_to_flask(
        http_client, settings, "POST", f"tickets/{ticket_id}/resolution-photo", authorization, payload,
    )


@router.post("/tickets/{ticket_id}/cancel", dependencies=[Depends(rate_limit_dependency(limit=20, window=60))])
async def mobile_cancel_ticket(
    ticket_id: int,
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    """Cancela un ticket (solicitante). Igual que resolution-photo, esta ruta
    faltaba en el bridge pese a que Flask ya soporta el endpoint."""
    return await _forward_to_flask(
        http_client, settings, "POST", f"tickets/{ticket_id}/cancel", authorization, {},
    )


@router.post("/tickets/{ticket_id}/status", dependencies=[Depends(rate_limit_dependency(limit=20, window=60))])
async def mobile_update_ticket_status(
    ticket_id: int,
    payload: dict = Body(...),
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    """Cambia el estado de un ticket (agente). Misma causa que arriba: ruta
    faltante en el bridge."""
    return await _forward_to_flask(
        http_client, settings, "POST", f"tickets/{ticket_id}/status", authorization, payload,
    )


@router.post("/tickets/{ticket_id}/feedback", dependencies=[Depends(rate_limit_dependency(limit=20, window=60))])
async def mobile_submit_feedback(
    ticket_id: int,
    payload: dict = Body(...),
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    """Calificación de satisfacción de un ticket cerrado (solicitante)."""
    return await _forward_to_flask(
        http_client, settings, "POST", f"tickets/{ticket_id}/feedback", authorization, payload,
    )


@router.get("/notifications")
async def mobile_notifications(
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    return await _forward_to_flask(http_client, settings, "GET", "notifications", authorization, None)


@router.post("/forgot-password", dependencies=[Depends(rate_limit_dependency(limit=4, window=300))])
async def mobile_forgot_password(
    payload: dict = Body(...),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    return await _forward_to_flask(http_client, settings, "POST", "forgot-password", None, payload)


@router.post("/reset-password", dependencies=[Depends(rate_limit_dependency(limit=6, window=300))])
async def mobile_reset_password(
    payload: dict = Body(...),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    return await _forward_to_flask(http_client, settings, "POST", "reset-password", None, payload)


@router.post("/change-password", dependencies=[Depends(rate_limit_dependency(limit=10, window=300))])
async def mobile_change_password(
    payload: dict = Body(...),
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    return await _forward_to_flask(http_client, settings, "POST", "change-password", authorization, payload)


@router.get("/maintenance")
async def mobile_list_maintenance(
    month: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    params = {"month": month} if month else None
    return await _forward_to_flask(http_client, settings, "GET", "maintenance", authorization, None, params=params)


@router.get("/maintenance/{task_id}")
async def mobile_maintenance_detail(
    task_id: int,
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    return await _forward_to_flask(http_client, settings, "GET", f"maintenance/{task_id}", authorization, None)


@router.post("/maintenance/{task_id}/checklist/{item_id}/toggle")
async def mobile_toggle_checklist_item(
    task_id: int,
    item_id: int,
    authorization: Optional[str] = Header(None),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
):
    return await _forward_to_flask(
        http_client, settings, "POST", f"maintenance/{task_id}/checklist/{item_id}/toggle", authorization, {},
    )
