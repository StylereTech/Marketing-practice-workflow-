# Agent Reference Guide

## Overview

PulsePilot uses 5 specialized agents that work together through a shared memory system to execute marketing campaigns autonomously.

## Agent 0: Marketing Orchestrator 🧭

**Role**: Strategic coordinator and decision-maker

**Responsibilities**:
- Create overall campaign strategy
- Delegate tasks to specialist agents
- Synthesize outputs into cohesive plans
- Manage campaign phases and checkpoints
- Make strategic trade-offs

**Key Methods**:
```python
orchestrator.create_campaign_strategy(campaign_input)
orchestrator.generate_checkpoint(phase, data_to_review)
```

**When It Acts**:
- Phase 1: Creates campaign strategy
- Throughout: Coordinates specialist agents
- At checkpoints: Requests human approval

**System Prompt Focus**:
- Strategic thinking over tactical execution
- Data-driven decision making
- Risk identification and mitigation
- Clear communication of decisions

---

## Agent 1: Market Intelligence 🧠

**Role**: ICP researcher and messaging strategist

**Responsibilities**:
- Refine ICP pain points and buying triggers
- Develop value propositions
- Create messaging hierarchy
- Define competitive positioning
- Identify proof points

**Key Methods**:
```python
market_intel.create_messaging_framework(icp, company_context)
market_intel.refine_icp_profile(icp, additional_context)
```

**Outputs**:
- `MessagingFramework` with value prop and message hierarchy
- Refined ICP profile with deeper insights
- Objection handling strategies

**Best Practices**:
- Start with customer pain points, not features
- Use jobs-to-be-done framework
- Make messaging specific and quantifiable
- Create 3-tier message hierarchy (theme → pillars → proof)

---

## Agent 2: Content Production ✍️

**Role**: Master copywriter and content creator

**Responsibilities**:
- Write landing page copy
- Create LinkedIn posts and ad copy
- Develop gated assets (whitepapers, guides)
- Generate A/B test variations
- Ensure brand voice consistency

**Key Methods**:
```python
content.create_landing_page(messaging_framework, brand_voice)
content.create_linkedin_posts(messaging_framework, num_posts=5)
```

**Content Types**:
1. **Landing Pages**: Hero, benefits, social proof, CTAs
2. **LinkedIn Posts**: Problem/insight/success/trend/solution
3. **Email Sequences**: Nurture flows with progressive value
4. **Gated Assets**: Whitepapers and guides

**Output Structure**:
- Primary content
- 2-3 A/B variations
- Metadata (hooks, CTAs, type)

**Writing Principles**:
- Customer-centric language
- Clarity over cleverness
- Value-first approach
- Scannable format (bullets, short paragraphs)

---

## Agent 3: Distribution & Growth 📣

**Role**: Channel strategist and budget optimizer

**Responsibilities**:
- Select optimal marketing channels
- Define audience targeting criteria
- Allocate budget across channels
- Create rollout sequencing
- Plan A/B testing strategy

**Key Methods**:
```python
distribution.create_distribution_plan(icp, budget, timeline_days, objectives)
distribution.optimize_budget_allocation(performance_data, current_allocation)
```

**Channel Expertise**:
- LinkedIn Ads (Sponsored Content, InMail)
- Google Ads (Search, Display)
- Email Marketing
- Sales Enablement
- Content Syndication

**Budget Allocation**:
- 70% to proven channels
- 30% to experiments
- 10-15% contingency reserve

**Outputs**:
- `DistributionPlan` with channel allocations
- Targeting criteria per channel
- Rollout timeline and sequence

---

## Agent 4: Analytics & Learning 📊

**Role**: Data analyst and optimization expert

**Responsibilities**:
- Define KPI frameworks
- Monitor campaign performance
- Identify underperforming elements
- Generate optimization recommendations
- Report on ROI and attribution

**Key Methods**:
```python
analytics.define_kpis(campaign_strategy, objectives)
analytics.analyze_performance(metrics_data)
analytics.recommend_optimizations(performance_data, campaign_context)
```

**Metrics Tracked**:
- **Awareness**: Impressions, Reach, Brand Lift
- **Engagement**: CTR, Time on Page, Video Views
- **Conversion**: CVR, MQL, SQL, Opportunity
- **Efficiency**: CPA, CAC, ROAS, LTV:CAC

