import os
import glob
import sys
import argparse
from evals.runner import GameRunner
from evals.report.make_report import ReportGenerator

def main():
    parser = argparse.ArgumentParser(description="Run AI NPC Evals")
    parser.add_argument("--scenarios", type=str, default="evals/scenarios", help="Directory containing scenario YAMLs")
    parser.add_argument("--output", type=str, default="evals/outputs/runs", help="Directory to save run outputs")
    parser.add_argument("--report-dir", type=str, default="evals/reports", help="Directory to save final report")
    
    args = parser.parse_args()
    
    # Discovery
    scenario_files = glob.glob(os.path.join(args.scenarios, "*.yaml"))
    
    if not scenario_files:
        print(f"No scenarios found in {args.scenarios}")
        return

    print(f"Found {len(scenario_files)} scenarios.")
    
    # Execution
    for s_file in scenario_files:
        runner = GameRunner(s_file, args.output)
        runner.run()
        
    # Reporting
    print("Generating report...")
    os.makedirs(args.report_dir, exist_ok=True)
    report_file = os.path.join(args.report_dir, "latest_report.md")
    gen = ReportGenerator(args.output)
    gen.generate_markdown(report_file)
    print("Done!")

if __name__ == "__main__":
    main()
