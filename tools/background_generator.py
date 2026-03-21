"""
Background Reel Generator - Continuously generates and queues reels
Runs as a background task to pre-fill the reel queue
"""

import asyncio
import logging
import time
from typing import List
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator import EducationalReelsOrchestrator
from tools.reel_queue import ReelQueueManager

logger = logging.getLogger(__name__)


class BackgroundReelGenerator:
    """Generates reels in background and adds to queue"""
    
    def __init__(
        self,
        orchestrator: EducationalReelsOrchestrator,
        queue_manager: ReelQueueManager,
        target_queue_size: int = 5,
        degrees: List[str] = None,
    ):
        """
        Initialize background generator
        
        Args:
            orchestrator: The EducationalReelsOrchestrator instance
            queue_manager: The ReelQueueManager instance
            target_queue_size: Target number of reels to keep queued per degree
            degrees: List of degrees to generate reels for
        """
        self.orchestrator = orchestrator
        self.queue = queue_manager
        self.target_queue_size = target_queue_size
        self.degrees = degrees or [
            "Computer Science",
            "Electrical Engineering",
            "Mechanical Engineering"
        ]
        self.is_running = False
        self.logger = logger
    
    async def start(self):
        """Start background generation loop"""
        self.is_running = True
        self.logger.info("🚀 Starting Background Reel Generator...")
        
        try:
            await self._generation_loop()
        except Exception as e:
            self.logger.error(f"❌ Error in generation loop: {e}")
            self.is_running = False
    
    async def stop(self):
        """Stop background generation"""
        self.is_running = False
        self.logger.info("⏹️ Stopped Background Reel Generator")
    
    async def _generation_loop(self):
        """Main generation loop - continuously generates reels"""
        while self.is_running:
            try:
                for degree in self.degrees:
                    # Check queue size
                    queue_size = self.queue.get_queue_size(degree)
                    
                    # Generate if below target
                    if queue_size < self.target_queue_size:
                        reels_to_generate = self.target_queue_size - queue_size
                        
                        for i in range(reels_to_generate):
                            try:
                                start_time = time.time()
                                
                                self.logger.info(
                                    f"📺 Generating reel for {degree} "
                                    f"(queue: {queue_size + i}/{self.target_queue_size})"
                                )
                                
                                # Generate reel
                                result = await self.orchestrator.generate_reel_content(
                                    degree, skip_cache=True
                                )
                                
                                # Create reel format
                                reel = {
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
                                }
                                
                                # Add to queue
                                self.queue.add_reel(degree, reel)
                                
                                generation_time = time.time() - start_time
                                self.logger.info(
                                    f"✅ Generated in {generation_time:.1f}s - "
                                    f"Queue size: {queue_size + i + 1}"
                                )
                                
                                # Small delay between generations
                                await asyncio.sleep(0.5)
                                
                            except Exception as e:
                                self.logger.error(f"⚠️ Failed to generate reel: {e}")
                                await asyncio.sleep(2)
                
                # Check all degrees once, then wait
                self.logger.debug("📊 Queue check complete, waiting...")
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Error in generation loop: {e}")
                await asyncio.sleep(5)
    
    def get_status(self) -> dict:
        """Get current status of generator"""
        status = {
            "is_running": self.is_running,
            "target_queue_size": self.target_queue_size,
            "degrees": {}
        }
        
        for degree in self.degrees:
            status["degrees"][degree] = self.queue.get_stats(degree)
        
        return status
