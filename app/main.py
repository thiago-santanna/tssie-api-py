from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.redis import init_redis, close_redis
from app.api.webhooks import router as webhooks_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Conectar ao Redis
    await init_redis()
    yield
    # Shutdown: Fechar conexões do Redis
    await close_redis()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Plataforma SaaS Multi-tenant de Atendimento WhatsApp",
    lifespan=lifespan
)

app.include_router(webhooks_router, prefix="/api/webhooks", tags=["evolution-webhooks"])

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
