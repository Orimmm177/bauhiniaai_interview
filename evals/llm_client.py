import os
import json
import random
from typing import List, Dict, Optional

class LLMClient:
    def __init__(self, provider: str = "mock", model: str = "mock-model"):
        self.provider = provider
        self.model = model
        
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Get a completion from the LLM.
        messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
        """
        if self.provider == "mock":
            return self._mock_response(messages)
        
        # TODO: Add real provider implementations (OpenAI, Anthropic) here
        # For the purpose of this assignment ensuring it runs locally without keys first
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
