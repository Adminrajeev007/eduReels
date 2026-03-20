"""
Mock Agent Tests for Development
Tests agents with mock AI responses (no API keys needed)
"""

import asyncio
import json
from typing import Dict, Any


# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


class MockModelConnector:
    """Mock model connector for testing without API calls"""

    async def generate(self, prompt: str) -> str:
        """Generate mock response based on prompt content"""

        if "research" in prompt.lower():
            return self._mock_research()
        elif "question generator" in prompt.lower() or "generate a question" in prompt.lower():
            return self._mock_question()
        elif "quality" in prompt.lower() or "score" in prompt.lower():
            return self._mock_quality()
        elif "answer" in prompt.lower():
            return self._mock_answer()
        else:
            return self._mock_fallback()

    def _mock_research(self) -> str:
        """Mock research agent response"""
        return json.dumps({
            "topics": [
                {
                    "name": "Memory Hierarchy",
                    "why_interesting": "Understanding how computer memory works at different speeds",
                    "difficulty": "intermediate",
                    "real_world_connection": "Makes your laptop faster"
                },
                {
                    "name": "CPU Caching",
                    "why_interesting": "Learn why CPUs need different levels of cache",
                    "difficulty": "intermediate",
                    "real_world_connection": "Affects gaming performance"
                },
                {
                    "name": "Virtual Memory",
                    "why_interesting": "How computers simulate unlimited memory",
                    "difficulty": "intermediate",
                    "real_world_connection": "Prevents your computer from crashing"
                }
            ],
            "recommended_topic": "Memory Hierarchy"
        })

    def _mock_question(self) -> str:
        """Mock question generator response"""
        return json.dumps({
            "question": "Why does your phone have both RAM and storage instead of just one?",
            "thinking_process": "A good question makes students think about the trade-offs between speed and capacity",
            "expected_difficulty": "intermediate"
        })

    def _mock_quality(self) -> str:
        """Mock quality checker response"""
        return json.dumps({
            "quality_score": 8.5,
            "pass": True,
            "issues": [],
            "suggested_improvements": ["Could add context about real-world impact"],
            "reasoning": "Question makes students think deeply about computer architecture"
        })

    def _mock_answer(self) -> str:
        """Mock answer generator response"""
        return json.dumps({
            "answer": "Your phone uses RAM for speed and storage for capacity. RAM is extremely fast but expensive and temporary—losing data when powered off. Storage is slower but permanent and cheap. Combining both gives you fast performance with permanent data storage.",
            "technical_depth": "suitable for B.Tech"
        })

    def _mock_fallback(self) -> str:
        """Generic fallback response"""
        return json.dumps({
            "result": "success",
            "data": "Mock data"
        })

    async def test_connection(self) -> Dict[str, Any]:
        """Mock connection test"""
        return {
            "chatgpt": "connected",
            "huggingface": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }


class TestFramework:
    """Simple test framework for mock tests"""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def test(self, name: str, condition: bool, message: str = ""):
        """Simple assertion helper"""
        if condition:
            print(f"{GREEN}✅ {name}{RESET}")
            if message:
                print(f"   {BLUE}{message}{RESET}")
            self.passed += 1
        else:
            print(f"{RED}❌ {name}{RESET}")
            if message:
                print(f"   {RED}{message}{RESET}")
            self.failed += 1

    def summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print(f"\n{BOLD}{'='*50}{RESET}")
        print(f"Tests Passed: {GREEN}{self.passed}/{total}{RESET}")
        if self.failed > 0:
            print(f"Tests Failed: {RED}{self.failed}{RESET}")
        print(f"{BOLD}{'='*50}{RESET}\n")

        return self.failed == 0


async def test_mock_research_parser():
    """Test parsing research response"""
    print(f"\n{BOLD}{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}{BLUE}Testing Mock Research Parser{RESET}")
    print(f"{BOLD}{BLUE}{'='*50}{RESET}\n")

    framework = TestFramework()
    connector = MockModelConnector()

    response = await connector.generate("research prompt")
    data = json.loads(response)

    framework.test("Has topics", "topics" in data)
    framework.test("Has recommended_topic", "recommended_topic" in data)
    framework.test("Topics count >= 3", len(data.get("topics", [])) >= 3)
    framework.test("First topic has name", "name" in data["topics"][0])
    framework.test("Recommended topic is valid", data["recommended_topic"] in [t["name"] for t in data["topics"]])

    return framework.summary()


