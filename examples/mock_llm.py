import json
from typing import Any
from pulsepilot.core.llm import LLMProvider

class MockLLMProvider(LLMProvider):
    """Mock LLM provider for demonstration/testing."""

    def complete(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.7
    ) -> str:
        """Generate mock completions based on the prompt content."""
        
        user_prompt_lower = user_prompt.lower()

        # 1. Campaign Strategy (Orchestrator)
        if "comprehensive campaign strategy" in user_prompt_lower or "campaign_name" in user_prompt:
            return json.dumps({
                "campaign_name": "Operation Cloud Growth",
                "objectives": ["Generate 50 MQLs", "Book 15 demos", "Increase brand awareness"],
                "approach": "Multi-channel demand generation focusing on pain point agitation",
                "key_decisions": {
                    "channels": "LinkedIn and Email",
                    "messaging": "Focus on 'Scattered tools' pain point"
                },
                "success_criteria": ["50 MQLs", "$50 CPM"],
                "risk_mitigation": {
                    "Low engagement": "Pivot to A/B test variations"
                }
            })

        # 2. Messaging Framework (Market Intel)
        if "messaging framework" in user_prompt_lower or "value_proposition" in user_prompt:
            return json.dumps({
                "value_proposition": "Unified project management for remote teams",
                "key_messages": ["Stop switching apps", "Get visibility now", "Align your team"],
                "pain_points": ["Tool fatigue", "Siloed data", "Missed deadlines"],
                "buying_triggers": ["New CTO", "Remote transition"],
                "proof_points": ["Used by 500+ teams", "99.9% uptime"],
                "objection_handling": {
                    "Too expensive": "ROI in 3 months",
                    "Hard to switch": "One-click migration"
                }
            })

        # 3. Content - Landing Page (Content Agent)
        if "landing page" in user_prompt_lower:
            return json.dumps({
                "headline": "Stop Herding Cats. Start Managing Projects.",
                "subheadline": "The all-in-one platform for modern remote teams.",
                "hero_cta": "Start Free Trial",
                "benefits": [
                    {"title": "Centralized task hub", "description": "All your tasks in one place"},
                    {"title": "Real-time collaboration", "description": "Work together instantly"},
                    {"title": "Automated reporting", "description": "Save time on updates"}
                ],
                "social_proof_section": "Trusted by market leaders like CorpX and TechY",
                "final_cta": "Get Started Now",
                "variations": {
                    "headline_v2": "The Remote Team's Command Center",
                    "headline_v3": "Project Management, Simplified"
                }
            })

        # 4. Content - LinkedIn Posts (Content Agent)
        if "linkedin posts" in user_prompt_lower:
            return json.dumps([
                {
                    "post_number": 1,
                    "type": "problem_agitation",
                    "hook": "Are your tools scattering your team? 🤯",
                    "full_text": "Are your tools scattering your team? 🤯\n\nIt's time to unify. Stop the chaos and bring your projects under one roof.\n\n#ProjectManagement #RemoteWork",
                    "cta": "Link in bio"
                },
                {
                    "post_number": 2,
                    "type": "insight",
                    "hook": "Remote work shouldn't feel distant.",
                    "full_text": "Remote work shouldn't feel distant. Bridge the gap with better tools. 🌉\n\nSee how TechCorp does it.",
                    "cta": "Read more"
                },
                {
                    "post_number": 3,
                    "type": "problem_agitation",
                    "hook": "3 signs you've outgrown your spreadsheet. 📊",
                    "full_text": "3 signs you've outgrown your spreadsheet. 📊\n1. Version conflicts\n2. Broken formulas\n3. No mobile access\n\nUpgrade today.",
                    "cta": "Try for free"
                },
                {
                    "post_number": 4,
                    "type": "engagement",
                    "hook": "What's your biggest remote work challenge?",
                    "full_text": "What's your biggest remote work challenge? Let's discuss below! 👇",
                    "cta": "Comment below"
                },
                {
                    "post_number": 5,
                    "type": "solution",
                    "hook": "We just launched our new dashboard feature! 🚀",
                    "full_text": "We just launched our new dashboard feature! Check it out. 🚀\n\nVisualise your success like never before.",
                    "cta": "See demo"
                }
            ])

        # 5. Distribution Plan (Distribution Agent)
        if "distribution plan" in user_prompt_lower:
            return json.dumps({
                "channels": [
                    {
                        "channel": "LinkedIn Ads",
                        "budget_allocation": 15000.0,
                        "targeting_criteria": {"job_title": "Head of Operations"},
                        "timeline": {"start_day": 1, "active_days": 30},
                        "success_metrics": ["CTR", "CPL"],
                        "rollout_sequence": [{"day": 1, "action": "Launch Ads"}]
                    },
                    {
                        "channel": "Email Outbound",
                        "budget_allocation": 10000.0,
                        "targeting_criteria": {"industry": "Technology"},
                        "timeline": {"start_day": 5, "active_days": 25},
                        "success_metrics": ["Open Rate", "Reply Rate"],
                        "rollout_sequence": [{"day": 5, "action": "Start Campaign"}]
                    }
                ],
                "total_budget": 25000.0,
                "launch_date": "2023-10-01T00:00:00",
                "sequence": [
                    {"phase": "Week 1", "focus": "Launch Ads"},
                    {"phase": "Week 2", "focus": "Start Email"}
                ]
            })

        # 6. KPIs (Analytics Agent)
        if "define kpis" in user_prompt_lower or "kpi framework" in user_prompt_lower:
            return json.dumps({
                "north_star_metric": {
                    "name": "Pipeline Generated",
                    "target": "$500K",
                    "rationale": "Key revenue driver"
                },
                "primary_kpis": [
                    {
                        "name": "MQL Volume",
                        "target": 50,
                        "threshold_green": "> 50",
                        "threshold_yellow": "40-50",
                        "threshold_red": "< 40",
                        "measurement_frequency": "weekly"
                    },
                    {
                        "name": "Demos Booked",
                        "target": 15,
                        "threshold_green": "> 15",
                        "threshold_yellow": "10-15",
                        "threshold_red": "< 10",
                        "measurement_frequency": "weekly"
                    }
                ],
                "secondary_kpis": [],
                "data_sources": {"MQLs": "CRM"}
            })

        # 7. Performance Analysis (Analytics Agent)
        if "analyze" in user_prompt_lower and "performance" in user_prompt_lower:
            return json.dumps({
                "summary": "Campaign performing well overall.",
                "wins": ["High CTR on LinkedIn", "Low CPA"],
                "concerns": ["Lower email open rate"],
                "insights": [
                    "LinkedIn ads resonating with pain points (CTR 2.1%)",
                    "Email needs subject line A/B testing"
                ],
                "channel_breakdown": {
                    "LinkedIn Ads": {
                        "ctr": 2.1,
                        "cpa": 140.5
                    },
                    "Email Outbound": {
                        "open_rate": 0.25,
                        "reply_rate": 0.02
                    }
                }
            })

        # 8. Optimization Recommendations (Analytics Agent)
        if "optimization recommendations" in user_prompt_lower or "recommend specific optimizations" in user_prompt_lower:
            return json.dumps([
                {
                    "priority": 1,
                    "category": "budget",
                    "recommendation": "Shift $5k to LinkedIn Ads",
                    "rationale": "Better CPA performance",
                    "expected_impact": "+10 MQLs",
                    "effort": "low",
                    "how_to_test": "Monitor CPA for 1 week"
                },
                {
                    "priority": 2,
                    "category": "creative",
                    "recommendation": "Refresh ad visuals",
                    "rationale": "Frequency increasing",
                    "expected_impact": "Maintain CTR",
                    "effort": "medium",
                    "how_to_test": "A/B test new against old"
                }
            ])

        # Default fallback
        return json.dumps({"result": "Mock response for " + user_prompt[:20]})
