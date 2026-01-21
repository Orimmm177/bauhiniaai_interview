# AI Agent Evaluation System

This project provides an automated evaluation framework for NPC dialogue systems.
It simulates conversations between a User (Simulated Player) and an NPC, and evaluates the interaction using both rule-based checks and LLM-based grading.

## Directory Structure

- `evals/agents`: Implementations of NPC and Player Simulator agents.
- `evals/graders`: Grading logic (Rule-based and LLM-based).
- `evals/scenarios`: Test case definitions (YAML).
- `evals/outputs`: Output logs and reports.
- `evals/run_eval.py`: Main CLI entry point.
- `evals/runner.py`: Core game loop.

## Setup

The project requires Python 3. It is recommended to use a virtual environment.

```bash
# Create virtual environment
python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install pyyaml
```

## Running Evaluations

### Basic Run
To run all scenarios in `evals/scenarios`:

```bash
export PYTHONPATH=$PYTHONPATH:.
python evals/run_eval.py
```

This will:
1. Load scenarios from `evals/scenarios`.
2. Run conversations between the Mock NPC and Simulated Player.
3. Save detailed JSON logs to `evals/outputs/runs`.
4. Generate a summary report at `evals/reports/latest_report.md`.

### Configuration
You can add new scenarios by creating YAML files in `evals/scenarios`.
See `evals/scenarios/scenario_01.yaml` for an example.

## Architecture

1. **Agents**: The system uses `LLMClient` to abstract model calls. The `NPC` agent represents the system under test, while `PlayerSimulator` drives the conversation based on a goal.
2. **Runner**: `GameRunner` orchestrates the turn-based interaction.
3. **Grading**:
   - `RuleGrader`: Hard constraints (e.g. response length).
   - `LLMGrader`: Subjective quality assessment (e.g. politeness, adherence to instructions) using an LLM judge.
