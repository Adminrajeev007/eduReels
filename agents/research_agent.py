"""
Research Agent - Finds interesting topics in a field
Input: degree name
Output: 3 topics with explanations + recommended topic
"""

import json
import logging
from typing import Dict, Any, List
from tools.model_connector import get_model_connector
from tools.prompt_templates import format_research_prompt

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Finds trending and interesting topics in a field.
    Uses AI to research what topics would make good questions.
    """

    def __init__(self):
        self.model = get_model_connector("chatgpt")
        self.logger = logger

    async def run(self, degree: str) -> Dict[str, Any]:
        """
        Research interesting topics for a degree.

        Args:
            degree: The degree/branch name (e.g., "Computer Science")

        Returns:
            Dict with topics list and recommended_topic
        """
        try:
            self.logger.info(f"🔍 Research Agent starting for: {degree}")

            # Format prompt with degree
            prompt = format_research_prompt(degree)

            # Call AI model
            self.logger.info("📡 Calling AI model for topic research...")
            response = await self.model.generate(prompt)

            # Parse JSON response
            result = self._parse_response(response)

            if not result:
                self.logger.warning("❌ Failed to parse research results")
                return self._get_fallback_topics(degree)

            self.logger.info(f"✅ Research Agent found {len(result.get('topics', []))} topics")
            return result

        except Exception as e:
            self.logger.error(f"❌ Research Agent error: {str(e)}")
            return self._get_fallback_topics(degree)

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
                if "topics" in response and "recommended_topic" in response:
                    self.logger.info("✅ Successfully parsed research response (already dict)")
                    return response
                else:
                    self.logger.warning("⚠️ Dict response missing required fields")
                    return None
            
            # Try to extract JSON from response string
            # Sometimes models wrap JSON in markdown, so clean it
            json_str = response.strip()

            # Remove markdown code blocks if present
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]

            json_str = json_str.strip()

            # Parse JSON
            parsed = json.loads(json_str)

            # Validate structure
            if "topics" in parsed and "recommended_topic" in parsed:
                self.logger.info("✅ Successfully parsed research response")
                return parsed
            else:
                self.logger.warning("⚠️ Response missing required fields")
                return None

        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON parse error: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Parse error: {str(e)}")
            return None

    def _get_fallback_topics(self, degree: str) -> Dict[str, Any]:
        """
        Return fallback topics if AI model fails.
        These are generic intermediate-level topics.
        """
        fallback_map = {
            "computer science": {
                "topics": [
                    {
                        "name": "Memory Hierarchy",
                        "why_interesting": "Explains why your phone has both RAM and storage",
                        "difficulty": "intermediate",
                        "real_world_connection": "Phone/laptop storage speeds",
                    },
                    {
                        "name": "CPU Caching",
                        "why_interesting": "Makes processors fast but is hidden from users",
                        "difficulty": "intermediate",
                        "real_world_connection": "App and browser caching",
                    },
                    {
                        "name": "Virtual Memory",
                        "why_interesting": "Prevents laptop freeze when RAM is full",
                        "difficulty": "intermediate",
                        "real_world_connection": "Laptop performance with many apps",
                    },
                ],
                "recommended_topic": "Memory Hierarchy",
            },
            "electrical engineering": {
                "topics": [
                    {
                        "name": "Impedance Matching",
                        "why_interesting": "Why signal quality matters in circuits",
                        "difficulty": "intermediate",
                        "real_world_connection": "Phone chargers, HDMI cables",
                    },
                    {
                        "name": "Power Factor",
                        "why_interesting": "Why AC power isn't as simple as DC",
                        "difficulty": "intermediate",
                        "real_world_connection": "Electricity bills, device efficiency",
                    },
                    {
                        "name": "Feedback Control",
                        "why_interesting": "How systems stabilize themselves",
                        "difficulty": "intermediate",
                        "real_world_connection": "Thermostat, cruise control",
                    },
                ],
                "recommended_topic": "Impedance Matching",
            },
            "mechanical engineering": {
                "topics": [
                    {
                        "name": "Stress vs Strain",
                        "why_interesting": "Why materials break under load",
                        "difficulty": "intermediate",
                        "real_world_connection": "Bridge design, material selection",
                    },
                    {
                        "name": "Friction",
                        "why_interesting": "Both helpful and harmful in machines",
                        "difficulty": "intermediate",
                        "real_world_connection": "Car brakes, skateboard wheels",
                    },
                    {
                        "name": "Torque",
                        "why_interesting": "Why leverage matters in mechanical systems",
                        "difficulty": "intermediate",
                        "real_world_connection": "Wrench size, door hinges",
                    },
                ],
                "recommended_topic": "Stress vs Strain",
            },
        }

        degree_lower = degree.lower()
        if degree_lower in fallback_map:
            self.logger.info(f"⚠️ Using fallback topics for: {degree}")
            return fallback_map[degree_lower]
        else:
            # Generic fallback
            self.logger.info(f"⚠️ Using generic fallback topics for: {degree}")
            return {
                "topics": [
                    {
                        "name": "Fundamentals",
                        "why_interesting": "Core concepts everyone should know",
                        "difficulty": "intermediate",
                        "real_world_connection": "Daily applications",
                    },
                    {
                        "name": "Current Trends",
                        "why_interesting": "What's being discussed in industry",
                        "difficulty": "intermediate",
                        "real_world_connection": "Modern applications",
                    },
                    {
                        "name": "Common Challenges",
                        "why_interesting": "Problems professionals face",
                        "difficulty": "intermediate",
                        "real_world_connection": "Career relevance",
                    },
                ],
                "recommended_topic": "Fundamentals",
            }
