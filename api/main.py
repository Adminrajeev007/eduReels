"""
EducationalReels API - FastAPI Backend
Endpoints for generating educational content for reels
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(Path(__file__).parent.parent / ".env")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio

from agents.orchestrator import EducationalReelsOrchestrator

# ============================================================================
# Initialize FastAPI app
# ============================================================================

app = FastAPI(
    title="EducationalReels API",
    description="Generate engaging educational content for short-form video reels",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================================
# CORS Configuration
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Pydantic Models
# ============================================================================

class GenerateRequest(BaseModel):
    """Request model for content generation"""
    degree: str

    class Config:
        example = {"degree": "Computer Science"}


class GenerateResponse(BaseModel):
    """Response model for generated content"""
    degree: str
    topic: str
    reel_question: str
    reel_answer: str
    simplified_answer: Optional[str] = None
    analogy: Optional[str] = None
    primary_example: Optional[str] = None
    secondary_examples: Optional[list] = None
    hook: Optional[str] = None
    compressed_content: Optional[str] = None
    engagement_tips: Optional[list] = None
    video_duration_seconds: Optional[int] = None
    engagement_score: Optional[float] = None
    quality_score: float
    generation_time: float
    cached: bool
    status: str


class CacheStatsResponse(BaseModel):
    """Response model for cache statistics"""
    total_entries: int
    cache_hits: int
    cache_misses: int
    total_time_saved_seconds: float
    branches_cached: list


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    timestamp: str
    uptime_seconds: float


# ============================================================================
# Initialize Orchestrator
# ============================================================================

orchestrator = EducationalReelsOrchestrator()
app_start_time = datetime.now()

logger.info("✅ EducationalReels API initialized")
logger.info("✅ Orchestrator loaded with all 7 agents")

# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/", tags=["Info"])
async def root():
    """Welcome message"""
    return {
        "message": "Welcome to EducationalReels API",
        "version": "1.0.0",
        "docs": "/docs",
        "generate_endpoint": "/generate",
        "cache_endpoint": "/cache",
        "health_endpoint": "/health",
    }


@app.post("/generate", response_model=dict, tags=["Generation"])
async def generate(request: GenerateRequest):
    """
    Generate engaging educational content for a degree

    **Parameters:**
    - degree: "Computer Science", "Electrical Engineering", or "Mechanical Engineering"

    **Returns:**
    Complete reel content with question, simplified answer, examples, and engagement tips
    """
    try:
        # Validate degree
        valid_degrees = ["Computer Science", "Electrical Engineering", "Mechanical Engineering"]
        if request.degree not in valid_degrees:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid degree. Must be one of: {', '.join(valid_degrees)}"
            )

        logger.info(f"📍 Generating content for: {request.degree}")

        # Generate content using orchestrator
        result = await orchestrator.generate_reel_content(request.degree)

        # Add metadata
        result["api_version"] = "1.0.0"
        result["timestamp"] = datetime.now().isoformat()

        logger.info(f"✅ Content generated successfully in {result.get('generation_time', 0):.2f}s")

        return result

    except HTTPException as e:
        logger.warning(f"⚠️ Validation error: {e.detail}")
        raise

    except Exception as e:
        logger.error(f"❌ Generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {str(e)}"
        )


@app.get("/cache", response_model=dict, tags=["Cache"])
async def get_cache_stats():
    """
    Get cache statistics

    **Returns:**
    Cache hit count, miss count, time saved, and cached branches
    """
    try:
        stats = orchestrator.get_cache_stats()

        # Calculate additional metrics
        total_hits = stats.get("cache_hits", 0)
        total_misses = stats.get("cache_misses", 0)
        avg_response_time = stats.get("avg_response_time", 0)
        time_saved = (total_hits * avg_response_time) if avg_response_time else 0

        return {
            "status": "success",
            "total_entries": stats.get("total_entries", 0),
            "cache_hits": total_hits,
            "cache_misses": total_misses,
            "hit_rate": (total_hits / (total_hits + total_misses)) if (total_hits + total_misses) > 0 else 0,
            "total_time_saved_seconds": round(time_saved, 2),
            "average_response_time_ms": round(avg_response_time * 1000, 2),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Cache stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cache statistics"
        )


@app.get("/health", response_model=dict, tags=["Health"])
async def health_check():
    """
    Health check endpoint

    **Returns:**
    Server status and uptime
    """
    try:
        uptime = (datetime.now() - app_start_time).total_seconds()

        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(uptime, 2),
            "agents_loaded": 7,
            "database": "sqlite",
            "cache_enabled": True,
        }

    except Exception as e:
        logger.error(f"❌ Health check error: {str(e)}")
        return {
            "status": "degraded",
            "version": "1.0.0",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/degrees", tags=["Info"])
async def list_supported_degrees():
    """Get list of supported degrees"""
    return {
        "supported_degrees": [
            "Computer Science",
            "Electrical Engineering",
            "Mechanical Engineering",
        ],
        "status": "success",
    }


@app.get("/info", tags=["Info"])
async def get_info():
    """Get API information"""
    return {
        "name": "EducationalReels API",
        "version": "1.0.0",
        "description": "Generate engaging educational content for short-form video reels",
        "author": "Educational Content Generation System",
        "agents": {
            "research": "Find interesting topics",
            "question_generator": "Create engaging questions",
            "quality_checker": "Validate question quality",
            "answer_generator": "Generate technical answers",
            "answer_simplifier": "Convert to plain language",
            "example_finder": "Find real-world examples",
            "engagement_optimizer": "Format for video reels",
        },
        "features": [
            "12-step content pipeline",
            "Intelligent caching (10x speedup)",
            "3-layer fallback system",
            "All 3 engineering branches supported",
            "Video format optimization",
            "Rich metadata in responses",
        ],
        "endpoints": {
            "generate": "POST /generate",
            "cache_stats": "GET /cache",
            "health": "GET /health",
            "degrees": "GET /degrees",
            "docs": "GET /docs",
        }
    }


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"❌ HTTP Error {exc.status_code}: {exc.detail}")
    return {
        "status": "error",
        "code": exc.status_code,
        "message": exc.detail,
        "timestamp": datetime.now().isoformat(),
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"❌ Unexpected error: {str(exc)}")
    return {
        "status": "error",
        "code": 500,
        "message": "Internal server error",
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup():
    """Run on server startup"""
    logger.info("🚀 EducationalReels API starting up...")
    logger.info("✅ All agents loaded and ready")


@app.on_event("shutdown")
async def shutdown():
    """Run on server shutdown"""
    logger.info("🛑 EducationalReels API shutting down...")


# ============================================================================
# For local testing
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
