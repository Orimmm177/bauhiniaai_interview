import os
import random
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMClient:
    def __init__(self, provider: str = "deepseek", model: str = "deepseek-chat"):
        self.provider = provider
        self.model = model
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        self.client = None
        if self.api_key and self.provider != "mock":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                print("Warning: 'openai' package not installed. Falling back to mock.")
        
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, seed: Optional[int] = None) -> str:
        """
        Get a completion from the LLM.
        messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
        """
        if self.client:
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature
                }
                if seed is not None:
                    kwargs["seed"] = seed

                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                print(f"Error calling LLM API: {e}. Falling back to mock.")
                return self._mock_response(messages)
        else:
            return self._mock_response(messages)

    def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        last_msg = messages[-1]["content"]
        # Simple heuristics to make the mock conversation flow slightly
        if "simulated player" in str(messages[0].get("content", "")).lower():
            # This is the player simulator generating a move
            actions = ["Hello there!", "What can you tell me about this place?", "I am looking for a quest.", "Goodbye."]
            return random.choice(actions)
        else:
            # This is the NPC responding
            return f"Mock NPC Response to: {last_msg[:20]}..."
