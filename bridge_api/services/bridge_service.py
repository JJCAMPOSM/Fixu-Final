import httpx
from typing import Optional, Dict, Any, List
from config import Settings


class BridgeService:
    """Servicio para comunicación bidireccional entre Flask y Laravel."""
    
    def __init__(self, http_client: httpx.AsyncClient, settings: Settings):
        self.client = http_client
        self.settings = settings
    
    async def check_flask_health(self) -> Dict[str, Any]:
        """Verifica salud de Flask."""
        try:
            response = await self.client.get(
                f"{self.settings.FLASK_APP_URL}/health",
                timeout=5.0
            )
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def check_laravel_health(self) -> Dict[str, Any]:
        """Verifica salud de Laravel."""
        try:
            response = await self.client.get(
                f"{self.settings.LARAVEL_ADMIN_URL}/health",
                timeout=5.0
            )
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_combined_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas combinadas."""
        flask_health = await self.check_flask_health()
        laravel_health = await self.check_laravel_health()
        
        return {
            "services": {
                "flask": flask_health,
                "laravel": laravel_health
            },
            "bridge_status": "operational" 
                if flask_health["status"] == "healthy" and laravel_health["status"] == "healthy"
                else "degraded"
        }
    
    async def proxy_to_flask(self, path: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Proxy hacia Flask."""
        url = f"{self.settings.FLASK_APP_URL}/{path}"
        try:
            if method.upper() == "GET":
                response = await self.client.get(url, headers={"X-API-Key": self.settings.INTERNAL_API_KEY})
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data, headers={"X-API-Key": self.settings.INTERNAL_API_KEY})
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=data, headers={"X-API-Key": self.settings.INTERNAL_API_KEY})
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers={"X-API-Key": self.settings.INTERNAL_API_KEY})
            else:
                return {"error": f"Método no soportado: {method}"}
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.status_code < 400 else None,
                "error": response.text if response.status_code >= 400 else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def proxy_to_laravel(self, path: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Proxy hacia Laravel."""
        url = f"{self.settings.LARAVEL_ADMIN_URL}/api/{path}"
        try:
            if method.upper() == "GET":
                response = await self.client.get(url, headers={"X-API-Key": self.settings.INTERNAL_API_KEY})
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data, headers={"X-API-Key": self.settings.INTERNAL_API_KEY})
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=data, headers={"X-API-Key": self.settings.INTERNAL_API_KEY})
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers={"X-API-Key": self.settings.INTERNAL_API_KEY})
            else:
                return {"error": f"Método no soportado: {method}"}
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.status_code < 400 else None,
                "error": response.text if response.status_code >= 400 else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_merged_users(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Obtiene usuarios de ambos sistemas."""
        flask_result = await self.proxy_to_flask(f"api/users?page={page}&limit={limit}")
        laravel_result = await self.proxy_to_laravel(f"users?page={page}&limit={limit}")
        
        flask_users = flask_result.get("data", {}).get("users", [])
        laravel_users = laravel_result.get("data", {}).get("data", [])
        
        # Merge y deduplicación por email
        all_users = {u["email"]: u for u in flask_users}
        for u in laravel_users:
            if u["email"] not in all_users:
                all_users[u["email"]] = u
        
        return {
            "users": list(all_users.values()),
            "total": len(all_users),
            "sources": {
                "flask_count": len(flask_users),
                "laravel_count": len(laravel_users)
            }
        }
    
    async def get_merged_tickets(self, page: int = 1, limit: int = 50, status: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene tickets de ambos sistemas."""
        status_filter = f"&status={status}" if status else ""
        flask_result = await self.proxy_to_flask(f"api/tickets?page={page}&limit={limit}{status_filter}")
        laravel_result = await self.proxy_to_laravel(f"tickets?page={page}&limit={limit}{status_filter}")
        
        flask_tickets = flask_result.get("data", {}).get("tickets", [])
        laravel_tickets = laravel_result.get("data", {}).get("data", [])
        
        return {
            "tickets": flask_tickets + laravel_tickets,
            "total": len(flask_tickets) + len(laravel_tickets),
            "sources": {
                "flask_count": len(flask_tickets),
                "laravel_count": len(laravel_tickets)
            }
        }
