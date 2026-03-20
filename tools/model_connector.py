"""
Model Connector - Abstraction layer for AI models
Connects to ChatGPT (primary) and Hugging Face (fallback)
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

# Import OpenAI v1.0+ client
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class ModelConnector:
    """
    Handles connections to different AI models with automatic fallback.
    Primary: ChatGPT free tier (GPT-5.2 mini)
    Fallback: Hugging Face free models (Mistral-7B)
    """

    def __init__(self, model_type: str = "chatgpt", max_retries: int = 2):
        self.model_type = model_type
        self.max_retries = max_retries
        self.openai_client = None
        self.openai_model = "gpt-3.5-turbo"

        # ChatGPT setup (v1.0+ API)
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key and OpenAI:
                # Create client with minimal config
                self.openai_client = OpenAI(
                    api_key=openai_api_key,
                    timeout=60.0,
                    max_retries=1
                )
        except Exception as e:
            print(f"⚠️ OpenAI client init: {e}")
            self.openai_client = None

        # Hugging Face setup
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        self.huggingface_model = "mistralai/Mistral-7B-Instruct-v0.1"
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
                if model == "chatgpt":
                    result = await self._call_chatgpt(prompt)
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
                    fallback_model = "huggingface" if model == "chatgpt" else "chatgpt"
                    print(f"🔄 Switching to fallback model: {fallback_model}")
                    model = fallback_model
                    await asyncio.sleep(1)  # Brief delay before retry
                else:
                    print(f"⚠️ All models failed. Returning fallback response.")
                    return self._get_fallback_response(prompt)

    async def _call_chatgpt(self, prompt: str) -> str:
        """Call ChatGPT API (v1.0+ - free tier)"""
        try:
            if not self.openai_client:
                raise Exception("OPENAI_API_KEY not configured")
            
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"ChatGPT API error: {str(e)}")

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
        results = {"chatgpt": "❌ Not tested", "huggingface": "❌ Not tested"}

        # Test ChatGPT
        try:
            test_prompt = "Say 'ChatGPT works' in exactly those words."
            response = await self._call_chatgpt(test_prompt)
            if "works" in response.lower():
                results["chatgpt"] = "✅ Working"
            else:
                results["chatgpt"] = "⚠️ Unexpected response"
        except Exception as e:
            results["chatgpt"] = f"❌ Error: {str(e)[:50]}"

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


def get_model_connector(model_type: str = "chatgpt") -> ModelConnector:
    """Get or create model connector instance"""
    global _model_connector_instance
    if _model_connector_instance is None:
        _model_connector_instance = ModelConnector(model_type=model_type)
    return _model_connector_instance
