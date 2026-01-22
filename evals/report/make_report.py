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
        
        # Group by scenario
        scenario_stats = {}
        for r in records:
            sid = r.get('scenario', 'Unknown')
            if sid not in scenario_stats:
                scenario_stats[sid] = {"runs": [], "passes": 0, "total_score": 0}
            
            # Determine Pass/Fail for this run
            grades = r.get('grades', [])
            is_pass = True
            run_score = 0
            
            for g in grades:
                # Rule grader check
                if g.get('result') == 'FAIL':
                    is_pass = False
                
                # Rubric check
                if g.get('metric') == 'rubric_eval':
                    if g.get('result') == 'FAIL':
                        is_pass = False
                    # Try to get score
                    s = g.get('total_score', 0)
                    if s == '-': s = 0
                    run_score = float(s)

            scenario_stats[sid]["runs"].append(r)
            if is_pass:
                scenario_stats[sid]["passes"] += 1
            scenario_stats[sid]["total_score"] += run_score
            
            # Annotate record for detailed view
            r["_is_pass"] = is_pass
            r["_score"] = run_score

        md = "# AI NPC Evaluation Report\n\n"
        md += f"**Total Runs**: {len(records)}\n\n"
        
        md += "## Reliability Analysis (Pass@k / Pass^k)\n"
        md += "Concepts:\n"
        md += "- **pass@k**: At least 1 success in k trials. Suitable for products allowing retry.\n"
        md += "- **pass^k**: All k trials successful. Suitable for NPCs requiring high stability.\n\n"
        
        md += "| Scenario | Trials (k) | Pass Count | pass@k | pass^k | Avg Score |\n"
        md += "|----------|------------|------------|--------|--------|-----------|\n"
        
        for sid, data in scenario_stats.items():
            k = len(data["runs"])
            passes = data["passes"]
            avg_score = data["total_score"] / k if k > 0 else 0
            
            pass_at_k = "YES" if passes >= 1 else "NO"
            pass_caret_k = "YES" if passes == k else "NO"
            
            md += f"| {sid} | {k} | {passes} | {pass_at_k} | {pass_caret_k} | {avg_score:.2f} |\n"
            
        md += "\n## Run Summary\n\n"
        md += "| Timestamp | Scenario | Run ID | Result | Score |\n"
        md += "|-----------|----------|--------|--------|-------|\n"
        
        for r in records:
            scenario = r.get('scenario', 'Unknown')
            timestamp = r.get('timestamp', '')
            run_id = r.get('run_config', {}).get('run_id', '-')
            result = "PASS" if r.get("_is_pass") else "FAIL"
            score = r.get("_score")
            
            md += f"| {timestamp} | {scenario} | {run_id} | {result} | {score} |\n"
            
        md += "\n## Detailed Results\n\n"
        
        for r in records:
            scenario = r.get('scenario')
            run_id = r.get('run_config', {}).get('run_id', '-')
            timestamp = r.get('timestamp')
            
            md += f"### Run: {scenario} (Run {run_id}, time: {timestamp})\n"
            md += f"**Result**: {'PASS' if r.get('_is_pass') else 'FAIL'}\n"
            
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
