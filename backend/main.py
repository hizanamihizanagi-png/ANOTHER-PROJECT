"""
ScorAI — FastAPI Application Entry Point.
Le cerveau central qui orchestre toutes les routes API.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import time

from backend.core.config import settings

# ============================================================
# App Initialization
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Infrastructure d'Intelligence Artificielle de Crédit via l'Épargne Gamifiée — Pan-African Credit Bureau MVP",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={"name": "ScorAI Team", "url": "https://scorai.africa"},
)

# ============================================================
# Middleware
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log toutes les requêtes avec timing."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    if settings.DEBUG:
        print(f"[{request.method}] {request.url.path} → {response.status_code} ({duration:.3f}s)")
    return response


# ============================================================
# Health Check
# ============================================================

@app.get("/")
async def root():
    """Root redirect to API docs."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_PREFIX}/docs",
    }


@app.get(f"{settings.API_PREFIX}/health")
async def health_check():
    """Health check endpoint pour le monitoring."""
    return {
        "status": "operational",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "virtual_ledger": "ready",
            "sports_trigger": "ready",
            "momo_gateway": "ready",
            "scorai_engine": "ready",
            "credit_engine": "ready",
        },
    }


# ============================================================
# API Routes Import (enregistrés après les services)
# ============================================================

from backend.api.wallet_routes import wallet_router
from backend.api.trigger_routes import trigger_router
from backend.api.score_routes import score_router
from backend.api.loan_routes import loan_router
from backend.api.auth_routes import auth_router
from backend.api.analytics_routes import analytics_router

app.include_router(wallet_router, prefix=settings.API_PREFIX, tags=["Wallet"])
app.include_router(trigger_router, prefix=settings.API_PREFIX, tags=["Triggers"])
app.include_router(score_router, prefix=settings.API_PREFIX, tags=["ScorAI Engine"])
app.include_router(loan_router, prefix=settings.API_PREFIX, tags=["Credit"])
app.include_router(auth_router, prefix=settings.API_PREFIX, tags=["Auth"])
app.include_router(analytics_router, prefix=settings.API_PREFIX, tags=["Analytics"])


# ============================================================
# Global Exception Handler
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Capture toutes les exceptions non gérées."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": str(exc) if settings.DEBUG else "Une erreur interne est survenue.",
            "path": str(request.url.path),
        },
    )
