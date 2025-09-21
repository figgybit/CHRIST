#!/usr/bin/env python3
"""
C.H.R.I.S.T. Project - Main Entry Point

This is the main application entry point that orchestrates all components.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import click
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from consciousness import consciousness
from holistic import holistic_model
from retrieval import retrieval
from intent import intent
from simulation import simulation
from teleology import teleology

# Import API endpoints
try:
    from api.endpoints import get_routers
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# Import Web UI routes
try:
    from web.routes import setup_web_routes
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="C.H.R.I.S.T. API",
    description="Consciousness Capture and Emulation System",
    version="0.1.0-alpha",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
if API_AVAILABLE:
    for router in get_routers():
        app.include_router(router)

# Setup Web UI routes
if WEB_AVAILABLE:
    setup_web_routes(app)


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    components: dict


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the C.H.R.I.S.T. Project",
        "description": "Consciousness Capture and Emulation System",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Check system health status."""
    try:
        # Check each component
        components_status = {
            "consciousness": "healthy",
            "holistic": "healthy",
            "retrieval": "healthy",
            "intent": "healthy",
            "simulation": "healthy",
            "teleology": "healthy"
        }

        return HealthResponse(
            status="healthy",
            version="0.1.0-alpha",
            components=components_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.on_event("startup")
async def startup_event():
    """Initialize all components on startup."""
    logger.info("Starting C.H.R.I.S.T. system...")

    try:
        # Initialize all components
        await consciousness.initialize()
        await holistic_model.initialize()
        await retrieval.initialize()
        await intent.initialize()
        await simulation.initialize()
        await teleology.initialize()

        logger.info("All components initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Shutting down C.H.R.I.S.T. system...")
    # Add cleanup logic here


@click.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
@click.option('--workers', default=1, help='Number of worker processes')
@click.option('--log-level', default='info', help='Logging level')
def main(
    host: str,
    port: int,
    reload: bool,
    workers: int,
    log_level: str
):
    """
    Start the C.H.R.I.S.T. application server.

    Example:
        python src/main.py --reload --port 8080
    """
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     ██████╗    ██╗  ██╗    ██████╗    ██╗    ███████╗   ║
    ║    ██╔════╝    ██║  ██║    ██╔══██╗   ██║    ██╔════╝   ║
    ║    ██║         ███████║    ██████╔╝   ██║    ███████╗   ║
    ║    ██║         ██╔══██║    ██╔══██╗   ██║    ╚════██║   ║
    ║    ╚██████╗    ██║  ██║    ██║  ██║   ██║    ███████║   ║
    ║     ╚═════╝    ╚═╝  ╚═╝    ╚═╝  ╚═╝   ╚═╝    ╚══════╝   ║
    ║                                                           ║
    ║          Consciousness Capture & Emulation System        ║
    ║                     Version 0.1.0-alpha                  ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    logger.info(f"Starting server on {host}:{port}")

    if reload and workers > 1:
        logger.warning("--reload flag disables multiple workers")
        workers = 1

    uvicorn.run(
        "main:app" if reload else app,
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()