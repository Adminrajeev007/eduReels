"""
Cache Manager - SQLite-based caching for generated questions
Stores and retrieves questions to avoid redundant API calls
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class CacheManager:
    """
    Manages caching of generated questions using SQLite.
    Cache TTL is configurable (default 7 days).
    """

    def __init__(self, db_path: str = None, ttl_days: int = 7):
        self.db_path = db_path or os.getenv("CACHE_DB_PATH", "data/question_cache.db")
        self.ttl_days = ttl_days
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with cache table"""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS question_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    degree TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    quality_score REAL NOT NULL,
                    payload JSON NOT NULL,
                    model_used TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_count INTEGER DEFAULT 0,
                    last_accessed_at TIMESTAMP,
                    UNIQUE(degree, topic)
                )
            """
            )
            conn.commit()

    def get(self, degree: str, topic: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached question if it exists and not expired.

        Args:
            degree: The degree/branch name
            topic: Optional specific topic to search for

        Returns:
            Cached payload or None if not found/expired
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if topic:
                    cursor.execute(
                        """
                        SELECT payload, created_at, accessed_count FROM question_cache
                        WHERE degree = ? AND topic = ? AND created_at > datetime('now', '-' || ? || ' days')
                    """,
                        (degree, topic, self.ttl_days),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT payload, created_at, accessed_count FROM question_cache
                        WHERE degree = ? AND created_at > datetime('now', '-' || ? || ' days')
                        ORDER BY last_accessed_at DESC LIMIT 1
                    """,
                        (degree, self.ttl_days),
                    )

                row = cursor.fetchone()
                if row:
                    payload_str, created_at, access_count = row
                    # Update accessed count and timestamp
                    cursor.execute(
                        """
                        UPDATE question_cache
                        SET accessed_count = ?, last_accessed_at = CURRENT_TIMESTAMP
                        WHERE degree = ? AND topic = ?
                    """,
                        (access_count + 1, degree, topic or ""),
                    )
                    conn.commit()

                    print(f"✅ Cache HIT for degree: {degree}")
                    return json.loads(payload_str)
                else:
                    print(f"❌ Cache MISS for degree: {degree}")
                    return None

        except Exception as e:
            print(f"⚠️ Cache retrieval error: {str(e)}")
            return None

    def save(self, degree: str, topic: str, payload: Dict[str, Any], quality_score: float, model_used: str = "chatgpt") -> bool:
        """
        Save generated question to cache.

        Args:
            degree: The degree/branch name
            topic: The topic used for generation
            payload: The complete generated reel payload
            quality_score: Quality score of the generated question
            model_used: Which model was used

        Returns:
            True if save successful, False otherwise
        """
        try:
            question = payload.get("reel_question", "")
            answer = payload.get("reel_answer", "")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO question_cache
                    (degree, topic, question, answer, quality_score, payload, model_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        degree,
                        topic,
                        question,
                        answer,
                        quality_score,
                        json.dumps(payload),
                        model_used,
                    ),
                )
                conn.commit()

            print(f"✅ Cached: {degree} / {topic}")
            return True

        except Exception as e:
            print(f"⚠️ Cache save error: {str(e)}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Total entries
                cursor.execute("SELECT COUNT(*) FROM question_cache")
                total_entries = cursor.fetchone()[0]

                # Cache hits (accessed_count > 0)
                cursor.execute("SELECT COUNT(*) FROM question_cache WHERE accessed_count > 0")
                cache_hits = cursor.fetchone()[0]

                # Average quality
                cursor.execute("SELECT AVG(quality_score) FROM question_cache WHERE quality_score > 0")
                avg_quality = cursor.fetchone()[0] or 0

                # Most cached degrees
                cursor.execute(
                    "SELECT degree, COUNT(*) as count FROM question_cache GROUP BY degree ORDER BY count DESC LIMIT 5"
                )
                top_degrees = cursor.fetchall()

                return {
                    "total_entries": total_entries,
                    "cache_hits": cache_hits,
                    "avg_quality_score": round(avg_quality, 2),
                    "cache_hit_rate": round((cache_hits / total_entries * 100) if total_entries > 0 else 0, 2),
                    "top_degrees": [{"degree": d, "count": c} for d, c in top_degrees],
                }

        except Exception as e:
            print(f"⚠️ Stats retrieval error: {str(e)}")
            return {}

    def clear_expired(self) -> int:
        """Remove expired cache entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    DELETE FROM question_cache
                    WHERE created_at < datetime('now', '-' || ? || ' days')
                """,
                    (self.ttl_days,),
                )
                conn.commit()
                return cursor.rowcount

        except Exception as e:
            print(f"⚠️ Cache cleanup error: {str(e)}")
            return 0

    def clear_all(self) -> bool:
        """Clear all cache (use with caution)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM question_cache")
                conn.commit()
            print("✅ Cache cleared")
            return True
        except Exception as e:
            print(f"⚠️ Cache clear error: {str(e)}")
            return False