**Analysis Approach**:
1. Compare to benchmarks and goals
2. Look for patterns and anomalies
3. Consider statistical significance
4. Identify root causes
5. Prioritize high-impact fixes

**Outputs**:
- `PerformanceMetrics` with insights
- Prioritized optimization recommendations
- Channel performance breakdown

---

## Shared Memory Architecture

All agents read from and write to a **Shared Memory** system that serves as the single source of truth.

### Memory Structure

```python
{
    "brand_voice_rules": {},
    "icp_definition": {},
    "messaging_hierarchy": {},
    "approved_claims": [],
    "performance_data": [],
    "draft_assets": [],
    "channel_plans": [],
    "campaign_strategy": {},
    "tasks": []
}
```

### Memory Operations

**Write**:
```python
memory.write("key", value, agent_id="agent_name")
```

**Read**:
```python
value = memory.read("key", default=None)
```

**Append**:
```python
memory.append("list_key", item, agent_id="agent_name")
```

**Structured Data**:
```python
memory.set_strategy(strategy)
memory.set_messaging(messaging)
memory.add_asset(asset)
```

### Memory Benefits

1. **No Information Silos**: All agents see the same data
2. **Audit Trail**: Track who wrote what and when
3. **Versioning**: Automatic version increments
4. **Persistence**: Saved to disk for recovery
5. **Coordination**: Agents know when dependencies are ready

---

## Agent Coordination

### Sequential Dependencies

Agent 1 → Agent 2/3/4

Agent 1 (Market Intel) must complete first because:
- Agent 2 needs messaging framework for content
- Agent 3 needs ICP for targeting
- Agent 4 needs objectives for KPI definition

### Parallel Execution

Agents 2, 3, 4 can run in parallel:
- Read from shared memory independently
- Write to different memory keys
- No blocking dependencies

### Orchestrator Flow

```
Orchestrator
  ├─> Delegate to Agent 1
  │   └─> Wait for messaging framework
  ├─> Delegate to Agents 2, 3, 4 (parallel)
  │   └─> Wait for all completions
  └─> Synthesize outputs
```

---

## Extending Agents

### Create Custom Agent

```python
from pulsepilot.agents.base import BaseAgent
from pulsepilot.core.models import AgentRole

class CustomAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(AgentRole.CUSTOM, *args, **kwargs)

    def get_system_prompt(self) -> str:
        return """You are a custom agent that..."""

    def execute_task(self, task: AgentTask) -> AgentOutput:
        # Your logic here
        response = self.generate_output(task.description, context=task.inputs)
        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"result": response},
            status=TaskStatus.COMPLETED
        )
```

### Customize Existing Agent

Override specific methods:

```python
class CustomMarketIntel(MarketIntelligenceAgent):
    def get_system_prompt(self) -> str:
        base_prompt = super().get_system_prompt()
        return base_prompt + "\n\nADDITIONAL INSTRUCTIONS: ..."
```

---

## Best Practices

### For Orchestrator
- Make strategic decisions, not tactical ones
- Document rationale for major choices
- Identify and flag risks early
- Use checkpoints for critical decisions

### For Market Intel
- Ground insights in customer research
- Make messaging specific and quantifiable
- Create clear message hierarchy
- Always include objection handling

### For Content
- Write from customer perspective
- Lead with value, not features
- Create variations for testing
- Maintain brand voice consistency

### For Distribution
- Choose channels based on ICP
- Reserve budget for experiments
- Account for ramp-up periods
- Plan for iteration

### For Analytics
- Define KPIs before launch
- Compare to benchmarks
- Look for root causes
- Prioritize high-impact fixes

---

## Agent Communication

Agents don't communicate directly. Instead:

1. **Write to Memory**: Agent A writes output to shared memory
2. **Signal Complete**: Task status changes to COMPLETED
3. **Read from Memory**: Agent B reads when ready
4. **Continue Work**: Agent B uses data for its task

This **asynchronous, memory-based** architecture:
- Prevents blocking
- Enables parallelism
- Creates audit trail
- Simplifies debugging
