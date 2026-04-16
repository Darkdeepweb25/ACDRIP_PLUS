"""
ACDRIP+ - Main Application Entry Point
Autonomous Cyber Defense, Risk Intelligence & Pre-Breach Simulation Platform

Author: ACDRIP+ Team
Version: 1.0.0
"""

import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager

# Ensure backend directory is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from database import init_db

# Import route modules
from auth.routes import router as auth_router
from scanner.routes import router as scanner_router
from risk_engine.routes import router as risk_router
from simulation.routes import router as simulation_router
from monitoring.routes import router as monitoring_router
from reports.routes import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    print(f"""
    ================================================================
    
       _    ____ ____  ____  ___ ____  _
      / \\  / ___|  _ \\|  _ \\|_ _|  _ \\| |_
     / _ \\| |   | | | | |_) || || |_) |_  _|
    / ___ | |___| |_| |  _ < | ||  __/  |_|
   /_/   \\_\\____|____/|_| \\_|___|_|

    Autonomous Cyber Defense, Risk Intelligence
    & Pre-Breach Simulation Platform

    Version: {settings.APP_VERSION}
    Server:  http://{settings.HOST}:{settings.PORT}
    
    ================================================================
    """)

    # Initialize database
    init_db()

    # Ensure reports directory exists
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)

    yield

    print("\n[OK] ACDRIP+ shutting down gracefully...")


# ── Create FastAPI Application ────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include API Routers ──────────────────────────────────────

app.include_router(auth_router)
app.include_router(scanner_router)
app.include_router(risk_router)
app.include_router(simulation_router)
app.include_router(monitoring_router)
app.include_router(reports_router)

# ── Serve Frontend Static Files ──────────────────────────────

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


# ── API Health Check ──────────────────────────────────────────

@app.get("/api/health")
def health_check():
    return {
        "status": "operational",
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ── Serve Frontend ───────────────────────────────────────────

@app.get("/")
def serve_frontend():
    """Serve the main frontend application completely bypassing cache."""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        response = FileResponse(index_path)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return JSONResponse({"message": "ACDRIP+ API is running. Frontend not found."})


# ── Global Exception Handler ─────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


# ── Run Application ──────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
