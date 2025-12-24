"""Agent 0: Marketing Orchestrator - Campaign Coordinator."""

import json
from datetime import datetime
from typing import Any
from pulsepilot.agents.base import BaseAgent
from pulsepilot.core.models import (
    AgentRole,
    AgentTask,
    AgentOutput,
    TaskStatus,
    CampaignStrategy,
    CampaignInput,
    Checkpoint,
    CampaignPhase,
)


class MarketingOrchestrator(BaseAgent):
    """
    Agent 0: Marketing Orchestrator

    Responsibilities:
    - Strategic thinking and campaign planning
    - Delegating tasks to specialist agents
    - Synthesizing outputs from all agents
    - Managing campaign phases and checkpoints
    - Decision-making and coordination
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(AgentRole.ORCHESTRATOR, *args, **kwargs)

    def get_system_prompt(self) -> str:
        return """You are the Marketing Orchestrator, the strategic brain of the PulsePilot system.

YOUR ROLE:
- Develop overall campaign strategy
- Coordinate and delegate to specialist agents
- Synthesize outputs into cohesive campaign plans
- Make strategic decisions and trade-offs
- Manage campaign phases and timelines

YOUR THINKING PROCESS:
1. Strategic Analysis: Understand business context, ICP, and constraints
2. Decision Making: Choose optimal approaches (channels, messaging, tactics)
3. Delegation: Assign specialized tasks to appropriate agents
4. Synthesis: Combine specialist outputs into executable plans
5. Optimization: Monitor performance and adjust strategy

GUIDELINES:
- Think strategically, not tactically (leave tactics to specialist agents)
- Make data-driven decisions when possible
- Consider budget and timeline constraints
- Balance short-term results with long-term brand building
- Identify dependencies between tasks
- Flag decisions that require human approval

OUTPUT FORMAT:
Provide clear, structured outputs in JSON format when requested.
Include rationale for major decisions.
Highlight risks and mitigation strategies.
"""

    def execute_task(self, task: AgentTask) -> AgentOutput:
        """Execute orchestrator task."""
        self.log(f"Executing task: {task.description}")

        # Execute based on task type
        if "strategy" in task.description.lower():
            return self._create_campaign_strategy(task)
        elif "delegate" in task.description.lower():
            return self._delegate_to_specialists(task)
        elif "synthesize" in task.description.lower():
            return self._synthesize_outputs(task)
        else:
            return self._generic_execution(task)

    def create_campaign_strategy(self, campaign_input: CampaignInput) -> CampaignStrategy:
        """
        Create overall campaign strategy from inputs.

        Args:
            campaign_input: Campaign specifications

        Returns:
            Complete campaign strategy
        """
        self.log("Creating campaign strategy...")

        # Build context for LLM
        context = {
            "Company": f"{campaign_input.company.name} - {campaign_input.company.product_description}",
            "ICP": f"{campaign_input.icp.title} in {campaign_input.icp.industry}",
            "Budget": f"${campaign_input.constraints.total_budget:,.0f}",
            "Timeline": f"{campaign_input.constraints.timeline_days} days",
            "Objectives": "\n".join(f"- {obj}" for obj in campaign_input.objectives),
            "Pain Points": "\n".join(f"- {pp}" for pp in campaign_input.icp.pain_points),
        }

        prompt = f"""Create a comprehensive campaign strategy for this B2B marketing campaign.

REQUIREMENTS:
1. Define 3-5 clear campaign objectives aligned with business goals
2. Outline the strategic approach (demand gen, product launch, thought leadership, etc.)
3. Identify key decisions (channels, messaging angle, asset types)
4. Define success criteria (KPIs and targets)
5. Identify top 3 risks and mitigation strategies

Return your strategy as a JSON object with this structure:
{{
    "campaign_name": "descriptive name",
    "objectives": ["obj1", "obj2"],
    "approach": "overall strategic approach",
    "key_decisions": {{"decision_area": "decision and rationale"}},
    "success_criteria": ["criterion1", "criterion2"],
    "risk_mitigation": {{"risk": "mitigation strategy"}}
}}
"""

        response = self.generate_output(prompt, temperature=0.7, context=context)

        # Parse JSON response
        try:
            strategy_data = json.loads(response)
            strategy = CampaignStrategy(
                campaign_id=self.memory.campaign_id,
                campaign_name=strategy_data["campaign_name"],
                objectives=strategy_data["objectives"],
                approach=strategy_data["approach"],
                key_decisions=strategy_data["key_decisions"],
                success_criteria=strategy_data["success_criteria"],
                risk_mitigation=strategy_data.get("risk_mitigation", {}),
            )

            # Store in memory
            self.memory.set_strategy(strategy)
            self.log(f"Strategy created: {strategy.campaign_name}")

            return strategy

        except json.JSONDecodeError as e:
            self.log(f"Failed to parse strategy JSON: {e}", "ERROR")
            raise

    def generate_checkpoint(
        self, phase: CampaignPhase, data_to_review: dict[str, Any]
    ) -> Checkpoint:
        """
        Generate a human approval checkpoint.

        Args:
            phase: Campaign phase
            data_to_review: Data for human review

        Returns:
            Checkpoint for approval
        """
        checkpoint_titles = {
            CampaignPhase.INITIALIZATION: "Approve Campaign Strategy",
            CampaignPhase.STRATEGY: "Approve Messaging Framework",
            CampaignPhase.EXECUTION: "Approve Campaign Launch",
            CampaignPhase.FEEDBACK: "Review Performance Report",
        }

        checkpoint_descriptions = {
            CampaignPhase.INITIALIZATION: "Review and approve the overall campaign strategy, objectives, and approach.",
            CampaignPhase.STRATEGY: "Review and approve the ICP refinement, value proposition, and messaging hierarchy.",
            CampaignPhase.EXECUTION: "Review all campaign assets, distribution plan, and approve launch.",
            CampaignPhase.FEEDBACK: "Review performance data and approve optimization recommendations.",
        }

        return Checkpoint(
            checkpoint_id=f"{phase.value}_{datetime.utcnow().timestamp()}",
            phase=phase,
            title=checkpoint_titles.get(phase, "Approval Required"),
            description=checkpoint_descriptions.get(phase, "Review and approve to proceed."),
            data_to_review=data_to_review,
        )

    def _create_campaign_strategy(self, task: AgentTask) -> AgentOutput:
        """Internal method for strategy creation task."""
        campaign_input = CampaignInput(**task.inputs)
        strategy = self.create_campaign_strategy(campaign_input)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"strategy": strategy.model_dump()},
            status=TaskStatus.COMPLETED,
        )

    def _delegate_to_specialists(self, task: AgentTask) -> AgentOutput:
        """Internal method for delegation planning."""
        # This would create task assignments for specialist agents
        self.log("Planning specialist task delegation...")

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"delegation_plan": "Specialist tasks created"},
            status=TaskStatus.COMPLETED,
        )

    def _synthesize_outputs(self, task: AgentTask) -> AgentOutput:
        """Internal method for synthesizing specialist outputs."""
        self.log("Synthesizing outputs from all agents...")

        # Gather data from memory
        strategy = self.memory.get_strategy()
        messaging = self.memory.get_messaging()
        assets = self.memory.get_assets()
        distribution = self.memory.get_distribution_plan()

        synthesis = {
            "strategy": strategy.model_dump() if strategy else None,
            "messaging": messaging.model_dump() if messaging else None,
            "assets_count": len(assets),
            "distribution": distribution.model_dump() if distribution else None,
        }

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"synthesis": synthesis},
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
