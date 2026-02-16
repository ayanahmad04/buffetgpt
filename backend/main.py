"""
BuffetGPT FastAPI Application
Entry point for the buffet strategy API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analyze, health, manual
from app.config import settings

app = FastAPI(
    title="BuffetGPT API",
    description="AI agent that generates optimal eating strategies from buffet images",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(analyze.router, prefix="/api/v1", tags=["Analyze"])
app.include_router(manual.router, prefix="/api/v1", tags=["Manual"])


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "BuffetGPT",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
