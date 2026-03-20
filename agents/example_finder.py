"""
Example Finder Agent - Finds real-world examples for answers
Input: topic + answer + degree
Output: relevant real-world examples that illustrate the concept
"""

import json
import logging
from typing import Dict, Any, List
from tools.model_connector import get_model_connector
from tools.prompt_templates import format_example_finder_prompt

logger = logging.getLogger(__name__)


class ExampleFinderAgent:
    """
    Finds relevant real-world examples that illustrate a concept.
    Makes abstract ideas concrete and relatable to students.
    """

    def __init__(self):
        self.model = get_model_connector("chatgpt")
        self.logger = logger

    async def run(
        self, 
        topic: str, 
        answer: str, 
        degree: str,
        question: str = ""
    ) -> Dict[str, Any]:
        """
        Find real-world examples for a topic.

        Args:
            topic: The topic being discussed
            answer: The answer/explanation provided
            degree: The degree/branch (e.g., "Computer Science")
            question: Original question (optional context)

        Returns:
            Dict with primary_example, secondary_examples, and why_these_work
        """
        try:
            self.logger.info(f"🔍 Example Finder starting for topic: {topic}")

            # Format prompt with context
            prompt = format_example_finder_prompt(
                topic=topic,
                simple_answer=answer
            )

            # Call AI model
            self.logger.info("📡 Calling AI model to find examples...")
            response = await self.model.generate(prompt)

            # Parse JSON response
            result = self._parse_response(response)

            if not result:
                self.logger.warning("❌ Failed to parse examples")
                return self._get_fallback_examples(topic, degree)

            self.logger.info(f"✅ Example Finder found {len(result.get('secondary_examples', []))} examples")
            return result

        except Exception as e:
            self.logger.error(f"❌ Example Finder error: {str(e)}")
            return self._get_fallback_examples(topic, degree)

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
                if "primary_example" in response and "secondary_examples" in response:
                    self.logger.info("✅ Successfully parsed examples response (already dict)")
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

            self.logger.info("✅ Successfully parsed examples response")
            return parsed

        except json.JSONDecodeError as e:
            self.logger.warning(f"⚠️ JSON parsing failed: {str(e)}")
            return None
        except Exception as e:
            self.logger.warning(f"⚠️ Parsing error: {str(e)}")
            return None

    def _get_fallback_examples(self, topic: str, degree: str) -> Dict[str, Any]:
        """
        Return fallback examples if model fails.

        Args:
            topic: Topic name
            degree: Degree/branch

        Returns:
            Fallback dict with examples
        """
        self.logger.info("📋 Using fallback examples")

        # Branch-specific fallback examples
        fallback_map = {
            "Computer Science": {
                "primary": "Your smartphone running multiple apps at once (demonstrates multitasking)",
                "secondary": [
                    "A web browser with multiple tabs (thread management)",
                    "Your laptop's task manager showing running processes",
                    "Download queue in a torrent app"
                ]
            },
            "Electrical Engineering": {
                "primary": "How your phone charger converts wall power to safe charging (demonstrates power conversion)",
                "secondary": [
                    "LED lights in your room (semiconductors and light)",
                    "Wireless charging on your phone (electromagnetic principles)",
                    "Your home circuit breaker (protection systems)"
                ]
            },
            "Mechanical Engineering": {
                "primary": "Shock absorbers in your car suspension (demonstrates force distribution)",
                "secondary": [
                    "Door hinges rotating smoothly (mechanical advantage)",
                    "Pulley system in elevators (load distribution)",
                    "Gears in car transmission (power transfer)"
                ]
            }
        }

        examples = fallback_map.get(degree, fallback_map["Computer Science"])

        return {
            "primary_example": examples['primary'],
            "secondary_examples": examples["secondary"],
            "why_these_work": "These are everyday items that demonstrate the concept",
            "relevance_score": 0.7,
            "engagement_potential": "high"
        }
