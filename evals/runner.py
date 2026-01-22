import json
import yaml
import os
import time
from typing import Dict, Any, List
from evals.agents.npc import NPCAgent
from evals.agents.player_sim import PlayerSimulator

class GameRunner:
    def __init__(self, scenario_path: str, output_dir: str, run_config: Dict[str, Any] = None):
        with open(scenario_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.output_dir = output_dir
        self.run_config = run_config or {}
        self.transcript = []
        
    def run(self):
        scenario_id = self.config.get('scenario_id', 'unknown_scenario')
        run_id = self.run_config.get('run_id', '0')
        print(f"Starting scenario: {scenario_id} (Run {run_id})")
        temperature = self.run_config.get('temperature', 0.7)
        seed = self.run_config.get('seed', None)
        
        # Construct NPC System Prompt
        npc_profile = self.config.get('npc_profile', {})
        style_rules = npc_profile.get('style_rules', {})
        must_have = style_rules.get('must_have', [])
        must_not = style_rules.get('must_not', [])
        constraints = self.config.get('constraints', {}).get('hard_fail', [])
        
        npc_system_prompt = (
            f"You are {npc_profile.get('name', 'NPC')}, a {npc_profile.get('archetype', 'character')}.\n"
            f"Style Rules:\n"
            f"- Must have: {', '.join(must_have)}\n"
            f"- Must not: {', '.join(must_not)}\n"
            f"Constraints: {', '.join(constraints)}\n"
            f"You are interacting with a Hunter (Player)."
        )
        
        npc = NPCAgent(
            name=npc_profile.get('name', 'NPC'),
            system_prompt=npc_system_prompt
        )
        
        # Construct Player Simulator System Prompt
        player_persona = self.config.get('player_persona', {})
        goal = self.config.get('goal', '')
        seed_dialogue = self.config.get('seed_dialogue', '')
        
        traits = player_persona.get('traits', [])
        traits_str = f"Traits: {', '.join(traits)}\n" if traits else ""
        
        player_system_prompt = (
            f"You are a Monster Hunter player.\n"
            f"Tone: {player_persona.get('tone', 'neutral')}\n"
            f"{traits_str}"
            f"Goal: {goal}\n"
            f"Your first line was: \"{seed_dialogue}\"\n"
            f"IMPORTANT: You must think before you speak. Use the following format for every response:\n"
            f"[THOUGHTS]\n"
            f"Your internal monologue, strategy, and reaction to the NPC.\n"
            f"[/THOUGHTS]\n"
            f"[ACTION]\n"
            f"Your actual spoken dialogue to the NPC."
        )
        
        player = PlayerSimulator(
            system_prompt=player_system_prompt
        )
        
        max_turns = self.config.get('max_turns', 8)
        
        last_response = None
        
        for turn in range(max_turns):
            print(f"--- Turn {turn+1} ---")
            
            # Handle Player Turn
            if turn == 0 and seed_dialogue:
                player_msg = seed_dialogue
                # Manually inject into player history so it knows it said this
                player.history.append({"role": "assistant", "content": player_msg})
            else:
                player_msg = player.next_action(last_response, temperature=temperature, seed=seed)
            
            self.transcript.append({
                "turn": turn,
                "speaker": "Player",
                "content": player_msg
            })
            print(f"Player: {player_msg}")
            
            # NPC Turn
            npc_response = npc.reply(player_msg, temperature=temperature, seed=seed)
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
        # New schema has 'rubric' at top level
        if 'rubric' in self.config:
            from evals.graders.rubric_llm import LLMGrader
            llm_grader = LLMGrader()
            grades.append(llm_grader.grade(self.transcript, self.config['rubric']))
            
        self._save_results(grades)
        
    def _save_results(self, grades: List[Dict]):
        os.makedirs(self.output_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        scenario_id = self.config.get('scenario_id', 'unknown')
        run_id = self.run_config.get('run_id', '0')
        filename = f"{scenario_id}_run{run_id}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        result = {
            "scenario": scenario_id,
            "config": self.config,
            "run_config": self.run_config,
            "transcript": self.transcript,
            "grades": grades,
            "timestamp": timestamp
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"Run finished. Results saved to {filepath}")

# For testing
if __name__ == "__main__":
    # Assumes running from root
    runner = GameRunner("evals/scenarios/scenario_01.yaml", "evals/outputs/runs")
    runner.run()
