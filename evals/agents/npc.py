from typing import List, Dict
from evals.llm_client import LLMClient

class NPCAgent:
    def __init__(self, name: str, system_prompt: str, model: str = "gpt-4o"):
        self.name = name
        self.system_prompt = system_prompt
        self.client = LLMClient(provider="openai", model=model) # Default to real provider assumption in code, client handles switching
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    def reply(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})
        
        response = self.client.chat_completion(self.history)
        
        self.history.append({"role": "assistant", "content": response})
        return response
    
    def get_history(self) -> List[Dict[str, str]]:
        return self.history
