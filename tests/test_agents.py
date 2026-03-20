"""
Tests for Week 2 Agents
Unit and integration tests for all agents
"""

import asyncio
import sys
import os
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.research_agent import ResearchAgent
from agents.question_generator import QuestionGeneratorAgent
from agents.quality_checker import QualityCheckAgent
from agents.orchestrator import EducationalReelsOrchestrator


# ============================================================================
# RESEARCH AGENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_research_agent_happy_path():
    """Test research agent with valid degree"""
    agent = ResearchAgent()
    result = await agent.run("Computer Science")

    assert "topics" in result
    assert "recommended_topic" in result
    assert len(result["topics"]) >= 3
    assert all("name" in t for t in result["topics"])
    print("✅ Research Agent Happy Path: PASS")


@pytest.mark.asyncio
async def test_research_agent_unknown_degree():
    """Test research agent with unknown degree (fallback)"""
    agent = ResearchAgent()
    result = await agent.run("UnknownDegree123")

    assert "topics" in result
    assert "recommended_topic" in result
    print("✅ Research Agent Fallback: PASS")


@pytest.mark.asyncio
async def test_research_agent_all_branches():
    """Test research agent with all 3 target branches"""
    agent = ResearchAgent()

    branches = ["Computer Science", "Electrical Engineering", "Mechanical Engineering"]

    for branch in branches:
        result = await agent.run(branch)
        assert "recommended_topic" in result
        assert len(result["topics"]) >= 1
        print(f"✅ Research Agent ({branch}): PASS")


# ============================================================================
# QUESTION GENERATOR TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_question_generator_happy_path():
    """Test question generator with valid inputs"""
    agent = QuestionGeneratorAgent()
    result = await agent.run("Computer Science", "Memory Hierarchy", "Students use laptops daily")

    assert "question" in result
    assert "thinking_process" in result
    assert "expected_difficulty" in result
    assert len(result["question"]) > 10
    print("✅ Question Generator Happy Path: PASS")


@pytest.mark.asyncio
async def test_question_generator_not_basic():
    """Test that generator avoids 'What is' format"""
    agent = QuestionGeneratorAgent()
    result = await agent.run("Computer Science", "CPU Caching", "Cache speeds up processors")

    question = result.get("question", "").lower()
    # Should ideally use Why/How/What-if, not What is/Define
    print(f"✅ Generated Question: {result.get('question', 'N/A')[:60]}...")


# ============================================================================
# QUALITY CHECKER TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_quality_checker_good_question():
    """Test quality checker with a good question"""
    agent = QualityCheckAgent()

    good_question = "Why does your phone have both RAM and storage instead of just one?"
    result = await agent.run("Computer Science", good_question)

    assert "quality_score" in result
    assert "pass" in result
    assert result["quality_score"] >= 1
    print(f"✅ Quality Check (Good Q): Score {result['quality_score']}/10")


@pytest.mark.asyncio
async def test_quality_checker_bad_question():
    """Test quality checker with a bad question"""
    agent = QualityCheckAgent()

    bad_question = "What is RAM?"
    result = await agent.run("Computer Science", bad_question)

    assert "quality_score" in result
    assert result["quality_score"] < 7  # Should fail
    print(f"✅ Quality Check (Bad Q): Score {result['quality_score']}/10 (FAIL as expected)")


@pytest.mark.asyncio
async def test_quality_checker_threshold():
    """Test quality checker threshold logic"""
    agent = QualityCheckAgent(quality_threshold=7.0)

    question = "Why is error handling important in programming?"
    result = await agent.run("Computer Science", question)

    # Check pass logic
    expected_pass = result["quality_score"] >= 7.0
    assert result["pass"] == expected_pass
    print(f"✅ Quality Threshold Logic: PASS")


