"""
Model Connector - Abstraction layer for AI models
Connects to Groq (primary - FREE) and Hugging Face (fallback)
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any
import aiohttp
from dotenv import load_dotenv

# Load .env from project root
from pathlib import Path
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

# Import Groq client
try:
    from groq import Groq
except ImportError:
    Groq = None


class ModelConnector:
    """
    Handles connections to different AI models with automatic fallback.
    Primary: Groq API (FREE - LLaMA 3.1 70B, super fast!)
    Fallback: Hugging Face free models (GPT2)
    """

    def __init__(self, model_type: str = "groq", max_retries: int = 2):
        self.model_type = model_type
        self.max_retries = max_retries
        self.groq_client = None
        self.groq_model = "llama-3.3-70b-versatile"  # Latest stable LLaMA 3.3 70B

        # Groq setup
        try:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key and Groq:
                self.groq_client = Groq(api_key=groq_api_key)
        except Exception as e:
            print(f"⚠️ Groq client init: {e}")
            self.groq_client = None

        # Hugging Face setup
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        self.huggingface_model = "gpt2"  # Using GPT2 - reliable and always available
        self.huggingface_api_url = f"https://api-inference.huggingface.co/models/{self.huggingface_model}"

    async def generate(self, prompt: str, model_override: Optional[str] = None) -> str:
        """
        Generate text using the specified model with automatic fallback.

        Args:
            prompt: The prompt to send to the model
            model_override: Override the default model choice

        Returns:
            Generated text from the model
        """
        model = model_override or self.model_type

        for attempt in range(self.max_retries + 1):
            try:
                if model == "groq":
                    result = await self._call_groq(prompt)
                    return result
                elif model == "huggingface":
                    result = await self._call_huggingface(prompt)
                    return result
                else:
                    return f"Model '{model}' not available"

            except Exception as e:
                print(f"❌ Attempt {attempt + 1}/{self.max_retries + 1} failed: {str(e)}")

                if attempt < self.max_retries:
                    # Try fallback model
                    fallback_model = "huggingface" if model == "groq" else "groq"
                    print(f"🔄 Switching to fallback model: {fallback_model}")
                    model = fallback_model
                    await asyncio.sleep(1)  # Brief delay before retry
                else:
                    print(f"⚠️ All models failed. Returning fallback response.")
                    return self._get_fallback_response(prompt)

    async def _call_groq(self, prompt: str) -> str:
        """Call Groq API (super fast, FREE)"""
        try:
            if not self.groq_client:
                raise Exception("GROQ_API_KEY not configured")
            
            # Groq API is sync, so we run it in a thread pool
            import concurrent.futures
            loop = asyncio.get_event_loop()
            
            def sync_call():
                message = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.groq_model,
                    temperature=0.7,
                    max_tokens=500,
                )
                return message.choices[0].message.content
            
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = await loop.run_in_executor(pool, sync_call)
            
            return result
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")

    async def _call_huggingface(self, prompt: str) -> str:
        """Call Hugging Face free inference API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.huggingface_token}",
                "Content-Type": "application/json",
            }

            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 500, "temperature": 0.7},
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.huggingface_api_url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result[0]["generated_text"]
                    else:
                        raise Exception(f"API returned status {response.status}")

        except Exception as e:
            raise Exception(f"Hugging Face API error: {str(e)}")

    def _get_fallback_response(self, prompt: str) -> str:
        """
        Return a safe fallback response when all models fail.
        Returns a JSON string that agents can parse.
        """
        # Return a string since model.generate() should return a string
        fallback_json = json.dumps({
            "topics": [
                {
                    "name": "General Topic",
                    "why_interesting": "Core concept in this field",
                    "difficulty": "intermediate",
                    "real_world_connection": "Practical applications exist"
                },
                {
                    "name": "Advanced Topic",
                    "why_interesting": "Builds on fundamental concepts",
                    "difficulty": "intermediate",
                    "real_world_connection": "Used in industry"
                },
                {
                    "name": "Emerging Topic",
                    "why_interesting": "New development in the field",
                    "difficulty": "intermediate",
                    "real_world_connection": "Future applications"
                }
            ],
            "recommended_topic": "General Topic"
        })
        return fallback_json

    async def test_connection(self) -> Dict[str, Any]:
        """Test both model connections and return status"""
        results = {"groq": "❌ Not tested", "huggingface": "❌ Not tested"}

        # Test Groq
        try:
            test_prompt = "Say 'Groq works' in exactly those words."
            response = await self._call_groq(test_prompt)
            if "works" in response.lower():
                results["groq"] = "✅ Working"
            else:
                results["groq"] = "⚠️ Unexpected response"
        except Exception as e:
            results["groq"] = f"❌ Error: {str(e)[:50]}"

        # Test Hugging Face
        try:
            test_prompt = "Say 'Hugging Face works' in exactly those words."
            response = await self._call_huggingface(test_prompt)
            if "works" in response.lower():
                results["huggingface"] = "✅ Working"
            else:
                results["huggingface"] = "⚠️ Unexpected response"
        except Exception as e:
            results["huggingface"] = f"❌ Error: {str(e)[:50]}"

        return results


# Singleton instance for use across app
_model_connector_instance = None


def get_model_connector(model_type: str = "groq") -> ModelConnector:
    """Get or create model connector instance"""
    global _model_connector_instance
    if _model_connector_instance is None:
        _model_connector_instance = ModelConnector(model_type=model_type)
    return _model_connector_instance
