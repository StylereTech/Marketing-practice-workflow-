"""Agent: Social Media - Multi-AI Content Generation for Instagram & TikTok."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from pulsepilot.agents.base import BaseAgent
from pulsepilot.core.llm import LLMInterface
from pulsepilot.core.models import (
    AgentRole,
    AgentTask,
    AgentOutput,
    TaskStatus,
    ContentAsset,
)


class SocialMediaAgent(BaseAgent):
    """
    Social Media Agent - Multi-AI Collaboration

    Responsibilities:
    - Coordinate Claude, ChatGPT, and Gemini for content generation
    - Generate Instagram and TikTok posts
    - Ensure brand consistency across all content
    - Create content variations for A/B testing
    - Schedule posts for daily distribution
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(AgentRole.CONTENT, *args, **kwargs)
        self.role_name = "social_media"

        # Initialize all three AI providers
        self.claude = LLMInterface(provider="anthropic")
        self.chatgpt = LLMInterface(provider="openai")
        self.gemini = LLMInterface(provider="google")

    def get_system_prompt(self) -> str:
        return """You are the Social Media Agent, specializing in creating engaging content for Instagram and TikTok.

YOUR EXPERTISE:
- Visual-first content creation
- Short-form video scripting
- Hashtag strategy and trends
- Platform-specific best practices
- Brand voice consistency
- Engagement optimization

YOUR PRINCIPLES:
1. Visual Impact: Every post must be visually compelling
2. Authenticity: Content should feel genuine and relatable
3. Trend Awareness: Leverage current trends while staying on-brand
4. Action-Driven: Drive engagement through compelling CTAs
5. Platform-Native: Content optimized for each platform's algorithm

PLATFORMS:
- Instagram: Focus on aesthetics, storytelling, and community
- TikTok: Embrace trends, authenticity, and entertainment

OUTPUT FORMAT:
Return structured JSON with content, captions, hashtags, and posting strategy.
"""

    def execute_task(self, task: AgentTask) -> AgentOutput:
        """Execute social media content generation task."""
        self.log(f"Executing task: {task.description}")

        task_lower = task.description.lower()

        if "generate posts" in task_lower or "create posts" in task_lower:
            return self._generate_daily_posts(task)
        elif "brand consistency" in task_lower:
            return self._check_brand_consistency(task)
        else:
            return self._generic_execution(task)

    def generate_posts_multi_ai(
        self,
        brand_guide: Dict[str, Any],
        num_posts: int = 3,
        platforms: List[str] = ["instagram", "tiktok"]
    ) -> List[ContentAsset]:
        """
        Generate social media posts using all three AI systems in collaboration.

        Workflow:
        1. Claude: Strategic planning and brand alignment
        2. ChatGPT: Creative content generation
        3. Gemini: Refinement and optimization

        Args:
            brand_guide: Brand guidelines including tone, values, examples
            num_posts: Number of posts to generate (default 3 for daily schedule)
            platforms: Target platforms

        Returns:
            List of ContentAsset objects
        """
        self.log(f"Generating {num_posts} posts using multi-AI collaboration...")

        assets = []

        # Step 1: Claude develops the strategic foundation
        self.log("Step 1: Claude is developing content strategy...")
        strategy_prompt = f"""Based on this brand guide, create a strategic content plan for {num_posts} social media posts.

Brand Guide:
{json.dumps(brand_guide, indent=2)}

Platforms: {', '.join(platforms)}

For each post, define:
1. Content theme/angle
2. Target emotion/outcome
3. Key message
4. Visual concept
5. Timing recommendation (morning/afternoon/evening)

Return as JSON array:
[
    {{
        "post_number": 1,
        "theme": "...",
        "emotion": "...",
        "key_message": "...",
        "visual_concept": "...",
        "best_time": "..."
    }},
    ...
]
"""

        strategy_response = self.claude.generate(
            self.get_system_prompt(),
            strategy_prompt,
            temperature=0.7
        )

        try:
            strategy_data = json.loads(strategy_response)
        except json.JSONDecodeError:
            self.log("Failed to parse Claude's strategy, using fallback", "WARNING")
            strategy_data = [{"post_number": i+1, "theme": "Brand showcase", "emotion": "inspiration"}
                           for i in range(num_posts)]

        # Step 2: ChatGPT creates the actual content
        self.log("Step 2: ChatGPT is creating content...")
        for i, strategy in enumerate(strategy_data[:num_posts]):
            content_prompt = f"""Create engaging social media content based on this strategy:

Strategy:
{json.dumps(strategy, indent=2)}

Brand Guide:
{json.dumps(brand_guide, indent=2)}

Platforms: {', '.join(platforms)}

Generate:
1. Caption (Instagram: 125-150 words, TikTok: 100 words max)
2. Primary hashtags (8-12 relevant tags)
3. Hook (first line - must grab attention)
4. Call-to-action
5. Visual description (for content creators)
6. TikTok script (if TikTok is included, 15-30 seconds)

Return as JSON:
{{
    "caption_instagram": "...",
    "caption_tiktok": "...",
    "hook": "...",
    "hashtags": ["tag1", "tag2", ...],
    "cta": "...",
    "visual_description": "...",
    "tiktok_script": "..."
}}
"""

            content_response = self.chatgpt.generate(
                "You are a creative social media content creator specializing in Instagram and TikTok.",
                content_prompt,
                temperature=0.9
            )

            try:
                content_data = json.loads(content_response)
            except json.JSONDecodeError:
                self.log(f"Failed to parse ChatGPT's content for post {i+1}", "WARNING")
                continue

            # Step 3: Gemini refines and ensures brand consistency
            self.log(f"Step 3: Gemini is refining post {i+1}...")
            refinement_prompt = f"""Review and refine this social media content to ensure it perfectly aligns with the brand.

Original Content:
{json.dumps(content_data, indent=2)}

Brand Guide:
{json.dumps(brand_guide, indent=2)}

Refinement Checklist:
1. Brand voice alignment
2. Tone consistency
3. Message clarity
4. Hashtag relevance
5. CTA effectiveness
6. Visual coherence

Make subtle improvements while preserving the creative direction. Return the refined version as JSON with the same structure, plus add:
- "brand_score": 0-100 (how well it aligns with brand)
- "refinements_made": ["list of changes"]
"""

            refined_response = self.gemini.generate(
                "You are a brand consistency expert specializing in social media content quality assurance.",
                refinement_prompt,
                temperature=0.3
            )

            try:
                refined_data = json.loads(refined_response)
            except json.JSONDecodeError:
                self.log(f"Failed to parse Gemini's refinement, using ChatGPT version", "WARNING")
                refined_data = content_data

            # Create assets for each platform
            for platform in platforms:
                caption_key = f"caption_{platform}"
                caption = refined_data.get(caption_key, refined_data.get("caption_instagram", ""))

                asset = ContentAsset(
                    asset_id=f"social_{platform}_{i+1}_{datetime.utcnow().timestamp()}",
                    asset_type=f"{platform}_post",
                    title=f"{platform.capitalize()} Post {i+1}: {strategy.get('theme', 'Brand Content')}",
                    content=caption,
                    metadata={
                        "platform": platform,
                        "post_number": i + 1,
                        "strategy": strategy,
                        "hook": refined_data.get("hook", ""),
                        "hashtags": refined_data.get("hashtags", []),
                        "cta": refined_data.get("cta", ""),
                        "visual_description": refined_data.get("visual_description", ""),
                        "tiktok_script": refined_data.get("tiktok_script", "") if platform == "tiktok" else "",
                        "best_time": strategy.get("best_time", "afternoon"),
                        "brand_score": refined_data.get("brand_score", 85),
                        "refinements": refined_data.get("refinements_made", []),
                        "ai_collaboration": {
                            "strategist": "Claude",
                            "creator": "ChatGPT",
                            "refiner": "Gemini"
                        }
                    },
                )

                assets.append(asset)
                self.memory.add_asset(asset)

                self.log(f"Created {platform} post {i+1} (Brand Score: {refined_data.get('brand_score', 85)})")

        self.log(f"Generated {len(assets)} social media posts using multi-AI collaboration")
        return assets

    def check_brand_consistency(
        self,
        content: str,
        brand_guide: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if content aligns with brand guidelines.

        Args:
            content: Content to check
            brand_guide: Brand guidelines

        Returns:
            Dictionary with consistency score and feedback
        """
        self.log("Checking brand consistency...")

        prompt = f"""Analyze this content against the brand guidelines and provide a detailed consistency report.

Content:
{content}

Brand Guide:
{json.dumps(brand_guide, indent=2)}

Evaluate:
1. Voice/Tone alignment (0-100)
2. Message consistency (0-100)
3. Visual alignment (0-100)
4. Values alignment (0-100)
5. Overall brand score (0-100)

Return as JSON:
{{
    "overall_score": 0-100,
    "voice_tone_score": 0-100,
    "message_score": 0-100,
    "visual_score": 0-100,
    "values_score": 0-100,
    "feedback": "detailed feedback",
    "suggestions": ["improvement 1", "improvement 2", ...],
    "approved": true/false
}}
"""

        response = self.claude.generate(
            "You are a brand consistency expert.",
            prompt,
            temperature=0.3
        )

        try:
            result = json.loads(response)
            self.log(f"Brand consistency check complete: {result.get('overall_score', 0)}/100")
            return result
        except json.JSONDecodeError:
            self.log("Failed to parse brand consistency check", "ERROR")
            return {
                "overall_score": 50,
                "approved": False,
                "feedback": "Unable to complete consistency check"
            }

    def _generate_daily_posts(self, task: AgentTask) -> AgentOutput:
        """Internal method for generating daily posts."""
        brand_guide = task.inputs.get("brand_guide", {})
        num_posts = task.inputs.get("num_posts", 3)
        platforms = task.inputs.get("platforms", ["instagram", "tiktok"])

        assets = self.generate_posts_multi_ai(brand_guide, num_posts, platforms)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={
                "assets": [a.model_dump() for a in assets],
                "summary": f"Generated {len(assets)} posts using Claude, ChatGPT, and Gemini collaboration"
            },
            status=TaskStatus.COMPLETED,
        )

    def _check_brand_consistency(self, task: AgentTask) -> AgentOutput:
        """Internal method for brand consistency checking."""
        content = task.inputs.get("content", "")
        brand_guide = task.inputs.get("brand_guide", {})

        result = self.check_brand_consistency(content, brand_guide)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs=result,
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
