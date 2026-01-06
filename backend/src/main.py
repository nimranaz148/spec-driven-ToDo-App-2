"""FastAPI application entry point."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Mount

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from .db import create_tables, close_connection
from .routes import tasks, chat, voice, conversations
from .middleware import RateLimitMiddleware, RequestIDMiddleware, TimingMiddleware
from .utils.logger import get_logger, configure_logging
from .mcp_server import mcp_server

# Configure logging at application startup
configure_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# CORS origins - configure for your frontend
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("application_starting")
    await create_tables()
    logger.info("mcp_server_ready", endpoint="/mcp")
    logger.info("application_ready")
    yield

    # Shutdown
    logger.info("application_shutting_down")
    await close_connection()
    logger.info("application_stopped")


# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="Backend API for Todo Web Application",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add observability middleware (order matters!)
# 1. Request ID - adds unique ID to each request
app.add_middleware(RequestIDMiddleware)
# 2. Timing - tracks response times
app.add_middleware(TimingMiddleware)
# 3. Rate limiting - enforces rate limits
app.add_middleware(RateLimitMiddleware)

# Include routers
# Note: Authentication is handled by Better Auth on the frontend
# The backend only verifies JWT tokens via get_current_user dependency
app.include_router(tasks.router)
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(conversations.router)

# NOTE: MCP server runs as a separate process on port 8001
# Start it with: python -m src.mcp_server
# The agent connects to it via http://localhost:8001/mcp


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Todo API",
        "version": "1.0.0",
        "docs": "/docs",
    }
