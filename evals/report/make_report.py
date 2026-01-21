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
        md += "| Timestamp | Scenario | Result | Score |\n"
        md += "|-----------|----------|--------|-------|\n"
        
        for r in records:
            scenario = r.get('scenario', 'Unknown')
            timestamp = r.get('timestamp', '')
            grades = r.get('grades', [])
            
            # Aggregate result
            overall_result = "PASS"
            overall_score = "-"
            
            for g in grades:
                if g.get('metric') == 'rubric_eval':
                    overall_score = g.get('score', '-')
                    if g.get('result') == 'FAIL':
                        overall_result = "FAIL"
            
            md += f"| {timestamp} | {scenario} | {overall_result} | {overall_score} |\n"
            
        md += "\n## Detailed Results\n\n"
        
        for r in records:
            md += f"### Run: {r.get('scenario')} ({r.get('timestamp')})\n"
            
            # Grades
            md += "#### Grades\n"
            for g in r.get('grades', []):
                md += f"- **{g.get('metric')}**: {g.get('score', '-')} ({g.get('result', '-')})\n"
                if 'reason' in g:
                    md += f"  - Reason: {g['reason']}\n"
            
            # Transcript
            md += "#### Transcript\n"
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
