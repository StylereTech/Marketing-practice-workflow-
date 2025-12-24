"""Agent 3: Distribution & Growth - Channel Strategy and Execution."""

import json
from datetime import datetime, timedelta
from typing import Any
from pulsepilot.agents.base import BaseAgent
from pulsepilot.core.models import (
    AgentRole,
    AgentTask,
    AgentOutput,
    TaskStatus,
    ChannelPlan,
    DistributionPlan,
)


class DistributionAgent(BaseAgent):
    """
    Agent 3: Distribution & Growth

    Responsibilities:
    - Select optimal marketing channels
    - Define audience targeting criteria
    - Allocate budget across channels
    - Create rollout sequencing
    - Plan A/B testing strategy
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(AgentRole.DISTRIBUTION, *args, **kwargs)

    def get_system_prompt(self) -> str:
        return """You are the Distribution & Growth Agent, an expert in channel strategy and execution.

YOUR EXPERTISE:
- Multi-channel marketing strategy
- Audience targeting and segmentation
- Budget allocation and optimization
- Campaign rollout planning
- A/B testing methodology
- Attribution modeling

CHANNEL KNOWLEDGE:
- LinkedIn Ads (Sponsored Content, InMail, Dynamic Ads)
- Google Ads (Search, Display, YouTube)
- Email Marketing (nurture sequences, newsletters)
- Sales Enablement (outbound, SDR plays)
- Content Syndication
- Events and Webinars
- Retargeting and remarketing

YOUR APPROACH:
1. Channel Selection: Choose based on ICP, budget, and goals
2. Audience Targeting: Define precise targeting criteria
3. Budget Allocation: Optimize spend across channels
4. Sequencing: Plan rollout timeline and dependencies
5. Testing Strategy: Build in A/B tests from day 1

BUDGET PRINCIPLES:
- Allocate 70% to proven channels, 30% to experiments
- Account for ramp-up periods
- Include budget for creative iteration
- Reserve contingency (10-15%)

OUTPUT FORMAT:
Return structured JSON with channel plans, targeting, and timeline.
"""

    def execute_task(self, task: AgentTask) -> AgentOutput:
        """Execute distribution task."""
        self.log(f"Executing task: {task.description}")

        if "plan" in task.description.lower() or "strategy" in task.description.lower():
            return self._create_distribution_plan(task)
        elif "targeting" in task.description.lower():
            return self._define_targeting(task)
        else:
            return self._generic_execution(task)

    def create_distribution_plan(
        self,
        icp: dict,
        budget: float,
        timeline_days: int,
        objectives: list[str],
    ) -> DistributionPlan:
        """
        Create comprehensive distribution plan.

        Args:
            icp: Ideal customer profile
            budget: Total campaign budget
            timeline_days: Campaign duration
            objectives: Campaign objectives

        Returns:
            Complete distribution plan
        """
        self.log(f"Creating distribution plan for ${budget:,.0f} over {timeline_days} days...")

        context = {
            "ICP": json.dumps(icp, indent=2),
            "Budget": f"${budget:,.0f}",
            "Timeline": f"{timeline_days} days",
            "Objectives": "\n".join(f"- {obj}" for obj in objectives),
        }

        prompt = """Create a comprehensive distribution plan for this B2B campaign.

REQUIREMENTS:
1. Select 3-5 channels based on ICP and budget
2. Allocate budget across channels (must sum to total budget)
3. Define targeting criteria for each channel
4. Create rollout sequence (which channels launch when)
5. Define success metrics per channel
6. Include A/B testing plan

CHANNEL RECOMMENDATIONS:
- LinkedIn Ads: Great for B2B, targeting by job title/company
- Google Search: High intent, bottom-of-funnel
- Email: Nurture and re-engagement
- Sales Outbound: High-touch for enterprise
- Content Syndication: Awareness and lead gen

