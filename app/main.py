from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

@app.get("/health")
async def health():
    return {"status": "ok"}
