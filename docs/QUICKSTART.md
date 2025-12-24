# Quick Start Guide

Get your first PulsePilot campaign running in 5 minutes.

## Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd Marketing-practice-workflow-

# 2. Install dependencies
pip install -e .

# 3. Set up API key
export OPENAI_API_KEY="sk-your-key-here"
# OR
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

## Your First Campaign

### Option 1: Run the Example

```bash
python examples/run_campaign.py
```

This runs a pre-configured B2B SaaS campaign for a fictional company called "DataFlow".

**What happens**:
1. ✅ Orchestrator creates campaign strategy
2. ✅ Market Intel develops messaging framework
3. ✅ Content creates landing page + 5 LinkedIn posts
4. ✅ Distribution plans 3-channel strategy
5. ✅ Analytics defines KPI framework
6. ✅ Campaign launches (simulated)
7. ✅ Performance analyzed with recommendations

**Output**: Full campaign package saved to `memory_store/campaign_*.json`

### Option 2: Quick Custom Campaign

```bash
python examples/simple_example.py
```

Edit the file to customize:
- Company name and product
- ICP details
- Budget and timeline
- Campaign objectives

### Option 3: CLI

```bash
pulsepilot campaign \
  --company "YourCompany" \
  --product "AI-powered analytics platform" \
  --icp "Head of Data" \
  --industry "SaaS" \
  --budget 25000 \
  --timeline 30
```

## Understanding the Output

### Console Output

```
🚀 PulsePilot Campaign Execution
Campaign: DataFlow
Budget: $50,000
Timeline: 30 days

📋 Phase 1: Initialization
  ✅ Strategy created
  ✓ Strategy approved: DataFlow Product Launch

🧠 Phase 2: Strategy Definition
  ✅ Messaging framework complete
  ✓ Messaging approved: The only data platform that...

⚡ Phase 3: Parallel Execution
  ✅ Created 6 assets
  ✅ Planned 3 channels
  ✅ KPI framework defined
  ✓ Launch approved

🚀 Phase 4: Campaign Launch
  → Launching LinkedIn Ads
  → Launching Email Marketing
  → Launching Sales Outbound

📊 Phase 5: Feedback Loop
  → CTR: 2.0%
  → CVR: 7.5%
  → CPA: $150
  ✓ Generated 3 optimization recommendations

📈 Phase 6: Campaign Close
  ✓ Campaign archived

✅ Campaign workflow completed!
```

### Saved Campaign Data

Located in `memory_store/campaign_[id].json`:

```json
{
  "campaign_strategy": {
    "campaign_name": "DataFlow Product Launch",
    "objectives": [...],
    "approach": "...",
    "key_decisions": {...}
  },
  "messaging_hierarchy": {
    "value_proposition": "...",
    "key_messages": [...],
    "pain_points": [...]
  },
  "draft_assets": [
    {
      "asset_type": "landing_page",
      "title": "...",
      "content": "..."
    },
    {
      "asset_type": "linkedin_post",
      "content": "..."
    }
  ],
  "distribution_plan": {
    "channels": [...],
    "total_budget": 50000
  },
  "kpi_framework": {
    "north_star_metric": {...},
    "primary_kpis": [...]
  }
}
```

## Next Steps

### 1. Review Campaign Assets

```python
from pulsepilot.core.memory import SharedMemory

# Load campaign
memory = SharedMemory("campaign_abc123")

# Get messaging
messaging = memory.get_messaging()
print(messaging.value_proposition)

# Get assets
assets = memory.get_assets()
for asset in assets:
    print(f"{asset.asset_type}: {asset.title}")
```

### 2. Customize Agents

Create `custom_agents.py`:

```python
from pulsepilot.agents.market_intel import MarketIntelligenceAgent

class MyMarketIntel(MarketIntelligenceAgent):
    def get_system_prompt(self) -> str:
        base = super().get_system_prompt()
        return base + "\n\nFocus on healthcare industry specifics."
```

