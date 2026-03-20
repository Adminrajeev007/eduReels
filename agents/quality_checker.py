"""
Quality Check Agent - Validates question quality
Input: degree + question
Output: quality_score (0-10), pass/fail, improvement suggestions
"""

import json
import logging
from typing import Dict, Any
from tools.model_connector import get_model_connector
from tools.prompt_templates import format_quality_check_prompt

logger = logging.getLogger(__name__)


class QualityCheckAgent:
    """
    Validates question quality on scale 1-10.
    Rejects questions with score < 7.
    Suggests improvements for borderline questions.
    """

    def __init__(self, quality_threshold: float = 7.0):
        self.model = get_model_connector("chatgpt")
        self.logger = logger
        self.quality_threshold = quality_threshold

    async def run(self, degree: str, question: str) -> Dict[str, Any]:
        """
        Check quality of a generated question.

        Args:
            degree: The degree/branch name
            question: The question to validate

        Returns:
            Dict with quality_score, pass/fail, issues, improvements
        """
        try:
            self.logger.info(f"✅ Quality Check Agent evaluating: {question[:50]}...")

            # Format prompt
            prompt = format_quality_check_prompt(degree, question)

            # Call AI model
            self.logger.info("📡 Calling AI model for quality evaluation...")
            response = await self.model.generate(prompt)

            # Parse response
            result = self._parse_response(response)

            if not result:
                self.logger.warning("❌ Failed to parse quality check response")
                return self._get_fallback_quality_check(question)

            # Check threshold
            quality_score = result.get("quality_score", 0)
            passes = quality_score >= self.quality_threshold

            self.logger.info(f"✅ Quality Check Result: {quality_score}/10 - {'PASS' if passes else 'FAIL'}")
            return result

        except Exception as e:
            self.logger.error(f"❌ Quality Check Agent error: {str(e)}")
            return self._get_fallback_quality_check(question)

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
                if "quality_score" in response and "pass" in response:
                    self.logger.info("✅ Successfully parsed quality response (already dict)")
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
            if "quality_score" in parsed and "pass" in parsed:
                # Ensure pass field is correct based on score
                quality_score = parsed.get("quality_score", 0)
                parsed["pass"] = quality_score >= self.quality_threshold

                self.logger.info("✅ Successfully parsed quality check response")
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

    def _get_fallback_quality_check(self, question: str) -> Dict[str, Any]:
        """
        Return fallback quality check if evaluation fails.
        Uses heuristic scoring.
        """
        self.logger.info("⚠️ Using fallback quality check")

        # Heuristic: If question starts with "Why" or "How", likely good
        score = 6.0  # Default to borderline

        if question.lower().startswith(("why", "how", "what if", "compare")):
            score = 8.0

        if question.lower().startswith(("what is", "define", "list", "explain")):
            score = 4.0

        return {
            "quality_score": score,
            "pass": score >= self.quality_threshold,
            "issues": (
                ["Question uses generic 'what is' format"]
                if score < self.quality_threshold
                else []
            ),
            "suggested_improvements": (
                "Rephrase using 'Why', 'How', or 'What if' format"
                if score < self.quality_threshold
                else "Question looks good"
            ),
            "reasoning": "Fallback heuristic scoring applied",
        }
