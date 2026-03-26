from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import httpx
import os
from typing import Optional

from config import Settings, get_settings
from routers import sync, bridge, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación."""
    # Startup
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    yield
    # Shutdown
    await app.state.http_client.aclose()


app = FastAPI(
    title="Fixu Bridge API",
    description="API de comunicación entre Laravel Admin y Flask App",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(sync.router, prefix="/sync", tags=["sincronización"])
app.include_router(bridge.router, prefix="/bridge", tags=["bridge"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])


@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "ok", "service": "fixu-bridge"}


@app.get("/")
async def root():
    """Raíz de la API."""
    return {
        "service": "Fixu Bridge API",
        "version": "1.0.0",
        "endpoints": {
            "sync": "/sync",
            "bridge": "/bridge",
            "webhooks": "/webhooks",
            "health": "/health",
            "docs": "/docs"
        }
    }