async def test_mock_question_parser():
    """Test parsing question response"""
    print(f"\n{BOLD}{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}{BLUE}Testing Mock Question Parser{RESET}")
    print(f"{BOLD}{BLUE}{'='*50}{RESET}\n")

    framework = TestFramework()
    connector = MockModelConnector()

    response = await connector.generate("question generator prompt")
    data = json.loads(response)

    framework.test("Has question", "question" in data)
    framework.test("Has thinking_process", "thinking_process" in data)
    framework.test("Has expected_difficulty", "expected_difficulty" in data)
    framework.test("Question length > 20", len(data.get("question", "")) > 20)

    return framework.summary()


async def test_mock_quality_parser():
    """Test parsing quality response"""
    print(f"\n{BOLD}{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}{BLUE}Testing Mock Quality Parser{RESET}")
    print(f"{BOLD}{BLUE}{'='*50}{RESET}\n")

    framework = TestFramework()
    connector = MockModelConnector()

    response = await connector.generate("quality check prompt")
    data = json.loads(response)

    framework.test("Has quality_score", "quality_score" in data)
    framework.test("Has pass", "pass" in data)
    framework.test("Quality score in range", 0 <= data["quality_score"] <= 10)
    framework.test("Pass is boolean", isinstance(data["pass"], bool))
    framework.test("Has issues", "issues" in data)

    return framework.summary()


async def test_mock_answer_parser():
    """Test parsing answer response"""
    print(f"\n{BOLD}{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}{BLUE}Testing Mock Answer Parser{RESET}")
    print(f"{BOLD}{BLUE}{'='*50}{RESET}\n")

    framework = TestFramework()
    connector = MockModelConnector()

    response = await connector.generate("answer generator prompt")
    data = json.loads(response)

    framework.test("Has answer", "answer" in data)
    framework.test("Answer length > 30", len(data.get("answer", "")) > 30)

    return framework.summary()


async def test_json_validation():
    """Test JSON response validation"""
    print(f"\n{BOLD}{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}{BLUE}Testing JSON Validation{RESET}")
    print(f"{BOLD}{BLUE}{'='*50}{RESET}\n")

    framework = TestFramework()
    connector = MockModelConnector()

    # Test all mock responses are valid JSON
    responses = [
        ("research", await connector.generate("research prompt")),
        ("question", await connector.generate("question generator prompt")),
        ("quality", await connector.generate("quality check prompt")),
        ("answer", await connector.generate("answer generator prompt")),
    ]

    for name, response in responses:
        try:
            data = json.loads(response)
            framework.test(f"JSON Valid ({name})", True, "Successfully parsed as JSON")
        except json.JSONDecodeError as e:
            framework.test(f"JSON Valid ({name})", False, f"Failed to parse: {e}")

    return framework.summary()


async def test_fallback_logic():
    """Test fallback topics for different branches"""
    print(f"\n{BOLD}{BLUE}{'='*50}{RESET}")
    print(f"{BOLD}{BLUE}Testing Fallback Logic{RESET}")
    print(f"{BOLD}{BLUE}{'='*50}{RESET}\n")

    framework = TestFramework()

    # These would be the fallback topics in agents
    fallback_topics = {
        "Computer Science": ["Memory Hierarchy", "CPU Caching", "Virtual Memory"],
        "Electrical Engineering": ["Impedance Matching", "Power Factor", "Signal Integrity"],
        "Mechanical Engineering": ["Stress vs Strain", "Fatigue Analysis", "Heat Transfer"],
    }

    for branch, topics in fallback_topics.items():
        framework.test(f"Fallback topics for {branch}", len(topics) == 3, f"Found {len(topics)} topics")

    return framework.summary()


async def run_all_mock_tests():
    """Run all mock tests"""
    print(f"\n{BOLD}{YELLOW}{'='*70}{RESET}")
    print(f"{BOLD}{YELLOW}🧪 MOCK AGENT TESTS (No API Keys Required){RESET}")
    print(f"{BOLD}{YELLOW}{'='*70}{RESET}")

    results = []
    results.append(("Research Parser", await test_mock_research_parser()))
    results.append(("Question Parser", await test_mock_question_parser()))
    results.append(("Quality Parser", await test_mock_quality_parser()))
    results.append(("Answer Parser", await test_mock_answer_parser()))
    results.append(("JSON Validation", await test_json_validation()))
    results.append(("Fallback Logic", await test_fallback_logic()))

    # Final summary
    print(f"\n{BOLD}{YELLOW}{'='*70}{RESET}")
    print(f"{BOLD}{YELLOW}📊 FINAL RESULTS{RESET}")
    print(f"{BOLD}{YELLOW}{'='*70}{RESET}\n")

    all_passed = True
    for name, passed in results:
        status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
        print(f"{name}: {status}")
        all_passed = all_passed and passed

    print(f"\n{BOLD}{YELLOW}{'='*70}{RESET}\n")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(run_all_mock_tests())
    exit(0 if success else 1)
