import requests
import os
import json
import hmac
import hashlib
from typing import Optional, Dict, Any


class BridgeAPIClient:
    """Cliente para comunicarse con el Bridge API (FastAPI)."""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or os.getenv("BRIDGE_API_URL", "http://bridge_api:8000")
        self.api_key = api_key or os.getenv("INTERNAL_API_KEY", "internal-bridge-secret-key")
        self.hmac_secret = os.getenv("HMAC_SECRET_KEY", "internal-hmac-secret-key")
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Realiza una petición HTTP al Bridge API."""
        url = f"{self.base_url}{endpoint}"
        headers = dict(self.headers)
        body_bytes = None
        if data is not None:
            body_bytes = json.dumps(data).encode("utf-8")
            signature = hmac.new(
                self.hmac_secret.encode("utf-8"),
                body_bytes,
                hashlib.sha256
            ).hexdigest()
            headers["X-HMAC-Signature"] = signature
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, data=body_bytes, headers=headers, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, data=body_bytes, headers=headers, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return {"error": f"Método no soportado: {method}"}
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    # ============ Health Checks ============
    def health_check(self) -> Dict[str, Any]:
        """Verifica salud del Bridge API."""
        return self._request("GET", "/health")
    
    def check_flask_health(self) -> Dict[str, Any]:
        """Verifica salud de Flask a través del Bridge."""
        return self._request("GET", "/bridge/flask/health")
    
    def check_laravel_health(self) -> Dict[str, Any]:
        """Verifica salud de Laravel a través del Bridge."""
        return self._request("GET", "/bridge/laravel/health")
    
    # ============ Sincronización ============
    def sync_user(self, action: str, data: Dict, source: str = "flask") -> Dict[str, Any]:
        """Sincroniza un usuario."""
        payload = {
            "entity": "users",
            "action": action,
            "data": data,
            "source": source
        }
        return self._request("POST", "/sync/user", payload)
    
    def sync_ticket(self, action: str, data: Dict, source: str = "flask") -> Dict[str, Any]:
        """Sincroniza un ticket."""
        payload = {
            "entity": "tickets",
            "action": action,
            "data": data,
            "source": source
        }
        return self._request("POST", "/sync/ticket", payload)
    
    def sync_team(self, action: str, data: Dict, source: str = "flask") -> Dict[str, Any]:
        """Sincroniza un equipo."""
        payload = {
            "entity": "teams",
            "action": action,
            "data": data,
            "source": source
        }
        return self._request("POST", "/sync/team", payload)
    
    def sync_requester(self, action: str, data: Dict, source: str = "flask") -> Dict[str, Any]:
        """Sincroniza un solicitante."""
        payload = {
            "entity": "requesters",
            "action": action,
            "data": data,
            "source": source
        }
        return self._request("POST", "/sync/requester", payload)
    
    def sync_category(self, action: str, data: Dict, source: str = "flask") -> Dict[str, Any]:
        """Sincroniza una categoría."""
        payload = {
            "entity": "categories",
            "action": action,
            "data": data,
            "source": source
        }
        return self._request("POST", "/sync/category", payload)
    
    def sync_batch(self, items: list) -> Dict[str, Any]:
        """Sincronización en batch."""
        return self._request("POST", "/sync/batch", items)
    
    # ============ Bridge/Proxy ============
    def proxy_to_laravel(self, path: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Proxy hacia Laravel."""
        payload = {"path": path, "method": method, "data": data}
        return self._request("POST", f"/bridge/laravel/proxy/{path}", payload)
    
    def get_merged_users(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Obtiene usuarios combinados."""
        return self._request("GET", f"/bridge/users/merged?page={page}&limit={limit}")
    
    def get_merged_tickets(self, page: int = 1, limit: int = 50, status: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene tickets combinados."""
        url = f"/bridge/tickets/merged?page={page}&limit={limit}"
        if status:
            url += f"&status={status}"
        return self._request("GET", url)
    
    # ============ Webhooks ============
    def send_webhook_to_laravel(self, event: str, entity: str, entity_id: int, data: Dict) -> Dict[str, Any]:
        """Envía un webhook a Laravel."""
        payload = {
            "event": event,
            "entity": entity,
            "entity_id": entity_id,
            "data": data
        }
        return self._request("POST", "/webhooks/laravel", payload)


# Instancia singleton para uso en la aplicación
_bridge_client = None

def get_bridge_client() -> BridgeAPIClient:
    """Obtiene instancia del cliente Bridge API."""
    global _bridge_client
    if _bridge_client is None:
        _bridge_client = BridgeAPIClient()
    return _bridge_client
