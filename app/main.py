from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


from app.middleware.logging import LoggingMiddleware
from app.routers.health import router as health_router


app = FastAPI(
    title="AI Support Agent",
    version="1.0.0"
)


# -----------
# CORS CONFIG
# -----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------
# LOGGING
# -------
app.add_middleware(LoggingMiddleware)


# -------
# ROUTERS
# -------
app.include_router(health_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
