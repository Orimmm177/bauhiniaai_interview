from typing import List, Dict, Any
from evals.llm_client import LLMClient

class LLMGrader:
    def __init__(self, model: str = "deepseek-chat"):
        self.client = LLMClient(provider="deepseek", model=model)

    def grade(self, transcript: List[Dict], rubric: str) -> Dict[str, Any]:
        """
        Grade the transcript based on the rubric.
        Returns a dict with score (1-5), reasoning, and pass/fail boolean.
        """
        # Format transcript for LLM
        transcript_text = ""
        for line in transcript:
            transcript_text += f"{line['speaker']}: {line['content']}\n"
        
        prompt = f"""
You are an expert judge of AI NPC performance.
Review the following conversation transcript and evaluate it based on the provided rubric.

Transcript:
{transcript_text}

Rubric:
{rubric}

Instructions:
1. Provide a score from 1 to 5 (1=Terrible, 5=Perfect).
2. Determine if the test case PASSED or FAILED based on the rubric criteria.
3. Provide a brief explanation for your score.

Output Format:
Score: <1-5>
Result: <PASS/FAIL>
Reasoning: <text>
"""
        messages = [{"role": "system", "content": "You are an automated evaluator."},
                    {"role": "user", "content": prompt}]
        
        response = self.client.chat_completion(messages)
        
        # Simple parsing (robustness would need regex in production)
        score = 0
        result = "FAIL"
        reasoning = response
        
        # Mock parsing logic since our mock LLM returns garbage right now
        # In real impl, we would parse `response`
        if "Score:" in response:
            try:
                score = int(response.split("Score:")[1].split()[0])
            except:
                pass
        
        if "Result: PASS" in response:
            result = "PASS"
            
        return {
            "metric": "rubric_eval",
            "score": score,
            "result": result,
            "reason": reasoning,
            "raw_output": response
        }