### 3. Add Human Checkpoints

```python
workflow = CampaignWorkflow(
    campaign_input,
    auto_approve=False  # Require human approval
)

# Will pause at each checkpoint for manual review
results = workflow.run()
```

### 4. Run Multiple Campaigns

```python
from concurrent.futures import ThreadPoolExecutor

campaigns = [campaign1, campaign2, campaign3]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(CampaignWorkflow(c, auto_approve=True).run)
        for c in campaigns
    ]
    results = [f.result() for f in futures]

print(f"Completed {len(results)} campaigns")
```

## Common Patterns

### B2B SaaS Campaign

```python
campaign_input = CampaignInput(
    company=CompanyBrief(
        name="YourSaaS",
        industry="B2B SaaS",
        product_description="[Product description]",
    ),
    icp=ICPDefinition(
        title="VP Engineering / CTO",
        industry="Technology",
        company_size="100-1000",
        pain_points=[
            "Engineers spend too much time on [problem]",
            "Current solutions are too [pain point]",
        ],
    ),
    constraints=CampaignConstraints(
        total_budget=50000,
        timeline_days=30,
    ),
    objectives=[
        "Generate 100 MQLs",
        "Book 25 demos",
        "Achieve <$500 CPA",
    ],
)
```

### Product Launch Campaign

```python
campaign_input = CampaignInput(
    # ... company and ICP ...
    objectives=[
        "Create awareness for new product launch",
        "Generate 500 signups in first month",
        "Achieve 20% activation rate",
    ],
    additional_context={
        "launch_date": "2025-02-01",
        "new_features": ["AI automation", "Real-time sync"],
    }
)
```

### Demand Generation Campaign

```python
campaign_input = CampaignInput(
    # ... company and ICP ...
    constraints=CampaignConstraints(
        total_budget=100000,
        timeline_days=90,  # Longer campaign
        priority_channels=["LinkedIn", "Google Search", "Content Syndication"],
    ),
    objectives=[
        "Generate 500 MQLs",
        "Create $2M in pipeline",
        "Maintain <$200 cost per MQL",
    ]
)
```

## Configuration Tips

### Choose the Right Model

**For High-Quality Outputs**:
```bash
export ORCHESTRATOR_MODEL=gpt-4-turbo-preview
export AGENT_MODEL=gpt-4-turbo-preview
```

**For Cost Optimization**:
```bash
export ORCHESTRATOR_MODEL=gpt-3.5-turbo
export AGENT_MODEL=gpt-3.5-turbo
```

**For Speed**:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
# Haiku is 5x faster and 10x cheaper
```

### Memory Management

```bash
# Enable persistence (default)
export MEMORY_PERSISTENCE=true

# Disable for ephemeral campaigns
export MEMORY_PERSISTENCE=false
```

## Troubleshooting

### "No API key found"

```bash
# Check if set
echo $OPENAI_API_KEY

# If empty, set it
export OPENAI_API_KEY="sk-..."
```

### "Module not found"

```bash
# Reinstall
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### "JSON parsing error"

This usually means the LLM returned invalid JSON. Solutions:

1. Lower the temperature (makes output more predictable)
2. Use a more capable model (GPT-4 vs GPT-3.5)
3. Check LLM API status

### Campaign not persisting

```bash
# Check permissions
ls -la memory_store/

# Create if missing
mkdir -p memory_store
chmod 755 memory_store
```

## What's Next?

- Read [Agent Guide](AGENTS.md) to understand each agent
- See [Deployment Guide](DEPLOYMENT.md) for production setup
- Check [examples/](../examples/) for more use cases
- Customize prompts in `src/pulsepilot/agents/`

## Getting Help

- **Documentation**: `/docs` folder
- **Examples**: `/examples` folder
- **Issues**: GitHub Issues
- **Code**: Well-commented source in `/src`

---

**You're ready to run autonomous marketing campaigns! 🚀**
