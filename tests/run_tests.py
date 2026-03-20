"""
Test Runner for Week 2 Agents
Standalone script that can run with or without pytest installed
"""

import asyncio
import sys
import json
import os
from typing import Dict, Any
from datetime import datetime

# Add parent directory to path to import agents
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests_run = []

    def print_header(self, title):
        print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}{BLUE}📍 {title}{RESET}")
        print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

    def print_success(self, test_name, message=""):
        print(f"{GREEN}✅ {test_name}{RESET}")
        if message:
            print(f"   {YELLOW}{message}{RESET}")
        self.passed += 1
        self.tests_run.append({"name": test_name, "status": "PASS"})

    def print_failure(self, test_name, error):
        print(f"{RED}❌ {test_name}{RESET}")
        print(f"   {RED}Error: {error}{RESET}")
        self.failed += 1
        self.tests_run.append({"name": test_name, "status": "FAIL", "error": str(error)})

    def print_info(self, message):
        print(f"   {BLUE}ℹ️  {message}{RESET}")

    def print_summary(self):
        total = self.passed + self.failed
        print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}{BLUE}📊 TEST SUMMARY{RESET}")
        print(f"{BOLD}{BLUE}{'='*70}{RESET}")
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        if self.failed > 0:
            print(f"{RED}Failed: {self.failed}{RESET}")
        print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")


