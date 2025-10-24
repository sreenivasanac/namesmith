"""FastAPI application for Namesmith backend."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, domains, health, jobs
from .settings import settings

logger = logging.getLogger(__name__)

app = FastAPI(title="Namesmith API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(domains.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": settings.branding_name, "status": "ok"}
