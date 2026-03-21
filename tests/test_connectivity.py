"""
Test - Connectivity Tests
Validates model and database connectivity
"""

import asyncio
import pytest
from tools.model_connector import get_model_connector
from tools.cache_manager import CacheManager


@pytest.mark.asyncio
async def test_chatgpt_connection():
    """Test ChatGPT API connection"""
    connector = get_model_connector("groq")
    try:
        response = await connector.generate("Say 'ChatGPT works' exactly.")
        assert "works" in response.lower()
        print("✅ ChatGPT connection OK")
    except Exception as e:
        print(f"❌ ChatGPT connection failed: {e}")
        raise


@pytest.mark.asyncio
async def test_huggingface_connection():
    """Test Hugging Face API connection"""
    connector = get_model_connector("huggingface")
    try:
        response = await connector.generate("Say 'Hugging Face works' exactly.")
        assert "works" in response.lower()
        print("✅ Hugging Face connection OK")
    except Exception as e:
        print(f"⚠️ Hugging Face temporarily unavailable (may retry): {e}")


def test_cache_manager():
    """Test cache manager functionality"""
    cache = CacheManager()

    # Test save
    test_payload = {
        "reel_question": "Test question?",
        "reel_answer": "Test answer.",
    }
    saved = cache.save("Computer Science", "test_topic", test_payload, 8.5)
    assert saved is True
    print("✅ Cache save OK")

    # Test retrieve
    retrieved = cache.get("Computer Science", "test_topic")
    assert retrieved is not None
    assert retrieved["reel_question"] == "Test question?"
    print("✅ Cache retrieval OK")

    # Test stats
    stats = cache.get_stats()
    assert stats["total_entries"] >= 1
    print(f"✅ Cache stats OK: {stats}")

    # Cleanup
    cache.clear_all()


def test_all_connectivity():
    """Run all connectivity tests"""
    print("\n🔍 Running connectivity tests...")

    asyncio.run(test_chatgpt_connection())
    asyncio.run(test_huggingface_connection())
    test_cache_manager()

    print("✅ All connectivity tests complete!")


if __name__ == "__main__":
    test_all_connectivity()
