"""
Web interface routes for C.H.R.I.S.T. system.
"""

from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Setup templates
templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(templates_dir))

# Create router
web_router = APIRouter()


@web_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@web_router.get("/ingest", response_class=HTMLResponse)
async def ingest_page(request: Request):
    """Data ingestion page."""
    return templates.TemplateResponse("ingest.html", {"request": request})


@web_router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Search page."""
    return templates.TemplateResponse("search.html", {"request": request})


@web_router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Chat interface page."""
    return templates.TemplateResponse("chat.html", {"request": request})


@web_router.get("/reflections", response_class=HTMLResponse)
async def reflections_page(request: Request):
    """Reflections page."""
    return templates.TemplateResponse("reflections.html", {"request": request})


@web_router.get("/goals", response_class=HTMLResponse)
async def goals_page(request: Request):
    """Goals tracking page."""
    return templates.TemplateResponse("goals.html", {"request": request})


@web_router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page."""
    return templates.TemplateResponse("settings.html", {"request": request})


# Additional pages can be added here

def setup_web_routes(app):
    """Setup web routes and static files."""
    # Mount static files
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Include web routes
    app.include_router(web_router)