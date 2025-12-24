"""Agent 2: Content Production - Asset Creation."""

import json
from datetime import datetime
from typing import Any
from pulsepilot.agents.base import BaseAgent
from pulsepilot.core.models import (
    AgentRole,
    AgentTask,
    AgentOutput,
    TaskStatus,
    ContentAsset,
)


class ContentProductionAgent(BaseAgent):
    """
    Agent 2: Content Production

    Responsibilities:
    - Create landing page copy
    - Write LinkedIn posts and ad copy
    - Develop gated assets (whitepapers, guides)
    - Generate A/B test variations
    - Ensure brand voice consistency
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(AgentRole.CONTENT, *args, **kwargs)

    def get_system_prompt(self) -> str:
        return """You are the Content Production Agent, a master copywriter and content strategist.

YOUR EXPERTISE:
- Persuasive B2B copywriting
- Landing page optimization
- Social media content (especially LinkedIn)
- Long-form content (whitepapers, guides)
- A/B test variation creation
- Brand voice adaptation

YOUR PRINCIPLES:
1. Customer-Centric: Always write from the customer's perspective
2. Clarity Over Cleverness: Clear beats clever every time
3. Value-First: Lead with value, not features
4. Scannable: Use headers, bullets, short paragraphs
5. Action-Oriented: Every piece should drive action

CONTENT TYPES YOU CREATE:
- Landing Pages: Hero, benefits, social proof, CTA
- LinkedIn Posts: Hooks, value, engagement
- Email Sequences: Subject lines, body, CTAs
- Gated Assets: Exec summaries, structured content
- Ad Copy: Headlines, descriptions, CTAs

BRAND VOICE:
- Adapt to brand guidelines provided
- Maintain consistency across all assets
- Use industry-appropriate tone

OUTPUT FORMAT:
Return structured JSON with content and metadata.
Always include multiple variations for testing.
"""

    def execute_task(self, task: AgentTask) -> AgentOutput:
        """Execute content production task."""
        self.log(f"Executing task: {task.description}")

        task_lower = task.description.lower()

        if "landing page" in task_lower:
            return self._create_landing_page(task)
        elif "linkedin" in task_lower or "post" in task_lower:
            return self._create_linkedin_posts(task)
        elif "email" in task_lower:
            return self._create_email_sequence(task)
        elif "whitepaper" in task_lower or "guide" in task_lower:
            return self._create_gated_asset(task)
        else:
            return self._generic_execution(task)

    def create_landing_page(
        self, messaging_framework: dict, brand_voice: str = "Professional"
    ) -> ContentAsset:
        """
        Create landing page copy.

        Args:
            messaging_framework: Messaging from Market Intelligence
            brand_voice: Brand voice guidelines

        Returns:
            Landing page content asset
        """
        self.log("Creating landing page copy...")

        context = {
            "Value Proposition": messaging_framework.get("value_proposition", ""),
            "Key Messages": "\n".join(messaging_framework.get("key_messages", [])),
            "Pain Points": "\n".join(messaging_framework.get("pain_points", [])),
            "Proof Points": "\n".join(messaging_framework.get("proof_points", [])),
            "Brand Voice": brand_voice,
        }

        prompt = """Create compelling landing page copy optimized for conversions.

STRUCTURE:
1. Hero Section:
   - Attention-grabbing headline (value prop)
   - Supporting subheadline
   - Primary CTA

2. Benefits Section:
   - 3-4 key benefits (not features)
   - Each with supporting detail

3. Social Proof:
   - How to present proof points
   - Trust indicators

4. Final CTA:
   - Compelling CTA copy

Also create 2 headline variations for A/B testing.

