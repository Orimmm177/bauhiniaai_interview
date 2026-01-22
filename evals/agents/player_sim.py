from typing import List, Dict
from evals.llm_client import LLMClient

class PlayerSimulator:
    def __init__(self, system_prompt: str, model: str = "deepseek-chat"):
        self.system_prompt = system_prompt
        self.client = LLMClient(provider="deepseek", model=model)
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    def next_action(self, npc_response: str = None) -> str:
        """
        Generate the next message to send to the NPC.
        If npc_response is None, it's the start of the conversation.
        """
        if npc_response:
            self.history.append({"role": "user", "content": npc_response})
        
        # Append instructions for the thought process if it's not the very first system prompt
        # (Though ideally this should be in the system prompt. Let's rely on the system prompt having these instructions now.)
        
        response = self.client.chat_completion(self.history)
        self.history.append({"role": "assistant", "content": response})
        
        # Parse the response to extract [ACTION]
        # Expected format:
        # [THOUGHTS] ... [/THOUGHTS]
        # [ACTION] ...
        
        import re
        action_match = re.search(r"\[ACTION\]\s*(.*)", response, re.DOTALL)
        if action_match:
            # Try to capture thoughts as well for debugging
            thoughts_match = re.search(r"\[THOUGHTS\]\s*(.*?)\[/THOUGHTS\]", response, re.DOTALL)
            if thoughts_match:
                thoughts = thoughts_match.group(1).strip()
                # Print thoughts in a distinct color (e.g., Cyan \033[96m)
                print(f"\033[96m[Player Inner Thoughts]: {thoughts}\033[0m")
            
            action_text = action_match.group(1).strip()
            # If the LLM generates closing tags or extra text, we might want to clean it up depending on how strict we are.
            # For now, let's assume the rest of the string is the action.
            return action_text
        else:
            # Fallback if the model forgets the format
            return response