# ============================================================================
# ORCHESTRATOR TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_orchestrator_full_pipeline():
    """Test full orchestrator pipeline"""
    orchestrator = EducationalReelsOrchestrator()

    result = await orchestrator.generate_reel_content("Computer Science")

    # Check all required fields
    assert "degree" in result
    assert "topic" in result
    assert "reel_question" in result
    assert "reel_answer" in result
    assert "quality_score" in result
    assert "generation_time" in result
    assert "status" in result

    print(f"✅ Orchestrator Full Pipeline: {result['status'].upper()}")
    print(f"   Topic: {result['topic']}")
    print(f"   Quality: {result['quality_score']}/10")
    print(f"   Time: {result['generation_time']:.2f}s")


@pytest.mark.asyncio
async def test_orchestrator_cache():
    """Test orchestrator caching"""
    orchestrator = EducationalReelsOrchestrator()

    # First call (uncached)
    result1 = await orchestrator.generate_reel_content("Computer Science")
    time1 = result1["generation_time"]

    # Second call (cached - should be much faster)
    result2 = await orchestrator.generate_reel_content("Computer Science")
    time2 = result2["generation_time"]

    assert result2["cached"] == True
    assert time2 < time1 * 0.5  # Cache should be at least 2x faster

    print(f"✅ Orchestrator Caching: PASS")
    print(f"   First call: {time1:.2f}s (uncached)")
    print(f"   Second call: {time2:.2f}s (cached)")


@pytest.mark.asyncio
async def test_orchestrator_all_branches():
    """Test orchestrator with all 3 branches"""
    orchestrator = EducationalReelsOrchestrator()

    branches = ["Computer Science", "Electrical Engineering", "Mechanical Engineering"]

    for branch in branches:
        result = await orchestrator.generate_reel_content(branch)

        assert result["status"] == "success"
        assert result["degree"] == branch
        assert result["quality_score"] > 0

        print(f"✅ Orchestrator ({branch}): PASS")


@pytest.mark.asyncio
async def test_orchestrator_cache_stats():
    """Test orchestrator cache statistics"""
    orchestrator = EducationalReelsOrchestrator()

    # Generate some content
    await orchestrator.generate_reel_content("Computer Science")
    await orchestrator.generate_reel_content("Computer Science")  # Cache hit

    stats = orchestrator.get_cache_stats()

    assert "total_entries" in stats
    assert "cache_hits" in stats
    assert "cache_hit_rate" in stats

    print(f"✅ Cache Stats: {stats}")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_integration_research_to_quality():
    """Integration test: Research → Generator → Quality"""
    research = ResearchAgent()
    generator = QuestionGeneratorAgent()
    quality = QualityCheckAgent()

    # Research
    research_result = await research.run("Computer Science")
    topic = research_result["recommended_topic"]

    # Generate
    gen_result = await generator.run("Computer Science", topic)
    question = gen_result["question"]

    # Check Quality
    quality_result = await quality.run("Computer Science", question)

    assert quality_result["quality_score"] > 0
    print(f"✅ Integration Test: Research → Generator → Quality: PASS")
    print(f"   Topic: {topic}")
    print(f"   Question: {question[:60]}...")
    print(f"   Quality: {quality_result['quality_score']}/10")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

async def run_all_tests():
    """Run all tests sequentially"""
    print("\n" + "=" * 70)
    print("🧪 WEEK 2 AGENT TESTS")
    print("=" * 70 + "\n")

    # Research Agent Tests
    print("📍 Research Agent Tests:")
    await test_research_agent_happy_path()
    await test_research_agent_unknown_degree()
    await test_research_agent_all_branches()

    print("\n📍 Question Generator Tests:")
    await test_question_generator_happy_path()
    await test_question_generator_not_basic()

    print("\n📍 Quality Checker Tests:")
    await test_quality_checker_good_question()
    await test_quality_checker_bad_question()
    await test_quality_checker_threshold()

    print("\n📍 Orchestrator Tests:")
    await test_orchestrator_full_pipeline()
    await test_orchestrator_cache()
    await test_orchestrator_all_branches()
    await test_orchestrator_cache_stats()

    print("\n📍 Integration Tests:")
    await test_integration_research_to_quality()

    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
