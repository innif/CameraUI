from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.api import recordings, admin, settings, health
from app.core.config import settings as app_settings
from app.services.recording_scheduler import RecordingScheduler
from app.services.obs_service import OBSService
from app.services.file_service import FileService

# Configure logging with local timezone for filename
_local_tz = ZoneInfo(app_settings.TIMEZONE)
_log_time = datetime.now(timezone.utc).astimezone(_local_tz)
logging.basicConfig(
    filename=f'logs/log_{_log_time.strftime("%y-%m-%d--%H-%M-%S")}.log',
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the application"""
    # Startup
    logger.info("Starting ScheinCam Backend")
    
    # Initialize services
    obs_service = OBSService()
    file_service = FileService()
    
    # Configure OBS service
    await obs_service.configure(
        host=app_settings.OBS_HOST,
        port=app_settings.OBS_PORT,
        password=app_settings.OBS_PASSWORD,
        show_logo=app_settings.SHOW_LOGO
    )
    
    # Initialize file service
    await file_service.initialize(delete_age=app_settings.delete_age)
    
    # Create scheduler
    scheduler = RecordingScheduler(obs_service, file_service)
    
    # Store services in app state
    app.state.obs_service = obs_service
    app.state.file_service = file_service
    app.state.scheduler = scheduler
    
    # Start background tasks
    await scheduler.start()
    
    logger.info("ScheinCam Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ScheinCam Backend")
    await scheduler.stop()
    await obs_service.disconnect()
    logger.info("ScheinCam Backend shut down")


app = FastAPI(
    title="ScheinCam API",
    description="Backend API for ScheinCam recording system",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/videos", StaticFiles(directory="videos"), name="videos")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(recordings.router, prefix="/api/recordings", tags=["recordings"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ScheinCam Backend API",
        "version": "2.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=app_settings.DEBUG
    )
