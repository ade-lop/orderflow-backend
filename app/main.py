from fastapi import FastAPI

from app.api.routes.orders import router as orders_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(orders_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
