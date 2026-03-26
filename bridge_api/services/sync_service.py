import httpx
from typing import Optional, Dict, Any, List
from config import Settings
from schemas import SyncRequest, SyncResponse
from datetime import datetime

class SyncService:
    """Servicio para sincronización de datos entre Laravel y Flask."""
    
    def __init__(self, http_client: httpx.AsyncClient, settings: Settings):
        self.client = http_client
        self.settings = settings
    
    async def _forward_to_flask(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Envía datos a Flask."""
        try:
            response = await self.client.post(
                f"{self.settings.FLASK_APP_URL}/api/sync/{endpoint}",
                json=data,
                headers={"X-API-Key": self.settings.INTERNAL_API_KEY}
            )
            return response.json() if response.status_code == 200 else {"error": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    async def _forward_to_laravel(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Envía datos a Laravel."""
        try:
            response = await self.client.post(
                f"{self.settings.LARAVEL_ADMIN_URL}/api/sync/{endpoint}",
                json=data,
                headers={"X-API-Key": self.settings.INTERNAL_API_KEY}
            )
            return response.json() if response.status_code == 200 else {"error": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    async def sync_user(self, data: SyncRequest) -> SyncResponse:
        """Sincroniza un usuario."""
        try:
            # Si viene de Laravel, reenviar a Flask
            if data.source == "laravel":
                result = await self._forward_to_flask("user", data.data)
            else:
                result = await self._forward_to_laravel("user", data.data)
            
            success = "error" not in result
            return SyncResponse(
                success=success,
                message="Usuario sincronizado" if success else result.get("error", "Error"),
                data=result if success else None
            )
        except Exception as e:
            return SyncResponse(success=False, message=str(e))
    
    async def sync_ticket(self, data: SyncRequest) -> SyncResponse:
        """Sincroniza un ticket."""
        try:
            if data.source == "laravel":
                result = await self._forward_to_flask("ticket", data.data)
            else:
                result = await self._forward_to_laravel("ticket", data.data)
            
            success = "error" not in result
            return SyncResponse(
                success=success,
                message="Ticket sincronizado" if success else result.get("error", "Error"),
                data=result if success else None
            )
        except Exception as e:
            return SyncResponse(success=False, message=str(e))
    
    async def sync_team(self, data: SyncRequest) -> SyncResponse:
        """Sincroniza un equipo."""
        try:
            if data.source == "laravel":
                result = await self._forward_to_flask("team", data.data)
            else:
                result = await self._forward_to_laravel("team", data.data)
            
            success = "error" not in result
            return SyncResponse(
                success=success,
                message="Equipo sincronizado" if success else result.get("error", "Error"),
                data=result if success else None
            )
        except Exception as e:
            return SyncResponse(success=False, message=str(e))
    
    async def sync_requester(self, data: SyncRequest) -> SyncResponse:
        """Sincroniza un solicitante."""
        try:
            if data.source == "laravel":
                result = await self._forward_to_flask("requester", data.data)
            else:
                result = await self._forward_to_laravel("requester", data.data)
            
            success = "error" not in result
            return SyncResponse(
                success=success,
                message="Solicitante sincronizado" if success else result.get("error", "Error"),
                data=result if success else None
            )
        except Exception as e:
            return SyncResponse(success=False, message=str(e))
    
    async def sync_category(self, data: SyncRequest) -> SyncResponse:
        """Sincroniza una categoría."""
        try:
            if data.source == "laravel":
                result = await self._forward_to_flask("category", data.data)
            else:
                result = await self._forward_to_laravel("category", data.data)
            
            success = "error" not in result
            return SyncResponse(
                success=success,
                message="Categoría sincronizada" if success else result.get("error", "Error"),
                data=result if success else None
            )
        except Exception as e:
            return SyncResponse(success=False, message=str(e))
