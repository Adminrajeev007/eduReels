"""
Question Generator Agent - Creates engaging questions from topics
Input: degree + topic + research context
Output: Engaging question (NOT "What is..." style)
"""

import json
import logging
from typing import Dict, Any
from tools.model_connector import get_model_connector
from tools.prompt_templates import format_question_generator_prompt

logger = logging.getLogger(__name__)


class QuestionGeneratorAgent:
    """
    Generates engaging questions that make students think.
    Enforces patterns like "Why", "How", "What if" instead of "What is".
    """

    def __init__(self):
        self.model = get_model_connector("chatgpt")
        self.logger = logger

    async def run(self, degree: str, topic: str, research_context: str = "") -> Dict[str, Any]:
        """
        Generate an engaging question from a topic.

        Args:
            degree: The degree/branch name
            topic: The topic to create a question about
            research_context: Context about why this topic is interesting

        Returns:
            Dict with question, thinking_process, expected_difficulty
        """
        try:
            self.logger.info(f"❓ Question Generator starting for: {degree} / {topic}")

            # Format prompt
            prompt = format_question_generator_prompt(degree, topic, research_context)

            # Call AI model
            self.logger.info("📡 Calling AI model to generate question...")
            response = await self.model.generate(prompt)

            # Parse JSON response
            result = self._parse_response(response)

            if not result:
                self.logger.warning("❌ Failed to parse question response")
                return self._get_fallback_question(degree, topic)

            # Validate question isn't "What is..." style
            if self._is_bad_question(result.get("question", "")):
                self.logger.warning("⚠️ Generated question is too basic, regenerating...")
                # In production, would retry with different prompt
                return self._get_fallback_question(degree, topic)

            self.logger.info(f"✅ Question Generator created: {result['question'][:60]}...")
            return result

        except Exception as e:
            self.logger.error(f"❌ Question Generator error: {str(e)}")
            return self._get_fallback_question(degree, topic)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse AI model response to extract JSON.

        Args:
            response: Raw response from AI model (string or dict)

        Returns:
            Parsed JSON dict or None
        """
        try:
            # If already a dict, validate and return
            if isinstance(response, dict):
                if "question" in response and "thinking_process" in response:
                    self.logger.info("✅ Successfully parsed question response (already dict)")
                    return response
                else:
                    self.logger.warning("⚠️ Dict response missing required fields")
                    return None
            
            # Clean response string
            json_str = response.strip()

            # Remove markdown code blocks
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
            if "question" in parsed and "thinking_process" in parsed:
                self.logger.info("✅ Successfully parsed question response")
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

    def _is_bad_question(self, question: str) -> bool:
        """
        Check if question follows bad patterns.

        Args:
            question: The question to validate

        Returns:
            True if question is bad (too basic)
        """
        bad_patterns = [
            "what is",
            "define ",
            "list the",
            "explain ",
            "describe how",
        ]

        question_lower = question.lower()
        for pattern in bad_patterns:
            if question_lower.startswith(pattern):
                self.logger.warning(f"⚠️ Question starts with bad pattern: {pattern}")
                return True

        return False

    def _get_fallback_question(self, degree: str, topic: str) -> Dict[str, Any]:
        """
        Return fallback question if generation fails.
        """
        self.logger.info(f"⚠️ Using fallback question for: {degree} / {topic}")

        return {
            "question": f"Why is {topic} important in {degree}?",
            "thinking_process": "Fallback question generated due to model error",
            "expected_difficulty": "intermediate",
        }
