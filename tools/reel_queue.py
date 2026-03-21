"""
Reel Queue Manager - Pre-generates and manages reel queue for fast loading
Stores reels in database and serves them on-demand while continuously generating new ones
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import asyncio

logger = logging.getLogger(__name__)


class ReelQueueManager:
    """Manages pre-generated reel queue for fast delivery"""
    
    def __init__(self, db_path: str = "data/reel_queue.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reel_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    degree TEXT NOT NULL,
                    reel_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    served BOOLEAN DEFAULT 0,
                    served_at TIMESTAMP
                )
            """)
            
            # Create index for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_degree_served 
                ON reel_queue (degree, served)
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS queue_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    degree TEXT UNIQUE,
                    total_generated INTEGER DEFAULT 0,
                    total_served INTEGER DEFAULT 0,
                    last_generated TIMESTAMP,
                    avg_generation_time REAL DEFAULT 0,
                    queue_size INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            logger.info("✅ Reel Queue Database initialized")
    
    def add_reel(self, degree: str, reel_data: Dict[str, Any]) -> bool:
        """Add a pre-generated reel to the queue"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                reel_json = json.dumps(reel_data)
                conn.execute(
                    "INSERT INTO reel_queue (degree, reel_data) VALUES (?, ?)",
                    (degree, reel_json)
                )
                
                # Update stats
                conn.execute("""
                    INSERT INTO queue_stats (degree, total_generated, last_generated)
                    VALUES (?, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT(degree) DO UPDATE SET
                        total_generated = total_generated + 1,
                        last_generated = CURRENT_TIMESTAMP
                """, (degree,))
                
                conn.commit()
                logger.info(f"✅ Added reel to queue for {degree}")
                return True
        except Exception as e:
            logger.error(f"❌ Error adding reel to queue: {e}")
            return False
    
    def get_next_reel(self, degree: str) -> Optional[Dict[str, Any]]:
        """Get next available reel for degree and mark as served"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, reel_data FROM reel_queue
                    WHERE degree = ? AND served = 0
                    ORDER BY created_at ASC
                    LIMIT 1
                """, (degree,))
                
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"⚠️ No queued reels for {degree}")
                    return None
                
                reel_id, reel_json = row
                reel_data = json.loads(reel_json)
                
                # Mark as served
                conn.execute("""
                    UPDATE reel_queue
                    SET served = 1, served_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (reel_id,))
                
                # Update stats
                conn.execute("""
                    UPDATE queue_stats
                    SET total_served = total_served + 1
                    WHERE degree = ?
                """, (degree,))
                
                conn.commit()
                logger.info(f"✅ Served reel #{reel_id} for {degree}")
                return reel_data
        except Exception as e:
            logger.error(f"❌ Error getting reel: {e}")
            return None
    
    def get_queue_size(self, degree: str) -> int:
        """Get number of available reels in queue"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM reel_queue
                    WHERE degree = ? AND served = 0
                """, (degree,))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"❌ Error getting queue size: {e}")
            return 0
    
    def get_stats(self, degree: str) -> Dict[str, Any]:
        """Get queue statistics for a degree"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT total_generated, total_served, last_generated, avg_generation_time
                    FROM queue_stats
                    WHERE degree = ?
                """, (degree,))
                row = cursor.fetchone()
                
                if not row:
                    return {"total_generated": 0, "total_served": 0, "queue_size": 0}
                
                queue_size = self.get_queue_size(degree)
                return {
                    "total_generated": row[0],
                    "total_served": row[1],
                    "last_generated": row[2],
                    "avg_generation_time": row[3],
                    "queue_size": queue_size
                }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {}
    
    def cleanup_served_reels(self, days: int = 7):
        """Remove served reels older than N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    DELETE FROM reel_queue
                    WHERE served = 1
                    AND served_at < datetime('now', '-' || ? || ' days')
                """, (days,))
                deleted = conn.total_changes
                conn.commit()
                logger.info(f"🧹 Cleaned up {deleted} old reels")
        except Exception as e:
            logger.error(f"❌ Error cleaning up: {e}")
