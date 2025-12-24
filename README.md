# 🚀 PulsePilot - Multi-Agent Marketing Orchestration System

<div align="center">

**Autonomous marketing campaign execution powered by specialized AI agents**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 📋 Overview

PulsePilot is a sophisticated multi-agent system that orchestrates end-to-end marketing campaigns through specialized AI agents. Each agent has a distinct role, working together through a shared memory system to execute campaigns from strategy to analytics.

### Architecture

```
🧭 Agent 0: Marketing Orchestrator
   ├── 🧠 Agent 1: Market Intelligence (ICP, messaging, positioning)
   ├── ✍️  Agent 2: Content Production (copy, assets, variations)
   ├── 📣 Agent 3: Distribution & Growth (channels, targeting, budget)
   └── 📊 Agent 4: Analytics & Learning (KPIs, monitoring, optimization)

🗂️  Shared Memory: Single source of truth for all campaign data
```

## 🎯 Key Features

- **Autonomous Campaign Execution**: 30-day campaign cycles with minimal human intervention
- **Specialist Agents**: Each agent focuses on a specific domain (strategy, content, distribution, analytics)
- **Shared Memory Architecture**: Centralized knowledge base prevents information silos
- **Human-in-the-Loop Checkpoints**: Strategic approval gates at critical decision points
- **Iterative Optimization**: Weekly performance analysis and automatic adjustments
- **Production-Ready**: Type-safe, well-tested, and properly structured

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Marketing-practice-workflow-

# Install dependencies with Poetry
poetry install

# Or with pip
pip install -e .
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# OPENAI_API_KEY=your_key_here
# or
# ANTHROPIC_API_KEY=your_key_here
```

### Run Your First Campaign

```bash
# Run the example campaign
poetry run python examples/run_campaign.py

# Or use the CLI
poetry run pulsepilot campaign create \
  --company "Your Company" \
  --icp "B2B SaaS CTOs" \
  --budget 50000 \
  --timeline 30
```

## 📖 Campaign Execution Flow

### Phase 1: Initialization (Day 0)
- Company brief intake
- ICP definition
- Budget & timeline setting
- **CHECKPOINT**: Approve overall strategy

### Phase 2: Strategy Definition (Days 1-3)
- Agent 1 refines ICP and pain points
- Creates messaging framework
- Develops value proposition
- **CHECKPOINT**: Approve messaging

### Phase 3: Parallel Execution (Days 4-10)
- Agent 2 creates content assets
- Agent 3 builds distribution plan
- Shared memory coordinates work
- **CHECKPOINT**: Approve launch

### Phase 4: Launch (Day 11)
- Deploy ads and sequences
- Enable sales outbound
- Begin performance tracking

### Phase 5: Feedback Loop (Days 12-30)
- Weekly performance analysis
- Automatic optimization
- Variation testing
- Continuous improvement

### Phase 6: Campaign Close
- Final performance analysis
- Learnings documentation
- Knowledge archival

## 🏗️ Project Structure

```
pulsepilot/
├── src/pulsepilot/
│   ├── agents/              # Specialist agent implementations
│   │   ├── orchestrator.py  # Agent 0: Campaign coordinator
│   │   ├── market_intel.py  # Agent 1: Market intelligence
│   │   ├── content.py       # Agent 2: Content production
│   │   ├── distribution.py  # Agent 3: Distribution strategy
│   │   └── analytics.py     # Agent 4: Analytics & learning
│   ├── core/
│   │   ├── memory.py        # Shared memory system
│   │   ├── models.py        # Pydantic data models
│   │   └── llm.py           # LLM interface layer
│   ├── workflows/
│   │   └── campaign.py      # Campaign orchestration logic
│   └── cli.py               # Command-line interface
├── examples/
│   └── run_campaign.py      # Example campaign execution
├── tests/                   # Test suite
├── docs/                    # Additional documentation
└── diagrams/                # Mermaid workflow diagrams
```

## 🔧 Advanced Usage

### Custom Agent Prompts

Each agent uses carefully crafted system prompts stored in `src/pulsepilot/prompts/`. Customize these to match your brand voice and requirements.

### Extending Agents

```python
from pulsepilot.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    async def execute(self, task: dict) -> dict:
        # Your custom logic here
        return {"status": "success", "output": "..."}
```

### Memory Inspection

```python
from pulsepilot.core.memory import SharedMemory

memory = SharedMemory()
messaging = memory.get("messaging_framework")
performance = memory.get("performance_data")
```

## 📊 Example Output

```
🧭 Campaign: B2B SaaS Product Launch
📅 Timeline: 30 days | 💰 Budget: $50,000

✅ Phase 1 Complete: Strategy approved
✅ Phase 2 Complete: Messaging framework ready
  → Pain Point: Legacy systems slow innovation
  → Value Prop: Ship features 3x faster

🔄 Phase 3 In Progress:
  ✍️  Content: 5 LinkedIn posts, 1 landing page, 1 whitepaper
  📣 Distribution: LinkedIn Ads + Email + Outbound

⏳ Next checkpoint: Approve launch (in 2 days)
```

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pulsepilot

# Run specific test
poetry run pytest tests/test_orchestrator.py
```

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with:
- OpenAI GPT-4 / Anthropic Claude for agent intelligence
- Pydantic for type safety
- Rich for beautiful CLI output

---

**Built with ❤️ by the PulsePilot team**
