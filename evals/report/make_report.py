import json
import os
import glob
from typing import List, Dict

class ReportGenerator:
    def __init__(self, runs_dir: str):
        self.runs_dir = runs_dir

    def generate_markdown(self, output_file: str = "report.md"):
        files = glob.glob(os.path.join(self.runs_dir, "*.json"))
        records = []
        for f in files:
            with open(f, 'r') as fd:
                records.append(json.load(fd))
        
        # Sort by timestamp desc
        records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        md = "# AI NPC Evaluation Report\n\n"
        md += f"**Total Runs**: {len(records)}\n\n"
        
        md += "## Summary\n\n"
        md += "| Timestamp | Scenario | Result | Total Score |\n"
        md += "|-----------|----------|--------|-------------|\n"
        
        for r in records:
            scenario = r.get('scenario', 'Unknown')
            timestamp = r.get('timestamp', '')
            grades = r.get('grades', [])
            
            # Aggregate result
            overall_result = "PASS"
            overall_score = "-"
            
            for g in grades:
                if g.get('metric') == 'rubric_eval':
                    # New format: total_score
                    if 'total_score' in g:
                         overall_score = g.get('total_score', '-')
                    # Old format: score
                    elif 'score' in g:
                         overall_score = g.get('score', '-')
                         
                    if g.get('result') == 'FAIL':
                        overall_result = "FAIL"
            
            md += f"| {timestamp} | {scenario} | {overall_result} | {overall_score} |\n"
            
        md += "\n## Detailed Results\n\n"
        
        for r in records:
            md += f"### Run: {r.get('scenario')} ({r.get('timestamp')})\n"
            
            # Grades
            md += "#### Rubric Evaluation\n"
            for g in r.get('grades', []):
                if g.get('metric') == 'rubric_eval':
                    
                    if 'scores' in g and isinstance(g['scores'], dict):
                        # Detailed table for dimensions
                        md += "| Dimension | Score | Evidence/Reasoning |\n"
                        md += "|-----------|-------|--------------------|\n"
                        scores = g.get('scores', {})
                        reasoning = g.get('reasoning', {})
                        
                        for dim, score in scores.items():
                            reason = reasoning.get(dim, "-")
                            md += f"| {dim} | {score} | {reason} |\n"
                        
                        md += f"\n**Total Score**: {g.get('total_score', '-')}\n"
                    else:
                        # Fallback for old simple score
                        md += f"- **Score**: {g.get('score', '-')} ({g.get('result', '-')})\n"
                        if 'reason' in g:
                            md += f"  - Reason: {g['reason']}\n"
            
            # Transcript
            md += "\n#### Transcript\n"
            md += "```\n"
            for line in r.get('transcript', []):
                md += f"{line['speaker']}: {line['content']}\n"
            md += "```\n\n"
            md += "---\n"
            
        with open(output_file, 'w') as f:
            f.write(md)
            
        print(f"Report generated at {output_file}")

if __name__ == "__main__":
    import sys
    runs_dir = sys.argv[1] if len(sys.argv) > 1 else "evals/outputs/runs"
    gen = ReportGenerator(runs_dir)
    gen.generate_markdown("evals/report/report.md")
