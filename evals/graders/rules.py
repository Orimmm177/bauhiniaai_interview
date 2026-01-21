from typing import List, Dict, Any

class RuleGrader:
    @staticmethod
    def check_max_length(transcript: List[Dict], max_chars: int = 500) -> Dict[str, Any]:
        """Check if any NPC response exceeds max_chars."""
        failures = []
        for line in transcript:
            if line['speaker'] == "NPC" and len(line['content']) > max_chars:
                failures.append(line['turn'])
        
        return {
            "metric": "max_length_check",
            "score": 0 if failures else 1,
            "reason": f"Failed turns: {failures}" if failures else "All responses within limit."
        }

    @staticmethod
    def check_keyword_presence(transcript: List[Dict], keywords: List[str]) -> Dict[str, Any]:
        """Check if any of the keywords appear in NPC responses."""
        found = []
        for line in transcript:
            if line['speaker'] == "NPC":
                text = line['content'].lower()
                for kw in keywords:
                    if kw.lower() in text:
                        found.append(kw)
        
        return {
            "metric": "keyword_presence",
            "score": 1 if found else 0,
            "reason": f"Found keywords: {set(found)}" if found else "No keywords found."
        }
