"""
Answer Simplifier Agent - Converts technical answers into plain language
Input: technical answer + topic + degree
Output: simplified answer with relatable analogies
"""

import json
import logging
from typing import Dict, Any
from tools.model_connector import get_model_connector
from tools.prompt_templates import format_simplifier_prompt

logger = logging.getLogger(__name__)


class AnswerSimplifierAgent:
    """
    Converts complex technical answers into plain language that students can understand.
    Uses analogies and relatable examples to make concepts stick.
    """

    def __init__(self):
        self.model = get_model_connector("chatgpt")
        self.logger = logger

    async def run(
        self, 
        technical_answer: str, 
        topic: str, 
        degree: str,
        question: str = ""
    ) -> Dict[str, Any]:
        """
        Simplify a technical answer into plain language.

        Args:
            technical_answer: Complex technical answer to simplify
            topic: The topic being discussed
            degree: The degree/branch (e.g., "Computer Science")
            question: Original question (optional context)

        Returns:
            Dict with simplified_answer, analogy, and key_insight
        """
        try:
            self.logger.info(f"📚 Answer Simplifier starting for topic: {topic}")

            # Format prompt with context
            prompt = format_simplifier_prompt(
                question=question,
                technical_answer=technical_answer
            )

            # Call AI model
            self.logger.info("📡 Calling AI model to simplify answer...")
            response = await self.model.generate(prompt)

            # Parse JSON response
            result = self._parse_response(response)

            if not result:
                self.logger.warning("❌ Failed to parse simplified answer")
                return self._get_fallback_answer(technical_answer, topic)

            self.logger.info("✅ Answer Simplifier successfully simplified the answer")
            return result

        except Exception as e:
            self.logger.error(f"❌ Answer Simplifier error: {str(e)}")
            return self._get_fallback_answer(technical_answer, topic)

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
                if "simplified_answer" in response and "analogy" in response:
                    self.logger.info("✅ Successfully parsed simplifier response (already dict)")
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

            self.logger.info("✅ Successfully parsed simplifier response")
            return parsed

        except json.JSONDecodeError as e:
            self.logger.warning(f"⚠️ JSON parsing failed: {str(e)}")
            return None
        except Exception as e:
            self.logger.warning(f"⚠️ Parsing error: {str(e)}")
            return None

    def _get_fallback_answer(self, technical_answer: str, topic: str) -> Dict[str, Any]:
        """
        Return fallback simplified answer if model fails.

        Args:
            technical_answer: Original technical answer
            topic: Topic name

        Returns:
            Fallback dict with simplified answer and analogy
        """
        self.logger.info("📋 Using fallback simplified answer")

        # Create a simple fallback by taking first 2-3 sentences
        sentences = technical_answer.split(".")
        simplified = ". ".join(sentences[:2]).strip() + "."

        return {
            "simplified_answer": simplified if simplified else f"Understanding {topic}: {technical_answer[:80]}.",
            "analogy": f"Think of {topic} like a familiar everyday concept you use.",
            "key_insight": f"The main idea: {topic} is important because it affects how things work.",
            "difficulty_level": "beginner",
            "confidence_score": 0.6
        }