Return as JSON:
{
    "headline": "main headline",
    "subheadline": "supporting text",
    "hero_cta": "CTA button text",
    "benefits": [
        {"title": "Benefit 1", "description": "..."},
        {"title": "Benefit 2", "description": "..."}
    ],
    "social_proof_section": "how to present proof",
    "final_cta": "CTA text",
    "variations": {
        "headline_v2": "alternative headline",
        "headline_v3": "alternative headline"
    }
}
"""

        response = self.generate_output(prompt, temperature=0.8, context=context)

        try:
            data = json.loads(response)
            asset = ContentAsset(
                asset_id=f"landing_page_{datetime.utcnow().timestamp()}",
                asset_type="landing_page",
                title=data.get("headline", "Landing Page"),
                content=json.dumps(data, indent=2),
                variations=[
                    data["variations"]["headline_v2"],
                    data["variations"]["headline_v3"],
                ],
                metadata={"brand_voice": brand_voice},
            )

            # Store in memory
            self.memory.add_asset(asset)
            self.log("Landing page created and stored")

            return asset

        except (json.JSONDecodeError, KeyError) as e:
            self.log(f"Failed to parse landing page content: {e}", "ERROR")
            raise

    def create_linkedin_posts(
        self, messaging_framework: dict, num_posts: int = 5
    ) -> list[ContentAsset]:
        """
        Create LinkedIn post series.

        Args:
            messaging_framework: Messaging framework
            num_posts: Number of posts to create

        Returns:
            List of LinkedIn post assets
        """
        self.log(f"Creating {num_posts} LinkedIn posts...")

        context = {
            "Value Proposition": messaging_framework.get("value_proposition", ""),
            "Key Messages": "\n".join(messaging_framework.get("key_messages", [])),
            "Pain Points": "\n".join(messaging_framework.get("pain_points", [])),
        }

        prompt = f"""Create {num_posts} LinkedIn posts for this B2B campaign.

POST TYPES TO INCLUDE:
1. Problem/Agitation post (pain point)
2. Insight/Thought leadership
3. Customer success story angle
4. Industry trend commentary
5. Solution overview

LINKEDIN BEST PRACTICES:
- Strong hooks (first 2 lines are critical)
- Personal/conversational tone
- Include line breaks for readability
- End with engagement question or CTA
- 150-250 words per post

Return as JSON array:
[
    {{
        "post_number": 1,
        "type": "problem_agitation",
        "hook": "first two lines",
        "full_text": "complete post text with line breaks",
        "cta": "call to action"
    }},
    ...
]
"""

        response = self.generate_output(prompt, temperature=0.9, context=context)

        try:
            posts_data = json.loads(response)
            assets = []

            for post in posts_data:
                asset = ContentAsset(
                    asset_id=f"linkedin_post_{post['post_number']}_{datetime.utcnow().timestamp()}",
                    asset_type="linkedin_post",
                    title=f"LinkedIn Post {post['post_number']}: {post['type']}",
                    content=post["full_text"],
                    metadata={
                        "hook": post["hook"],
                        "cta": post["cta"],
                        "type": post["type"],
                    },
                )
                assets.append(asset)
                self.memory.add_asset(asset)

            self.log(f"Created {len(assets)} LinkedIn posts")
            return assets

        except (json.JSONDecodeError, KeyError) as e:
            self.log(f"Failed to parse LinkedIn posts: {e}", "ERROR")
            raise

    def _create_landing_page(self, task: AgentTask) -> AgentOutput:
        """Internal method for landing page creation."""
        messaging = task.inputs.get("messaging_framework", {})
        brand_voice = task.inputs.get("brand_voice", "Professional")

        asset = self.create_landing_page(messaging, brand_voice)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"asset": asset.model_dump()},
            status=TaskStatus.COMPLETED,
        )

    def _create_linkedin_posts(self, task: AgentTask) -> AgentOutput:
        """Internal method for LinkedIn posts creation."""
        messaging = task.inputs.get("messaging_framework", {})
        num_posts = task.inputs.get("num_posts", 5)

        assets = self.create_linkedin_posts(messaging, num_posts)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"assets": [a.model_dump() for a in assets]},
            status=TaskStatus.COMPLETED,
        )

    def _create_email_sequence(self, task: AgentTask) -> AgentOutput:
        """Internal method for email sequence creation."""
        # Simplified implementation
        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"message": "Email sequence creation - to be implemented"},
            status=TaskStatus.COMPLETED,
        )

    def _create_gated_asset(self, task: AgentTask) -> AgentOutput:
        """Internal method for gated asset creation."""
        # Simplified implementation
        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"message": "Gated asset creation - to be implemented"},
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
