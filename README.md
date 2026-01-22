# AI NPC 对话评测系统 - 项目报告

## 1. 项目介绍

本项目旨在构建一个**自动化、可扩展且具有高可靠性**的游戏 NPC 对话评测系统。该系统通过模拟真实的玩家交互，对 AI NPC 的角色扮演能力、互动质量以及逻辑一致性进行多维度的量化评估。

系统的核心目标是解决传统人工测试效率低、难以回归以及覆盖面不足的问题，特别是针对 LLM 输出具有随机性（Non-determinism）的特点，引入了**多轮次验证**机制，以提供更可信的质量报告。


## 2. 系统架构 (System Architecture)

- `evals/agents`: NPCAgent和PlayerSimulator的实现
- `evals/graders`: Rule-based Grader和LLM Grader的实现
- `evals/scenarios`: 测试场景的定义（YAML）
- `evals/outputs`: 输出日志和报告
- `evals/run_eval.py`: 主CLI入口
- `evals/runner.py`: 核心游戏循环

## 3. 核心方法与实现

本项目采用了以下关键技术和方法论，以确保评测的准确性和有效性：

### 3.1 模拟仿真
为了实现全自动评测，构建了 **Player Simulator (模拟玩家)**。
- **机制**：基于 LLM 的 Agent，根据预设的 `Player Persona`（玩家人设）、`Goal`（目标）和 `Tone`（语气）自动生成回复。
- **优势**：能够模拟多样化的玩家行为（如刁钻提问、情感倾诉、闲聊等），覆盖人工测试难以穷尽的边界情况。
- **实现**：不仅生成对话，还包含 `[THOUGHTS]` 内部独白，模拟玩家的心理活动，使交互更逼真。

### 3.2 自动化评分
利用 LLM 强大的语义理解能力作为裁判（Judge），根据详细的 **Rubric (评分细则)** 对对话日志进行打分。
- **多维度评估**：我们在 YAML 配置文件中定义了灵活的评分维度，如 `tsundere_consistency`（傲娇一致性）、`gentleness`（温柔度）、`interaction_quality`（互动质量）等。
- **证据支撑**：评分不仅给出分数，还强制要求输出评分依据，避免“黑盒打分”，便于后续分析。

### 3.3 评估
针对 LLM 输出不稳定的特性，单一的测试结果往往具有误导性。必须要通过多次运行来评估**稳定性**。
- **多轮次运行 (Trials)**：每个场景默认执行 $k=5$ 次，每次使用随机的 `temperature` 和 `seed`，模拟不同的生成环境。
- **关键指标**：
    - **pass@k**：在 $k$ 次尝试中至少成功 1 次。这适用于对“下限”容忍度高、允许用户重试的场景（如创意写作助手）。
    - **pass^k**：在 $k$ 次尝试中**全部成功**。这对于游戏 NPC 至关重要，因为 NPC 需要保持**极高的稳定性**（High Consistency），以免打破沉浸感（OOC）。
- **意义**：这让我们不仅能判断 NPC "能不能做对"，还能判断它 "是不是总是对"。在这个项目中，因为是要评测对话智能体，所以我认为pass^k是更重要的指标，因为我们要保证每次对话都符合npc的人设。

### 3.4 解耦架构设计
- **Runner 与 Agent 解耦**：`GameRunner` 只负责流程控制，`NPCAgent` 和 `PlayerSimulator` 均作为插件式组件。未来可以轻松替换为其他模型或规则引擎 NPC。
- **配置驱动**：所有测试场景均通过 YAML 文件定义，无需修改代码即可新增测试用例，极大地提高了扩展性。

## 4. 运行说明

确保已安装依赖：
```bash
pip install -r requirements.txt
```

运行评测（全量场景，每个场景执行 5 次）：
```bash
python evals/run_eval.py
```

查看生成的报告：
`evals/report/report.md`
