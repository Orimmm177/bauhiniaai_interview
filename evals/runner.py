import json
import yaml
import os
import time
from typing import Dict, Any, List
from evals.agents.npc import NPCAgent
from evals.agents.player_sim import PlayerSimulator

class GameRunner:
    def __init__(self, scenario_path: str, output_dir: str):
        with open(scenario_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.output_dir = output_dir
        self.transcript = []
        
    def run(self):
        print(f"Starting scenario: {self.config['name']}")
        
        npc = NPCAgent(
            name=self.config['npc']['name'],
            system_prompt=self.config['npc']['system_prompt']
        )
        
        player = PlayerSimulator(
            system_prompt=self.config['player']['system_prompt']
        )
        
        max_turns = self.config.get('max_turns', 5)
        
        # Initial trigger to start the conversation
        # Usually player starts, or NPC starts. Let's assume Player approaches NPC.
        last_response = None
        
        for turn in range(max_turns):
            # Player turn
            print(f"--- Turn {turn+1} ---")
            player_msg = player.next_action(last_response)
            self.transcript.append({
                "turn": turn,
                "speaker": "Player",
                "content": player_msg
            })
            print(f"Player: {player_msg}")
            
            # NPC turn
            npc_response = npc.reply(player_msg)
            self.transcript.append({
                "turn": turn,
                "speaker": "NPC",
                "content": npc_response
            })
            print(f"NPC: {npc_response}")
            
            last_response = npc_response
            
        # Grading
        print("Running graders...")
        grades = []
        
        # Rule-based
        from evals.graders.rules import RuleGrader
        grades.append(RuleGrader.check_max_length(self.transcript))
        
        # LLM-based
        if 'evaluation' in self.config and 'rubric' in self.config['evaluation']:
            from evals.graders.rubric_llm import LLMGrader
            llm_grader = LLMGrader()
            grades.append(llm_grader.grade(self.transcript, self.config['evaluation']['rubric']))
            
        self._save_results(grades)
        
    def _save_results(self, grades: List[Dict]):
        os.makedirs(self.output_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config['name']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        result = {
            "scenario": self.config['name'],
            "config": self.config,
            "transcript": self.transcript,
            "grades": grades,
            "timestamp": timestamp
        }
        
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
            
        print(f"Run finished. Results saved to {filepath}")

# For testing
if __name__ == "__main__":
    # Assumes running from root
    runner = GameRunner("evals/scenarios/scenario_01.yaml", "evals/outputs/runs")
    runner.run()
