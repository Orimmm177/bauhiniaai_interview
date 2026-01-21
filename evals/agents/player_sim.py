from typing import List, Dict
from evals.llm_client import LLMClient

class PlayerSimulator:
    def __init__(self, system_prompt: str, model: str = "gpt-4o"):
        self.system_prompt = system_prompt
        self.client = LLMClient(provider="openai", model=model)
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    def next_action(self, npc_response: str = None) -> str:
        """
        Generate the next message to send to the NPC.
        If npc_response is None, it's the start of the conversation.
        """
        if npc_response:
            self.history.append({"role": "user", "content": npc_response}) # From player POv, NPC is 'user' or we treat NPC as assistant?
            # Let's treat NPC as 'user' in the Sim's prompt history to distinguish, OR
            # Standard: System (Sim instructions), User (NPC says), Assistant (Sim thinks/says)
            # Let's go with: System=Persona, User=NPC's last message, Assistant=Sim's next move.
        
        response = self.client.chat_completion(self.history)
        
        self.history.append({"role": "assistant", "content": response})
        return response
