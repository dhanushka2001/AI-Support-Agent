from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.config import settings
from app.middleware.logging import LoggingMiddleware
from app.routers.health import router as health_router
from app.routers.pdf_upload import router as pdf_upload_router
from app.routers.pdf_extract import router as pdf_extract_router
from app.routers.qdrant_health import router as qdrant_health_router
from app.db.qdrant import create_collection_if_not_exists


app = FastAPI(
    title="AI Support Agent",
    version="1.0.0"
)


# -----------------
# QDRANT COLLECTION
# -----------------
@app.on_event("startup")
def startup_event():
    create_collection_if_not_exists()


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
app.include_router(pdf_upload_router)
app.include_router(pdf_extract_router)
app.include_router(qdrant_health_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
