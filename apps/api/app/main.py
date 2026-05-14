from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api_keys.routes import router as api_keys_router
from app.core.config import get_settings
from app.core.database import init_db
from app.organizations.routes import router as organizations_router
from app.projects.routes import router as projects_router
from app.protected_api.routes import router as protected_api_router
from app.usage.routes import router as usage_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(organizations_router)
app.include_router(projects_router)
app.include_router(api_keys_router)
app.include_router(protected_api_router)
app.include_router(usage_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
def readiness_check() -> dict[str, str]:
    # DB/Redis checks become deeper later.
    return {"status": "ready"}
