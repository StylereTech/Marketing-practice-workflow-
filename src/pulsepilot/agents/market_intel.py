"""Agent 1: Market Intelligence - ICP Refinement and Messaging."""

import json
from typing import Any
from pulsepilot.agents.base import BaseAgent
from pulsepilot.core.models import (
    AgentRole,
    AgentTask,
    AgentOutput,
    TaskStatus,
    MessagingFramework,
    ICPDefinition,
)


class MarketIntelligenceAgent(BaseAgent):
    """
    Agent 1: Market Intelligence

    Responsibilities:
    - Refine ICP pain points and buying triggers
    - Develop value proposition
    - Create messaging hierarchy
    - Define positioning and differentiation
    - Research competitive landscape
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(AgentRole.MARKET_INTEL, *args, **kwargs)

    def get_system_prompt(self) -> str:
        return """You are the Market Intelligence Agent, an expert in customer research and positioning.

YOUR EXPERTISE:
- Deep understanding of B2B buyer psychology
- ICP refinement and segmentation
- Value proposition development
- Competitive positioning
- Message architecture and hierarchy

YOUR RESPONSIBILITIES:
1. Refine ICP: Deep-dive into pain points, buying triggers, decision criteria
2. Value Proposition: Craft compelling, differentiated value props
3. Messaging Framework: Create message hierarchy from high-level to tactical
4. Positioning: Define how to position against competitors
5. Proof Points: Identify credible evidence for claims

APPROACH:
- Start with pain points, not product features
- Use jobs-to-be-done framework
- Identify emotional and rational buying triggers
- Create message hierarchy: Theme → Pillars → Supporting points
- Always include objection handling

OUTPUT REQUIREMENTS:
- Specific, actionable insights (not generic advice)
- Customer language (not company jargon)
- Quantifiable claims when possible
- Clear prioritization (what matters most)

Return structured JSON outputs when requested.
"""

    def execute_task(self, task: AgentTask) -> AgentOutput:
        """Execute market intelligence task."""
        self.log(f"Executing task: {task.description}")

        if "messaging" in task.description.lower() or "framework" in task.description.lower():
            return self._create_messaging_framework(task)
        elif "icp" in task.description.lower():
            return self._refine_icp(task)
        else:
            return self._generic_execution(task)

    def create_messaging_framework(self, icp: ICPDefinition, company_context: dict) -> MessagingFramework:
        """
        Create comprehensive messaging framework.

        Args:
            icp: ICP definition
            company_context: Company and product context

        Returns:
            Complete messaging framework
        """
        self.log("Creating messaging framework...")

        context = {
            "ICP": f"{icp.title} at {icp.company_size} companies in {icp.industry}",
            "Known Pain Points": "\n".join(f"- {pp}" for pp in icp.pain_points),
            "Buying Triggers": "\n".join(f"- {bt}" for bt in icp.buying_triggers),
            "Company": company_context.get("name", ""),
            "Product": company_context.get("product_description", ""),
            "Unique Value": company_context.get("unique_value_prop", ""),
        }

        prompt = """Create a comprehensive messaging framework for this campaign.

TASKS:
1. Refine the pain points - make them specific and emotionally resonant
2. Identify 3-5 key buying triggers (why buy now?)
3. Craft a compelling value proposition (one clear sentence)
4. Create message hierarchy:
   - 1 core theme
   - 3-4 supporting pillars
   - 2-3 proof points per pillar
5. Anticipate top 3 objections and responses

Return as JSON:
{
    "value_proposition": "one sentence value prop",
    "key_messages": ["theme", "pillar 1", "pillar 2", "pillar 3"],
    "pain_points": ["refined pain 1", "refined pain 2"],
    "buying_triggers": ["trigger 1", "trigger 2"],
    "proof_points": ["proof 1", "proof 2", "proof 3"],
    "objection_handling": {
        "objection": "response"
    }
}
"""

        response = self.generate_output(prompt, temperature=0.7, context=context)

        try:
            data = json.loads(response)
            framework = MessagingFramework(**data)

            # Store in memory
            self.memory.set_messaging(framework)
            self.log("Messaging framework created and stored")

            return framework

        except (json.JSONDecodeError, ValueError) as e:
            self.log(f"Failed to parse messaging framework: {e}", "ERROR")
            raise

    def refine_icp_profile(self, icp: ICPDefinition, additional_context: dict) -> dict[str, Any]:
        """
        Refine ICP with deeper insights.

        Args:
            icp: Initial ICP definition
            additional_context: Additional research context

        Returns:
            Refined ICP profile
        """
        self.log("Refining ICP profile...")

        context = {
            "Current ICP": icp.model_dump_json(indent=2),
            "Additional Context": json.dumps(additional_context, indent=2),
        }

        prompt = """Refine this ICP profile with deeper insights.

FOCUS AREAS:
1. Pain Points: Make them more specific and emotionally charged
2. Buying Triggers: What events trigger purchase consideration?
3. Decision Criteria: What factors drive vendor selection?
4. Day-in-the-Life: What does their typical day look like?
5. Success Metrics: How do they measure success?

Return enhanced ICP as JSON with additional fields.
"""

        response = self.generate_output(prompt, temperature=0.6, context=context)

        try:
            refined_icp = json.loads(response)
            self.memory.write("refined_icp_profile", refined_icp)
            return refined_icp

        except json.JSONDecodeError:
            return {"error": "Failed to parse refined ICP"}

    def _create_messaging_framework(self, task: AgentTask) -> AgentOutput:
        """Internal method for messaging framework creation."""
        icp = ICPDefinition(**task.inputs.get("icp", {}))
        company_context = task.inputs.get("company_context", {})

        framework = self.create_messaging_framework(icp, company_context)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"messaging_framework": framework.model_dump()},
            status=TaskStatus.COMPLETED,
        )

    def _refine_icp(self, task: AgentTask) -> AgentOutput:
        """Internal method for ICP refinement."""
        icp = ICPDefinition(**task.inputs.get("icp", {}))
        context = task.inputs.get("context", {})

        refined = self.refine_icp_profile(icp, context)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"refined_icp": refined},
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
