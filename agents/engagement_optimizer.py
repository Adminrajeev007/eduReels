"""
Engagement Optimizer Agent - Formats content for short-form video reels
Input: simplified answer + examples + topic
Output: compressed, engaging reel content optimized for short-form video
"""

import json
import logging
from typing import Dict, Any
from tools.model_connector import get_model_connector
from tools.prompt_templates import format_engagement_prompt

logger = logging.getLogger(__name__)


class EngagementOptimizerAgent:
    """
    Optimizes content for short-form video format (TikTok, YouTube Shorts, Reels).
    Compresses information, adds hooks, and maximizes engagement potential.
    """

    def __init__(self):
        self.model = get_model_connector("chatgpt")
        self.logger = logger

    async def run(
        self,
        simplified_answer: str,
        examples: str,
        topic: str,
        question: str = "",
        degree: str = "Computer Science"
    ) -> Dict[str, Any]:
        """
        Optimize content for short-form video engagement.

        Args:
            simplified_answer: Simplified plain-language answer
            examples: Real-world examples to include
            topic: Topic being discussed
            question: Original question (optional)
            degree: Degree/branch (optional)

        Returns:
            Dict with hook, compressed_content, transition_points, and engagement_tips
        """
        try:
            self.logger.info(f"🎬 Engagement Optimizer starting for: {topic}")

            # Format prompt with context
            prompt = format_engagement_prompt(
                question=question,
                answer=simplified_answer
            )

            # Call AI model
            self.logger.info("📡 Calling AI model to optimize engagement...")
            response = await self.model.generate(prompt)

            # Parse JSON response
            result = self._parse_response(response)

            if not result:
                self.logger.warning("❌ Failed to parse engagement optimization")
                return self._get_fallback_optimization(simplified_answer, topic)

            self.logger.info("✅ Engagement Optimizer successfully optimized content")
            return result

        except Exception as e:
            self.logger.error(f"❌ Engagement Optimizer error: {str(e)}")
            return self._get_fallback_optimization(simplified_answer, topic)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI model response to extract JSON.

        Args:
            response: Raw response from AI model (string or dict)

        Returns:
            Parsed JSON dict or None
        """
        try:
            # If already a dict, return it
            if isinstance(response, dict):
                if "hook" in response and "compressed_content" in response:
                    self.logger.info("✅ Successfully parsed optimization response (already dict)")
                    return response
                else:
                    self.logger.warning("⚠️ Dict response missing required fields")
                    return None

            # Try to extract JSON from response string
            if not isinstance(response, str):
                response = str(response)

            # Find JSON in response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                self.logger.warning("⚠️ No JSON found in response")
                return None

            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)

            self.logger.info("✅ Successfully parsed optimization response")
            return parsed

        except json.JSONDecodeError as e:
            self.logger.warning(f"⚠️ JSON parsing failed: {str(e)}")
            return None
        except Exception as e:
            self.logger.warning(f"⚠️ Parsing error: {str(e)}")
            return None

    def _get_fallback_optimization(self, simplified_answer: str, topic: str) -> Dict[str, Any]:
        """
        Return fallback optimized content if model fails.

        Args:
            simplified_answer: Simplified answer text
            topic: Topic name

        Returns:
            Fallback dict with optimized content
        """
        self.logger.info("📋 Using fallback engagement optimization")

        # Create compressed version (first sentence + key insight)
        compressed = simplified_answer.split(".")[0] + "."
        if len(compressed) > 100:
            compressed = compressed[:100] + "..."

        return {
            "hook": f"🤔 Did you know about {topic}?",
            "compressed_content": compressed,
            "transition_points": [
                {"text": "Here's the interesting part:", "position": "middle"},
                {"text": "And that's why it matters:", "position": "end"}
            ],
            "engagement_tips": [
                "Use quick cuts between explanations",
                "Show real examples on screen",
                "End with a thought-provoking question"
            ],
            "video_duration_seconds": 30,
            "platform_recommendations": ["instagram_reels", "tiktok", "youtube_shorts"],
            "engagement_score": 7.0
        }