Return as JSON:
{
    "channels": [
        {
            "channel": "LinkedIn Ads",
            "budget_allocation": 25000,
            "targeting_criteria": {
                "job_titles": ["CTO", "VP Engineering"],
                "company_size": "100-1000",
                "industries": ["SaaS", "Technology"]
            },
            "timeline": {
                "start_day": 1,
                "ramp_up_days": 7,
                "active_days": 23
            },
            "success_metrics": ["CTR > 2%", "CPA < $150", "100 MQLs"],
            "rollout_sequence": [
                {"day": 1, "action": "Launch first ad set"},
                {"day": 7, "action": "Analyze and optimize"}
            ]
        }
    ],
    "total_budget": 50000,
    "launch_date": "2025-01-15",
    "sequence": [
        {"phase": "Week 1", "focus": "LinkedIn + Email launch"},
        {"phase": "Week 2", "focus": "Add Google Search"},
        {"phase": "Week 3-4", "focus": "Optimize and scale"}
    ]
}
"""

        response = self.generate_output(prompt, temperature=0.7, context=context)

        try:
            data = json.loads(response)

            # Create ChannelPlan objects
            channels = []
            for ch in data["channels"]:
                channel_plan = ChannelPlan(
                    channel=ch["channel"],
                    budget_allocation=ch["budget_allocation"],
                    targeting_criteria=ch["targeting_criteria"],
                    timeline=ch["timeline"],
                    success_metrics=ch["success_metrics"],
                    rollout_sequence=ch.get("rollout_sequence", []),
                )
                channels.append(channel_plan)

            # Create DistributionPlan
            plan = DistributionPlan(
                channels=channels,
                total_budget=data["total_budget"],
                launch_date=datetime.fromisoformat(data["launch_date"]),
                sequence=data["sequence"],
            )

            # Store in memory
            self.memory.set_distribution_plan(plan)
            self.log(f"Distribution plan created: {len(channels)} channels")

            return plan

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.log(f"Failed to parse distribution plan: {e}", "ERROR")
            raise

    def optimize_budget_allocation(
        self, performance_data: dict, current_allocation: dict
    ) -> dict[str, float]:
        """
        Optimize budget allocation based on performance.

        Args:
            performance_data: Channel performance metrics
            current_allocation: Current budget by channel

        Returns:
            Optimized budget allocation
        """
        self.log("Optimizing budget allocation based on performance...")

        context = {
            "Performance Data": json.dumps(performance_data, indent=2),
            "Current Allocation": json.dumps(current_allocation, indent=2),
        }

        prompt = """Analyze channel performance and recommend budget reallocation.

OPTIMIZATION CRITERIA:
1. Shift budget from underperforming to high-performing channels
2. Consider channel scalability (can it handle more budget?)
3. Maintain diversification (don't put all eggs in one basket)
4. Account for learning curves (new channels need time)

RULES:
- Don't cut any channel by more than 50%
- Don't increase any channel by more than 100%
- Maintain 10% contingency budget

Return optimized allocation as JSON:
{
    "channel_name": new_budget_amount,
    "rationale": "explanation of changes"
}
"""

        response = self.generate_output(prompt, temperature=0.6, context=context)

        try:
            optimized = json.loads(response)
            self.memory.write("optimized_budget_allocation", optimized)
            return optimized

        except json.JSONDecodeError:
            return current_allocation

    def _create_distribution_plan(self, task: AgentTask) -> AgentOutput:
        """Internal method for distribution plan creation."""
        icp = task.inputs.get("icp", {})
        budget = task.inputs.get("budget", 50000)
        timeline_days = task.inputs.get("timeline_days", 30)
        objectives = task.inputs.get("objectives", [])

        plan = self.create_distribution_plan(icp, budget, timeline_days, objectives)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"distribution_plan": plan.model_dump()},
            status=TaskStatus.COMPLETED,
        )

    def _define_targeting(self, task: AgentTask) -> AgentOutput:
        """Internal method for targeting criteria definition."""
        # Simplified implementation
        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"message": "Targeting criteria definition - to be implemented"},
            status=TaskStatus.COMPLETED,
        )

    def _generic_execution(self, task: AgentTask) -> AgentOutput:
        """Generic task execution."""
        response = self.generate_output(task.description, context=task.inputs)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"result": response},
            status=TaskStatus.COMPLETED,
        )
