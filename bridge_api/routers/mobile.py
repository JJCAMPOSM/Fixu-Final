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
):
    headers = {}
    if authorization:
        headers["Authorization"] = authorization
    try:
        response = await http_client.request(
            method, f"{settings.FLASK_APP_URL}/api/mobile/{path}",
            json=json_body, headers=headers,
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
