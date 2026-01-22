from typing import List, Dict, Any
from evals.llm_client import LLMClient

class LLMGrader:
    def __init__(self, model: str = "deepseek-chat"):
        self.client = LLMClient(provider="deepseek", model=model)

    def grade(self, transcript: List[Dict], rubric: Dict[str, Any]) -> Dict[str, Any]:
        """
        Grade the transcript based on the rubric dictionary.
        Returns a dict with structured scores and reasoning.
        """
        # Format transcript for LLM
        transcript_text = ""
        for line in transcript:
            transcript_text += f"{line['speaker']}: {line['content']}\n"
        
        # Format Rubric Instructions
        dimensions_text = ""
        if 'dimensions' in rubric:
            for dim, range_val in rubric['dimensions'].items():
                min_val = range_val.get('min', 0)
                max_val = range_val.get('max', 5)
                dimensions_text += f"- {dim}: Score between {min_val} and {max_val}\n"
        else:
             # Fallback if rubric format is different
             dimensions_text = f"Evaluate based on the following criteria: {rubric}"

        prompt = f"""
You are an expert judge of AI NPC performance.
Review the following conversation transcript and evaluate it based on the provided rubric dimensions.

Transcript:
{transcript_text}

Rubric Dimensions:
{dimensions_text}

Instructions:
1. For EACH dimension listed above, provide a score within the specified range.
2. Provide specific evidence/reasoning from the transcript for each score.
3. Calculate the total score.
4. Output your evaluation in valid JSON format.

Output Format (JSON):
{{
  "scores": {{
    "dimension_name": <number>,
    ...
  }},
  "reasoning": {{
    "dimension_name": "<text>",
    ...
  }},
  "total_score": <number>,
  "max_possible_score": <number>
}}
"""
        messages = [{"role": "system", "content": "You are an automated evaluator. Always output valid JSON."},
                    {"role": "user", "content": prompt}]
        
        response = self.client.chat_completion(messages)
        
        # Parse JSON
        import json
        import re
        
        try:
            # Try to find JSON block if mixed with text
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                data = json.loads(response)
                
            return {
                "metric": "rubric_eval",
                "scores": data.get("scores", {}),
                "reasoning": data.get("reasoning", {}),
                "total_score": data.get("total_score", 0),
                "result": "PASS", # Implicit pass for now, or define threshold
                "raw_output": response
            }
        except Exception as e:
            print(f"Failed to parse grader JSON: {e}")
            return {
                "metric": "rubric_eval",
                "score": 0,
                "result": "ERROR",
                "error": str(e),
                "raw_output": response
            }
