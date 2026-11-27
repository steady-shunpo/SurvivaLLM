import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # init_db()
    # checkCacheAlive()
    yield


app = FastAPI(
    title="LLM Gateway",
    description="LLM Gateway API Service",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", summary="Root endpoint")
async def root():
    return {
        "message": "Welcome to LLM Gateway API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", summary="Health checkpoint", tags=["Health"])
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "llm-gateway",
        },
    )