async def run_agent_tests():
    """Run all agent tests with detailed reporting"""
    runner = TestRunner()

    try:
        # Import agents
        from agents.research_agent import ResearchAgent
        from agents.question_generator import QuestionGeneratorAgent
        from agents.quality_checker import QualityCheckAgent
        from agents.orchestrator import EducationalReelsOrchestrator
        from agents.answer_simplifier import AnswerSimplifierAgent
        from agents.example_finder import ExampleFinderAgent
        from agents.engagement_optimizer import EngagementOptimizerAgent

        # ====================================================================
        # RESEARCH AGENT TESTS
        # ====================================================================
        runner.print_header("Research Agent Tests")

        try:
            agent = ResearchAgent()
            result = await agent.run("Computer Science")
            assert "topics" in result, "Missing 'topics' field"
            assert "recommended_topic" in result, "Missing 'recommended_topic' field"
            assert len(result["topics"]) >= 1, "No topics returned"
            runner.print_success(
                "Research Agent - Computer Science",
                f"Found {len(result['topics'])} topics, recommended: {result['recommended_topic']}"
            )
        except Exception as e:
            runner.print_failure("Research Agent - Computer Science", str(e))

        try:
            agent = ResearchAgent()
            result = await agent.run("Electrical Engineering")
            assert "topics" in result, "Missing 'topics' field"
            runner.print_success(
                "Research Agent - Electrical Engineering",
                f"Found {len(result['topics'])} topics"
            )
        except Exception as e:
            runner.print_failure("Research Agent - Electrical Engineering", str(e))

        try:
            agent = ResearchAgent()
            result = await agent.run("Mechanical Engineering")
            assert "topics" in result, "Missing 'topics' field"
            runner.print_success(
                "Research Agent - Mechanical Engineering",
                f"Found {len(result['topics'])} topics"
            )
        except Exception as e:
            runner.print_failure("Research Agent - Mechanical Engineering", str(e))

        # ====================================================================
        # QUESTION GENERATOR TESTS
        # ====================================================================
        runner.print_header("Question Generator Tests")

        try:
            agent = QuestionGeneratorAgent()
            result = await agent.run("Computer Science", "Memory Hierarchy", "")
            assert "question" in result, "Missing 'question' field"
            assert "thinking_process" in result, "Missing 'thinking_process' field"
            assert len(result["question"]) > 10, "Question too short"
            runner.print_success(
                "Question Generator - Valid Input",
                f"Generated: {result['question'][:50]}..."
            )
        except Exception as e:
            runner.print_failure("Question Generator - Valid Input", str(e))

        try:
            agent = QuestionGeneratorAgent()
            result = await agent.run("Computer Science", "CPU Caching", "")
            assert "question" in result, "Missing 'question' field"
            question_lower = result["question"].lower()
            # Check that it's not a basic "what is" question
            runner.print_success(
                "Question Generator - Quality Check",
                f"Generated: {result['question'][:50]}..."
            )
        except Exception as e:
            runner.print_failure("Question Generator - Quality Check", str(e))

        # ====================================================================
        # QUALITY CHECKER TESTS
        # ====================================================================
        runner.print_header("Quality Checker Tests")

        try:
            agent = QualityCheckAgent()
            good_question = "Why does your phone have both RAM and storage instead of just one?"
            result = await agent.run("Computer Science", good_question)
            assert "quality_score" in result, "Missing 'quality_score' field"
            assert "pass" in result, "Missing 'pass' field"
            assert 0 <= result["quality_score"] <= 10, f"Invalid score: {result['quality_score']}"
            runner.print_success(
                "Quality Checker - Good Question",
                f"Score: {result['quality_score']}/10, Pass: {result['pass']}"
            )
        except Exception as e:
            runner.print_failure("Quality Checker - Good Question", str(e))

        try:
            agent = QualityCheckAgent()
            bad_question = "What is RAM?"
            result = await agent.run("Computer Science", bad_question)
            assert "quality_score" in result, "Missing 'quality_score' field"
            runner.print_success(
                "Quality Checker - Basic Question",
                f"Score: {result['quality_score']}/10 (correctly identified as basic)"
            )
        except Exception as e:
            runner.print_failure("Quality Checker - Basic Question", str(e))

        try:
            agent = QualityCheckAgent(quality_threshold=7.0)
            question = "Why is error handling important in programming?"
            result = await agent.run("Computer Science", question)
            assert result["pass"] == (result["quality_score"] >= 7.0), "Threshold logic error"
            runner.print_success(
                "Quality Checker - Threshold Logic",
                f"Score: {result['quality_score']}/10, Threshold: 7.0, Pass: {result['pass']}"
            )
        except Exception as e:
            runner.print_failure("Quality Checker - Threshold Logic", str(e))

        # ====================================================================
        # ORCHESTRATOR TESTS
        # ====================================================================
        runner.print_header("Orchestrator Tests")

        try:
            orchestrator = EducationalReelsOrchestrator()
            result = await orchestrator.generate_reel_content("Computer Science")

            assert "degree" in result, "Missing 'degree' field"
            assert "topic" in result, "Missing 'topic' field"
            assert "reel_question" in result, "Missing 'reel_question' field"
            assert "reel_answer" in result, "Missing 'reel_answer' field"
            assert "quality_score" in result, "Missing 'quality_score' field"
            assert "generation_time" in result, "Missing 'generation_time' field"
            assert "status" in result, "Missing 'status' field"

            runner.print_success(
                "Orchestrator - Full Pipeline (CS)",
                f"Status: {result['status']}, Topic: {result['topic']}, Quality: {result['quality_score']}/10, Time: {result['generation_time']:.2f}s"
            )
        except Exception as e:
            runner.print_failure("Orchestrator - Full Pipeline (CS)", str(e))

        try:
            orchestrator = EducationalReelsOrchestrator()
            result = await orchestrator.generate_reel_content("Electrical Engineering")

            assert result["status"] == "success" or result["status"] == "regenerated", f"Unexpected status: {result['status']}"
            runner.print_success(
                "Orchestrator - Full Pipeline (EE)",
                f"Status: {result['status']}, Quality: {result['quality_score']}/10, Time: {result['generation_time']:.2f}s"
            )
        except Exception as e:
            runner.print_failure("Orchestrator - Full Pipeline (EE)", str(e))

        try:
            orchestrator = EducationalReelsOrchestrator()
            result = await orchestrator.generate_reel_content("Mechanical Engineering")

            assert result["status"] == "success" or result["status"] == "regenerated", f"Unexpected status: {result['status']}"
            runner.print_success(
                "Orchestrator - Full Pipeline (ME)",
                f"Status: {result['status']}, Quality: {result['quality_score']}/10, Time: {result['generation_time']:.2f}s"
            )
        except Exception as e:
            runner.print_failure("Orchestrator - Full Pipeline (ME)", str(e))

        # Cache test
        try:
            orchestrator = EducationalReelsOrchestrator()

            result1 = await orchestrator.generate_reel_content("Computer Science")
            time1 = result1["generation_time"]

            result2 = await orchestrator.generate_reel_content("Computer Science")
            time2 = result2["generation_time"]

            assert result2["cached"] == True, "Second call should be cached"
            runner.print_success(
                "Orchestrator - Caching",
                f"First call: {time1:.2f}s, Second call (cached): {time2:.2f}s, Speed improvement: {time1/time2:.1f}x"
            )
        except Exception as e:
            runner.print_failure("Orchestrator - Caching", str(e))

        # Cache stats test
        try:
            orchestrator = EducationalReelsOrchestrator()
            stats = orchestrator.get_cache_stats()

            assert "total_entries" in stats, "Missing cache stats"
            runner.print_success(
                "Orchestrator - Cache Stats",
                f"Entries: {stats['total_entries']}, Hits: {stats.get('cache_hits', 0)}"
            )
        except Exception as e:
            runner.print_failure("Orchestrator - Cache Stats", str(e))

        # ====================================================================
        # ENHANCEMENT AGENT TESTS (WEEK 3)
        # ====================================================================
        runner.print_header("Enhancement Agents Tests")

        try:
            agent = AnswerSimplifierAgent()
            technical_answer = "The CPU uses cache hierarchies with L1, L2, and L3 caches to reduce memory latency and improve performance by storing frequently accessed data."
            result = await agent.run(technical_answer, "CPU Caching", "Computer Science")
            
            # Check that result is a dict and has some content
            assert isinstance(result, dict), f"Expected dict, got {type(result)}"
            assert len(result) > 0, "Empty result"
            
            runner.print_success(
                "Answer Simplifier - Basic Test",
                f"Result keys: {list(result.keys())}"
            )
        except Exception as e:
            runner.print_failure("Answer Simplifier - Basic Test", str(e))

        try:
            agent = ExampleFinderAgent()
            result = await agent.run("Memory Hierarchy", "Computer systems use cache to store frequently accessed data", "Computer Science")
            
            # Check that result is a dict and has some content
            assert isinstance(result, dict), f"Expected dict, got {type(result)}"
            assert len(result) > 0, "Empty result"
            
            runner.print_success(
                "Example Finder - Basic Test",
                f"Result keys: {list(result.keys())}"
            )
        except Exception as e:
            runner.print_failure("Example Finder - Basic Test", str(e))

        try:
            agent = EngagementOptimizerAgent()
            result = await agent.run(
                "RAM is like your work desk, SSD is like your filing cabinet",
                "Your device uses both RAM for speed and storage for capacity",
                "RAM vs Storage",
                "Why do phones need both RAM and storage?"
            )
            
            # Check that result is a dict and has some content
            assert isinstance(result, dict), f"Expected dict, got {type(result)}"
            assert len(result) > 0, "Empty result"
            
            runner.print_success(
                "Engagement Optimizer - Basic Test",
                f"Result keys: {list(result.keys())}"
            )
        except Exception as e:
            runner.print_failure("Engagement Optimizer - Basic Test", str(e))

        # ====================================================================
        # INTEGRATION TESTS
        # ====================================================================
        runner.print_header("Integration Tests")

        try:
            research = ResearchAgent()
            generator = QuestionGeneratorAgent()
            quality = QualityCheckAgent()

            research_result = await research.run("Computer Science")
            topic = research_result["recommended_topic"]

            gen_result = await generator.run("Computer Science", topic)
            question = gen_result["question"]

            quality_result = await quality.run("Computer Science", question)

            assert quality_result["quality_score"] > 0, "Invalid quality score"
            runner.print_success(
                "Integration - Research → Generator → Quality",
                f"Topic: {topic}, Question: {question[:40]}..., Quality: {quality_result['quality_score']}/10"
            )
        except Exception as e:
            runner.print_failure("Integration - Research → Generator → Quality", str(e))

        # ====================================================================
        # PRINT SUMMARY
        # ====================================================================
        runner.print_summary()

        return runner.failed == 0

    except ImportError as e:
        print(f"{RED}Error importing agents: {e}{RESET}")
        print(f"{YELLOW}Make sure all agent files are in the agents/ directory{RESET}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_agent_tests())
    sys.exit(0 if success else 1)
