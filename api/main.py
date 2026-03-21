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
from tools.reel_queue import ReelQueueManager
from tools.background_generator import BackgroundReelGenerator
from tools.qa_database import QADatabaseManager

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
queue_manager = ReelQueueManager()
qa_database = QADatabaseManager()
background_generator = BackgroundReelGenerator(
    orchestrator=orchestrator,
    queue_manager=queue_manager,
    target_queue_size=5,
    degrees=["Computer Science", "Electrical Engineering", "Mechanical Engineering"]
)
app_start_time = datetime.now()

logger.info("✅ EducationalReels API initialized")
logger.info("✅ Orchestrator loaded with all 7 agents")
logger.info("✅ Reel queue manager initialized")
logger.info("✅ Backup Q&A database initialized")
logger.info("✅ Background reel generator ready to start")

# ============================================================================
# Startup Event - Start Background Reel Generator
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Start background reel generation on app startup"""
    logger.info("🚀 Starting background reel generator...")
    asyncio.create_task(background_generator.start())
    logger.info("✅ Background reel generator started")

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
# Reels Endpoint - Horizontal Scrolling Cards
# ============================================================================

@app.get("/api/reels")
async def get_reels(degree: str = "Computer Science", count: int = 1, skip_cache: bool = False):
    """
    Get reels from pre-generated queue for instant display.
    
    **Parameters:**
    - degree: "Computer Science", "Electrical Engineering", or "Mechanical Engineering"
    - count: Number of reels to return (default: 1)
    - skip_cache: If True, force generation instead of using queue (default: False)
    
    **Returns:**
    List of reel objects with questions and simplified answers
    """
    try:
        valid_degrees = ["Computer Science", "Electrical Engineering", "Mechanical Engineering"]
        if degree not in valid_degrees:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid degree. Must be one of: {', '.join(valid_degrees)}"
            )
        
        logger.info(f"📺 Retrieving {count} reels for {degree} (skip_cache={skip_cache})")
        
        reels = []
        
        # If skip_cache is True or queue is empty, try backup Q&A first
        queue_size = queue_manager.get_queue_size(degree)
        
        if skip_cache or queue_size == 0:
            if skip_cache:
                logger.info(f"⚠️ skip_cache=True, trying to generate fresh content...")
            else:
                logger.warning(f"⚠️ Queue is empty for {degree}, serving from backup Q&A database...")
            
            # First, try to serve backup Q&A while generating happens in background
            backup_qa_served = False
            for i in range(min(count, 5)):
                try:
                    qa = qa_database.get_random_qa(degree)
                    if qa:
                        reel = {
                            "id": i + 1,
                            "degree": degree,
                            "topic": qa.get("topic"),
                            "question": qa.get("question"),
                            "answer": qa.get("answer"),
                            "analogy": qa.get("analogy", ""),
                            "hook": qa.get("hook", ""),
                            "examples": qa.get("examples", []),
                            "quality_score": qa.get("quality_score", 8.0),
                            "engagement_score": qa.get("engagement_score", 7.5),
                            "cached": False,
                            "timestamp": qa.get("created_at"),
                            "source": "backup-qa-database"
                        }
                        reels.append(reel)
                        backup_qa_served = True
                except Exception as e:
                    logger.warning(f"⚠️ Failed to get backup Q&A: {str(e)}")
                    continue
            
            if backup_qa_served:
                logger.info(f"✅ Served {len(reels)} reels from backup Q&A database")
                
                # Return backup Q&A with info message
                qa_stats = qa_database.get_stats(degree)
                return {
                    "status": "success",
                    "count": len(reels),
                    "degree": degree,
                    "reels": reels,
                    "message": "Serving from backup Q&A database while generating fresh content",
                    "queue_status": {
                        "queue_size": queue_size,
                        "target_size": 5,
                        "total_generated": 0,
                        "total_served": 0
                    },
                    "backup_qa_stats": qa_stats,
                    "api_version": "1.0.0"
                }
            
            # If backup Q&A also failed, try generating fresh content
            logger.warning(f"⚠️ Backup Q&A not available, attempting fresh generation...")
            for i in range(min(count, 10)):
                try:
                    if i > 0:
                        await asyncio.sleep(0.2)
                    
                    result = await orchestrator.generate_reel_content(degree, skip_cache=True)
                    
                    # Create simplified reel format
                    reel = {
                        "id": i + 1,
                        "degree": result.get("degree"),
                        "topic": result.get("topic"),
                        "question": result.get("reel_question"),
                        "answer": result.get("simplified_answer", result.get("reel_answer")),
                        "analogy": result.get("analogy", ""),
                        "hook": result.get("hook", ""),
                        "examples": [
                            result.get("primary_example", ""),
                            *result.get("secondary_examples", [])
                        ],
                        "quality_score": result.get("quality_score", 0),
                        "engagement_score": result.get("engagement_score", 0),
                        "cached": result.get("cached", False),
                        "timestamp": result.get("timestamp"),
                        "source": "on-demand-generation"
                    }
                    reels.append(reel)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to generate reel {i + 1}: {str(e)}")
                    continue
        else:
            # Serve from queue (much faster!)
            logger.info(f"✅ Serving from queue (queue_size={queue_size})")
            
            for i in range(min(count, 5)):  # Limit to 5 from queue
                try:
                    reel_data = queue_manager.get_next_reel(degree)
                    if reel_data:
                        reel_data["source"] = "pre-generated-queue"
                        reel_data["id"] = i + 1
                        reels.append(reel_data)
                    else:
                        break
                except Exception as e:
                    logger.warning(f"⚠️ Failed to retrieve reel from queue: {str(e)}")
                    break
        
        if not reels:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve any reels"
            )
        
        # Log queue status
        queue_stats = queue_manager.get_stats(degree)
        logger.info(f"✅ Returned {len(reels)} reels. Queue stats: {queue_stats}")
        
        return {
            "status": "success",
            "count": len(reels),
            "degree": degree,
            "reels": reels,
            "queue_status": queue_stats,
            "api_version": "1.0.0"
        }
    
    except HTTPException as e:
        logger.warning(f"⚠️ Validation error: {e.detail}")
        raise
    
    except Exception as e:
        logger.error(f"❌ Reels generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate reels: {str(e)}"
        )


@app.get("/api/reels/status", tags=["Queue Management"])
async def get_reels_status():
    """
    Get the status of the background reel generation queue.
    
    **Returns:**
    Queue statistics for each degree including queue size, generation metrics, etc.
    """
    try:
        logger.info("📊 Fetching reel queue status...")
        
        status_data = {}
        degrees = ["Computer Science", "Electrical Engineering", "Mechanical Engineering"]
        
        for degree in degrees:
            stats = queue_manager.get_stats(degree)
            queue_size = queue_manager.get_queue_size(degree)
            status_data[degree] = {
                "queue_size": queue_size,
                "target_size": 5,
                "healthy": queue_size >= 5,
                "total_generated": stats.get("total_generated", 0),
                "total_served": stats.get("total_served", 0),
                "last_generated": stats.get("last_generated"),
                "avg_generation_time_seconds": stats.get("avg_generation_time_seconds", 0)
            }
        
        # Overall health check
        all_healthy = all(status_data[d]["healthy"] for d in degrees)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "background_generator_running": True,
            "overall_health": "healthy" if all_healthy else "needs-attention",
            "degrees": status_data,
            "api_version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"❌ Queue status error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get queue status: {str(e)}"
        )


@app.get("/api/backup-qa/stats", tags=["Backup Q&A"])
async def get_backup_qa_stats():
    """
    Get statistics about the backup Q&A database.
    
    **Returns:**
    Statistics for each degree including total questions, topics, and serve metrics
    """
    try:
        logger.info("📊 Fetching backup Q&A database statistics...")
        
        stats_data = {}
        degrees = ["Computer Science", "Electrical Engineering", "Mechanical Engineering"]
        
        for degree in degrees:
            stats = qa_database.get_stats(degree)
            topics = qa_database.get_all_topics(degree)
            stats_data[degree] = {
                "total_questions": stats['total_questions'],
                "unique_topics": stats['unique_topics'],
                "total_serves": stats['total_serves'],
                "avg_quality": stats['avg_quality'],
                "topics": topics
            }
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "degrees": stats_data,
            "total_backup_questions": sum(s['total_questions'] for s in stats_data.values()),
            "message": "Backup Q&A database provides instant content while generating fresh reels",
            "api_version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"❌ Backup Q&A stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get backup Q&A stats: {str(e)}"
        )


@app.get("/api/backup-qa/{degree}/{topic}", tags=["Backup Q&A"])
async def get_backup_qa_by_topic(degree: str, topic: str):
    """
    Get a specific Q&A pair from the backup database by topic.
    
    **Parameters:**
    - degree: Degree name
    - topic: Topic name
    
    **Returns:**
    Q&A pair with question, answer, analogy, hook, and examples
    """
    try:
        logger.info(f"🔍 Fetching backup Q&A for {degree}/{topic}")
        
        qa = qa_database.get_by_topic(degree, topic)
        
        if not qa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No backup Q&A found for {degree}/{topic}"
            )
        
        return {
            "status": "success",
            "qa": qa,
            "source": "backup-qa-database",
            "api_version": "1.0.0"
        }
    
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching backup Q&A: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch backup Q&A: {str(e)}"
        )


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
# Mount Static Files (Frontend) - MUST BE LAST
# ============================================================================

frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")
    logger.info(f"✅ Frontend mounted at / from {frontend_path}")

# ============================================================================
# For local testing
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
