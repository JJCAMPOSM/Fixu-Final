from typing import Dict, Any
from config import Settings
from schemas import WebhookPayload, SyncResponse
from datetime import datetime
import httpx


class WebhookService:
    """Servicio para manejo de webhooks entre sistemas."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    async def handle_laravel_webhook(self, payload: WebhookPayload) -> SyncResponse:
        """Procesa webhooks entrantes de Laravel."""
        try:
            # Aquí se implementa la lógica para reenviar a Flask
            # o procesar el webhook según el evento
            event_handlers = {
                "user.created": self._handle_user_created,
                "user.updated": self._handle_user_updated,
                "ticket.created": self._handle_ticket_created,
                "ticket.updated": self._handle_ticket_updated,
            }
            
            handler = event_handlers.get(payload.event)
            if handler:
                return await handler(payload, source="laravel")
            
            return SyncResponse(
                success=True,
                message=f"Evento {payload.event} recibido pero no requiere acción",
                data={"event": payload.event, "entity_id": payload.entity_id}
            )
        except Exception as e:
            return SyncResponse(success=False, message=str(e))
    
    async def handle_flask_webhook(self, payload: WebhookPayload) -> SyncResponse:
        """Procesa webhooks entrantes de Flask."""
        try:
            event_handlers = {
                "ticket.created": self._handle_ticket_created,
                "ticket.updated": self._handle_ticket_updated,
                "comment.created": self._handle_comment_created,
            }
            
            handler = event_handlers.get(payload.event)
            if handler:
                return await handler(payload, source="flask")
            
            return SyncResponse(
                success=True,
                message=f"Evento {payload.event} recibido pero no requiere acción",
                data={"event": payload.event, "entity_id": payload.entity_id}
            )
        except Exception as e:
            return SyncResponse(success=False, message=str(e))
    
    async def _handle_user_created(self, payload: WebhookPayload, source: str) -> SyncResponse:
        """Maneja creación de usuario."""
        # Reenviar al otro sistema
        target = "flask" if source == "laravel" else "laravel"
        
        async with httpx.AsyncClient() as client:
            target_url = (
                self.settings.FLASK_APP_URL if target == "flask" 
                else self.settings.LARAVEL_ADMIN_URL
            )
            try:
                response = await client.post(
                    f"{target_url}/api/webhooks/user-created",
                    json=payload.data,
                    headers={"X-API-Key": self.settings.INTERNAL_API_KEY}
                )
                return SyncResponse(
                    success=response.status_code == 200,
                    message=f"Usuario replicado en {target}",
                    data={"target": target, "status": response.status_code}
                )
            except Exception as e:
                return SyncResponse(
                    success=False,
                    message=f"Error replicando a {target}: {str(e)}"
                )
    
    async def _handle_user_updated(self, payload: WebhookPayload, source: str) -> SyncResponse:
        """Maneja actualización de usuario."""
        target = "flask" if source == "laravel" else "laravel"
        
        async with httpx.AsyncClient() as client:
            target_url = (
                self.settings.FLASK_APP_URL if target == "flask" 
                else self.settings.LARAVEL_ADMIN_URL
            )
            try:
                response = await client.put(
                    f"{target_url}/api/webhooks/user-updated",
                    json=payload.data,
                    headers={"X-API-Key": self.settings.INTERNAL_API_KEY}
                )
                return SyncResponse(
                    success=response.status_code == 200,
                    message=f"Usuario actualizado en {target}",
                    data={"target": target, "status": response.status_code}
                )
            except Exception as e:
                return SyncResponse(
                    success=False,
                    message=f"Error actualizando en {target}: {str(e)}"
                )
    
    async def _handle_ticket_created(self, payload: WebhookPayload, source: str) -> SyncResponse:
        """Maneja creación de ticket."""
        target = "flask" if source == "laravel" else "laravel"
        
        async with httpx.AsyncClient() as client:
            target_url = (
                self.settings.FLASK_APP_URL if target == "flask" 
                else self.settings.LARAVEL_ADMIN_URL
            )
            try:
                response = await client.post(
                    f"{target_url}/api/webhooks/ticket-created",
                    json=payload.data,
                    headers={"X-API-Key": self.settings.INTERNAL_API_KEY}
                )
                return SyncResponse(
                    success=response.status_code == 200,
                    message=f"Ticket replicado en {target}",
                    data={"target": target, "status": response.status_code}
                )
            except Exception as e:
                return SyncResponse(
                    success=False,
                    message=f"Error replicando ticket a {target}: {str(e)}"
                )
    
    async def _handle_ticket_updated(self, payload: WebhookPayload, source: str) -> SyncResponse:
        """Maneja actualización de ticket."""
        target = "flask" if source == "laravel" else "laravel"
        
        async with httpx.AsyncClient() as client:
            target_url = (
                self.settings.FLASK_APP_URL if target == "flask" 
                else self.settings.LARAVEL_ADMIN_URL
            )
            try:
                response = await client.put(
                    f"{target_url}/api/webhooks/ticket-updated",
                    json=payload.data,
                    headers={"X-API-Key": self.settings.INTERNAL_API_KEY}
                )
                return SyncResponse(
                    success=response.status_code == 200,
                    message=f"Ticket actualizado en {target}",
                    data={"target": target, "status": response.status_code}
                )
            except Exception as e:
                return SyncResponse(
                    success=False,
                    message=f"Error actualizando ticket en {target}: {str(e)}"
                )
    
    async def _handle_comment_created(self, payload: WebhookPayload, source: str) -> SyncResponse:
        """Maneja creación de comentario."""
        target = "flask" if source == "laravel" else "laravel"
        
        async with httpx.AsyncClient() as client:
            target_url = (
                self.settings.FLASK_APP_URL if target == "flask" 
                else self.settings.LARAVEL_ADMIN_URL
            )
            try:
                response = await client.post(
                    f"{target_url}/api/webhooks/comment-created",
                    json=payload.data,
                    headers={"X-API-Key": self.settings.INTERNAL_API_KEY}
                )
                return SyncResponse(
                    success=response.status_code == 200,
                    message=f"Comentario replicado en {target}",
                    data={"target": target, "status": response.status_code}
                )
            except Exception as e:
                return SyncResponse(
                    success=False,
                    message=f"Error replicando comentario a {target}: {str(e)}"
                )
