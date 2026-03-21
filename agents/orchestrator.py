"""
Orchestrator Agent - Coordinates all other agents
Input: degree name
Output: Complete reel payload (question + metadata + optimized content)

This is the main brain that:
1. Checks cache
2. Runs Research Agent (finds topics)
3. Runs Question Generator (creates engaging question)
4. Runs Quality Checker (validates quality ≥7.0)
5. Handles regeneration if quality < 7
6. Runs Answer Generator (creates technical answer)
7. Runs Answer Simplifier (converts to plain language)
8. Runs Example Finder (adds real-world examples)
9. Runs Engagement Optimizer (formats for reels)
10. Caches result
11. Returns final package
"""

import logging
import time
from typing import Dict, Any
from datetime import datetime

from agents.research_agent import ResearchAgent
from agents.question_generator import QuestionGeneratorAgent
from agents.quality_checker import QualityCheckAgent
from agents.answer_simplifier import AnswerSimplifierAgent
from agents.example_finder import ExampleFinderAgent
from agents.engagement_optimizer import EngagementOptimizerAgent
from tools.model_connector import get_model_connector
from tools.cache_manager import CacheManager
from tools.prompt_templates import format_answer_generator_prompt

logger = logging.getLogger(__name__)


class EducationalReelsOrchestrator:
    """
    Master orchestrator that coordinates the entire question generation pipeline.
    Manages cache, agents, error handling, and regeneration.
    """

    def __init__(self, max_regeneration_attempts: int = 2):
        """
        Initialize orchestrator with all sub-agents.

        Args:
            max_regeneration_attempts: Max times to regenerate if quality fails
        """
        self.research_agent = ResearchAgent()
        self.question_generator = QuestionGeneratorAgent()
        self.quality_checker = QualityCheckAgent()
        self.answer_simplifier = AnswerSimplifierAgent()
        self.example_finder = ExampleFinderAgent()
        self.engagement_optimizer = EngagementOptimizerAgent()
        self.model = get_model_connector("groq")
        self.cache = CacheManager()
        self.max_regeneration_attempts = max_regeneration_attempts
        self.logger = logger

        self.logger.info("✅ Orchestrator initialized with all agents")

    async def generate_reel_content(self, degree: str, skip_cache: bool = False) -> Dict[str, Any]:
        """
        Main method: Generate complete reel content from degree input.

        Args:
            degree: Degree/branch name (e.g., "Computer Science")
            skip_cache: Force generation of new content, bypassing cache (default: False)

        Returns:
            Complete reel payload with question, answer, metadata
        """
        start_time = time.time()

        try:
            self.logger.info(f"🚀 Orchestrator: Starting reel generation for: {degree} (skip_cache={skip_cache})")

            # ================================================================
            # STEP 1: CHECK CACHE (unless skip_cache is True)
            # ================================================================
            if not skip_cache:
                self.logger.info("📦 Checking cache...")
                cached = self.cache.get(degree)
                if cached:
                    elapsed = time.time() - start_time
                    self.logger.info(f"✅ Cache HIT - returning in {elapsed:.2f}s")
                    return {
                        **cached, 
                        "cached": True, 
                        "generation_time": elapsed,
                        "status": "success"
                    }
            else:
                self.logger.info("⏭️  Skipping cache - forcing fresh generation")

            # ================================================================
            # STEP 2: RESEARCH - Find good topics
            # ================================================================
            self.logger.info("🔍 STEP 1: Research Agent - Finding topics...")
            research_result = await self.research_agent.run(degree)

            topic = research_result.get("recommended_topic", "General")
            research_context = research_result.get("topics", [{}])[0].get("why_interesting", "")

            self.logger.info(f"   ✅ Found topic: {topic}")

            # ================================================================
            # STEP 3: GENERATE - Create raw question
            # ================================================================
            self.logger.info("❓ STEP 2: Question Generator - Creating question...")
            question_result = await self.question_generator.run(degree, topic, research_context)

            raw_question = question_result.get("question", "")
            self.logger.info(f"   ✅ Generated: {raw_question[:60]}...")

            # ================================================================
            # STEP 4: QUALITY CHECK - Validate question
            # ================================================================
            self.logger.info("✅ STEP 3: Quality Check Agent - Validating...")
            quality_result = await self.quality_checker.run(degree, raw_question)

            quality_score = quality_result.get("quality_score", 0)
            passes = quality_result.get("pass", False)

            self.logger.info(f"   Score: {quality_score}/10 - {'PASS' if passes else 'FAIL'}")

            # ================================================================
            # STEP 5: REGENERATION LOOP - If quality fails
            # ================================================================
            regeneration_count = 0
            while not passes and regeneration_count < self.max_regeneration_attempts:
                regeneration_count += 1
                self.logger.info(
                    f"⚠️ Quality failed (score {quality_score}/10). "
                    f"Regenerating... (attempt {regeneration_count}/{self.max_regeneration_attempts})"
                )

                improvements = quality_result.get("suggested_improvements", "")
                self.logger.info(f"   Improvement hint: {improvements}")

                # Generate new question with improvements hint
                question_result = await self.question_generator.run(
                    degree, topic, f"{research_context} {improvements}"
                )
                raw_question = question_result.get("question", "")

                # Re-check quality
                quality_result = await self.quality_checker.run(degree, raw_question)
                quality_score = quality_result.get("quality_score", 0)
                passes = quality_result.get("pass", False)

                self.logger.info(f"   Attempt {regeneration_count}: Score {quality_score}/10 - {'PASS' if passes else 'FAIL'}")

            if not passes:
                self.logger.warning(f"❌ Quality check still failed after {regeneration_count} regenerations. Proceeding anyway.")

            # ================================================================
            # STEP 6: GENERATE ANSWER - Get technical answer
            # ================================================================
            self.logger.info("📝 Generating technical answer...")
            raw_answer = await self._generate_raw_answer(degree, raw_question)
            self.logger.info(f"   ✅ Answer generated ({len(raw_answer)} chars)")

            # ================================================================
            # STEP 7: SIMPLIFY ANSWER - Convert to plain language
            # ================================================================
            self.logger.info("🎓 STEP 5: Answer Simplifier - Converting to plain language...")
            simplify_result = await self.answer_simplifier.run(
                raw_answer, topic, degree, raw_question
            )
            simplified_answer = simplify_result.get(
                "simplified_answer", 
                raw_answer
            )
            analogy_used = simplify_result.get("analogy", "")
            self.logger.info(f"   ✅ Simplified: {simplified_answer[:60]}...")

            # ================================================================
            # STEP 8: FIND EXAMPLES - Add real-world examples
            # ================================================================
            self.logger.info("🔍 STEP 6: Example Finder - Finding real-world examples...")
            examples_result = await self.example_finder.run(
                topic, simplified_answer, degree, raw_question
            )
            primary_example = examples_result.get("primary_example", "")
            secondary_examples = examples_result.get("secondary_examples", [])
            self.logger.info(f"   ✅ Found example: {primary_example[:50]}...")

            # ================================================================
            # STEP 9: OPTIMIZE ENGAGEMENT - Format for reels
            # ================================================================
            self.logger.info("🎬 STEP 7: Engagement Optimizer - Optimizing for reels...")
            engagement_result = await self.engagement_optimizer.run(
                simplified_answer, 
                primary_example,
                topic, 
                raw_question, 
                degree
            )
            hook = engagement_result.get("hook", "")
            compressed_content = engagement_result.get("compressed_content", simplified_answer)
            engagement_tips = engagement_result.get("engagement_tips", [])
            video_duration = engagement_result.get("video_duration_seconds", 30)
            engagement_score = engagement_result.get("engagement_score", 0)
            self.logger.info(f"   ✅ Hook: {hook[:50]}...")

            # ================================================================
            # STEP 10: BUILD PAYLOAD - Create final reel package
            # ================================================================
            payload = {
                "degree": degree,
                "topic": topic,
                "reel_question": raw_question,
                "reel_answer": raw_answer,
                "simplified_answer": simplified_answer,
                "analogy": analogy_used,
                "primary_example": primary_example,
                "secondary_examples": secondary_examples,
                "hook": hook,
                "compressed_content": compressed_content,
                "engagement_tips": engagement_tips,
                "video_duration_seconds": video_duration,
                "engagement_score": engagement_score,
                "quality_score": quality_score,
                "research_context": research_context,
                "model_used": "chatgpt",
                "regeneration_attempts": regeneration_count,
                "timestamp": datetime.now().isoformat(),
            }

            # ================================================================
            # STEP 11: CACHE - Save for next time
            # ================================================================
            self.logger.info("💾 Caching result...")
            self.cache.save(degree, topic, payload, quality_score, "chatgpt")

            # ================================================================
            # STEP 12: RETURN - Complete package
            # ================================================================
            elapsed = time.time() - start_time

            result = {
                **payload,
                "cached": False,
                "generation_time": elapsed,
                "status": "success",
            }

            self.logger.info(f"✅ Orchestrator complete in {elapsed:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"❌ Orchestrator error: {str(e)}")
            elapsed = time.time() - start_time
            return self._get_fallback_payload(degree, elapsed)

    async def _generate_raw_answer(self, degree: str, question: str) -> str:
        """
        Generate a technical answer to the question.

        Args:
            degree: The degree name
            question: The question to answer

        Returns:
            Technical answer text
        """
        try:
            prompt = format_answer_generator_prompt(degree, question)
            answer = await self.model.generate(prompt)
            
            # Handle both string and dict responses
            if isinstance(answer, dict):
                answer = answer.get("answer", str(answer))
            
            return answer.strip() if isinstance(answer, str) else str(answer)
        except Exception as e:
            self.logger.error(f"❌ Answer generation error: {str(e)}")
            return "Unable to generate answer at this time."

    def _get_fallback_payload(self, degree: str, elapsed_time: float) -> Dict[str, Any]:
        """
        Return fallback payload if generation fails completely.

        Args:
            degree: The degree name
            elapsed_time: Time spent before failure

        Returns:
            Fallback reel payload
        """
        self.logger.info("⚠️ Returning fallback payload")

        return {
            "degree": degree,
            "topic": "General",
            "reel_question": "What are some key concepts in this field?",
            "reel_answer": "Please try again. Our system encountered an error.",
            "quality_score": 0,
            "model_used": "fallback",
            "cached": False,
            "generation_time": elapsed_time,
            "status": "error",
            "error": "Generation failed - all models unavailable",
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()

    def clear_cache(self) -> bool:
        """Clear all cache"""
        return self.cache.clear_all()
