"""Agent 4: Analytics & Learning - Performance Monitoring and Optimization."""

import json
from datetime import datetime
from typing import Any
from pulsepilot.agents.base import BaseAgent
from pulsepilot.core.models import (
    AgentRole,
    AgentTask,
    AgentOutput,
    TaskStatus,
    PerformanceMetrics,
)


class AnalyticsAgent(BaseAgent):
    """
    Agent 4: Analytics & Learning

    Responsibilities:
    - Define KPIs and success metrics
    - Monitor campaign performance
    - Identify underperforming elements
    - Generate optimization recommendations
    - Report on ROI and attribution
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(AgentRole.ANALYTICS, *args, **kwargs)

    def get_system_prompt(self) -> str:
        return """You are the Analytics & Learning Agent, a data-driven marketing analyst.

YOUR EXPERTISE:
- KPI framework development
- Performance analysis and reporting
- Statistical significance testing
- Attribution modeling
- Optimization recommendations
- Predictive analytics

YOUR RESPONSIBILITIES:
1. Define KPIs: Set up measurement framework before launch
2. Monitor Signals: Track performance in real-time
3. Identify Issues: Flag underperformance early
4. Recommend Changes: Provide actionable optimization ideas
5. Report Insights: Translate data into business impact

KEY METRICS YOU TRACK:
- Awareness: Impressions, Reach, Brand Lift
- Engagement: CTR, Time on Page, Video Views
- Conversion: CVR, MQL, SQL, Opportunity
- Efficiency: CPA, CAC, ROAS, LTV:CAC
- Velocity: Time to MQL, Sales Cycle Length

ANALYSIS APPROACH:
1. Compare to benchmarks and goals
2. Look for patterns and anomalies
3. Consider statistical significance
4. Identify root causes, not just symptoms
5. Prioritize high-impact, low-effort fixes

REPORTING STYLE:
- Lead with insights, not data dumps
- Use clear visualizations (describe them)
- Include "So what?" implications
- Provide specific next actions

OUTPUT FORMAT:
Return structured JSON with metrics, insights, and recommendations.
"""

    def execute_task(self, task: AgentTask) -> AgentOutput:
        """Execute analytics task."""
        self.log(f"Executing task: {task.description}")

        task_lower = task.description.lower()

        if "kpi" in task_lower or "define" in task_lower:
            return self._define_kpis(task)
        elif "analyze" in task_lower or "performance" in task_lower:
            return self._analyze_performance(task)
        elif "recommend" in task_lower or "optimize" in task_lower:
            return self._recommend_optimizations(task)
        else:
            return self._generic_execution(task)

    def define_kpis(self, campaign_strategy: dict, objectives: list[str]) -> dict[str, Any]:
        """
        Define KPI framework for the campaign.

        Args:
            campaign_strategy: Campaign strategy from Orchestrator
            objectives: Campaign objectives

        Returns:
            KPI framework with targets
        """
        self.log("Defining KPI framework...")

        context = {
            "Campaign Strategy": json.dumps(campaign_strategy, indent=2),
            "Objectives": "\n".join(f"- {obj}" for obj in objectives),
        }

        prompt = """Define a comprehensive KPI framework for this campaign.

REQUIREMENTS:
1. Primary KPIs (2-3 most important metrics)
2. Secondary KPIs (supporting metrics)
3. Specific targets for each KPI
4. Measurement frequency
5. Data sources

FRAMEWORK LEVELS:
- North Star: One metric that matters most
- Primary: 2-3 key success indicators
- Secondary: 5-7 supporting metrics
- Diagnostic: Metrics to understand "why"

Include:
- Metric definitions
- Target values (with rationale)
- Benchmarks (if available)
- Red/yellow/green thresholds

Return as JSON:
{
    "north_star_metric": {
        "name": "Pipeline Generated",
        "target": "$500K",
        "rationale": "why this matters"
    },
    "primary_kpis": [
        {
            "name": "MQL Volume",
            "target": 100,
            "threshold_green": "> 100",
            "threshold_yellow": "75-100",
            "threshold_red": "< 75",
            "measurement_frequency": "weekly"
        }
    ],
    "secondary_kpis": [...],
    "data_sources": {
        "metric_name": "where to get data"
    }
}
"""

        response = self.generate_output(prompt, temperature=0.6, context=context)

        try:
            kpi_framework = json.loads(response)
            self.memory.write("kpi_framework", kpi_framework)
            self.log("KPI framework defined and stored")
            return kpi_framework

        except json.JSONDecodeError as e:
            self.log(f"Failed to parse KPI framework: {e}", "ERROR")
            raise

    def analyze_performance(self, metrics_data: dict[str, float]) -> PerformanceMetrics:
        """
        Analyze campaign performance data.

        Args:
            metrics_data: Raw metrics (CTR, CVR, CPA, etc.)

        Returns:
            Performance analysis with insights
        """
        self.log("Analyzing campaign performance...")

        # Get KPI framework for comparison
        kpi_framework = self.memory.read("kpi_framework", {})

        context = {
            "Current Metrics": json.dumps(metrics_data, indent=2),
            "KPI Targets": json.dumps(kpi_framework.get("primary_kpis", []), indent=2),
        }

        prompt = """Analyze this campaign performance data and provide insights.

ANALYSIS TASKS:
1. Compare actuals vs. targets
2. Identify what's working well
3. Identify what's underperforming
4. Look for patterns and trends
5. Flag any anomalies

INSIGHTS TO PROVIDE:
- Performance summary (high-level)
- Key wins (what's exceeding expectations)
- Key concerns (what's underperforming)
- Potential causes (hypotheses)
- Impact assessment (what matters most)

Return as JSON:
{
    "summary": "overall performance assessment",
    "wins": ["win 1", "win 2"],
    "concerns": ["concern 1", "concern 2"],
    "insights": [
        {
            "insight": "what we learned",
            "data": "supporting data",
            "implication": "what it means"
        }
    ],
    "channel_breakdown": {
        "channel_name": {
            "performance": "good/okay/poor",
            "key_metric": value,
            "vs_target": "+/- X%"
        }
    }
}
"""

        response = self.generate_output(prompt, temperature=0.6, context=context)

        try:
            analysis = json.loads(response)

            # Create PerformanceMetrics object
            performance = PerformanceMetrics(
                campaign_id=self.memory.campaign_id,
                metrics=metrics_data,
                channel_breakdown=analysis.get("channel_breakdown", {}),
                insights=analysis.get("insights", []),
                recommendations=[],  # Will be filled by recommend_optimizations
            )

            # Store in memory
            self.memory.add_performance_metrics(performance)
            self.log("Performance analysis complete")

            return performance

        except (json.JSONDecodeError, KeyError) as e:
            self.log(f"Failed to parse performance analysis: {e}", "ERROR")
            raise

    def recommend_optimizations(
        self, performance_data: dict, campaign_context: dict
    ) -> list[dict[str, Any]]:
        """
        Generate optimization recommendations.

        Args:
            performance_data: Current performance metrics
            campaign_context: Campaign context and assets

        Returns:
            Prioritized list of recommendations
        """
        self.log("Generating optimization recommendations...")

        context = {
            "Performance Data": json.dumps(performance_data, indent=2),
            "Campaign Context": json.dumps(campaign_context, indent=2),
        }

        prompt = """Based on performance data, recommend specific optimizations.

RECOMMENDATION CRITERIA:
1. High Impact: Will meaningfully improve results
2. Low Effort: Can be implemented quickly
3. Low Risk: Won't break what's working
4. Testable: Can measure the impact

AREAS TO CONSIDER:
- Creative (headlines, copy, images)
- Targeting (audience expansion/narrowing)
- Budget (reallocation across channels)
- Bidding (CPC, CPM optimization)
- Landing Pages (conversion optimization)
- Messaging (value prop refinement)

For each recommendation:
- What to change
- Why (based on data)
- Expected impact
- Implementation effort
- How to test

Return as JSON array (prioritized):
[
    {
        "priority": 1,
        "category": "creative",
        "recommendation": "specific action to take",
        "rationale": "why this will help",
        "expected_impact": "quantified if possible",
        "effort": "low/medium/high",
        "how_to_test": "testing approach"
    }
]
"""

        response = self.generate_output(prompt, temperature=0.7, context=context)

        try:
            recommendations = json.loads(response)
            self.memory.write("optimization_recommendations", recommendations)
            self.log(f"Generated {len(recommendations)} optimization recommendations")
            return recommendations

        except json.JSONDecodeError:
            return []

    def _define_kpis(self, task: AgentTask) -> AgentOutput:
        """Internal method for KPI definition."""
        strategy = task.inputs.get("strategy", {})
        objectives = task.inputs.get("objectives", [])

        kpis = self.define_kpis(strategy, objectives)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"kpi_framework": kpis},
            status=TaskStatus.COMPLETED,
        )

    def _analyze_performance(self, task: AgentTask) -> AgentOutput:
        """Internal method for performance analysis."""
        metrics_data = task.inputs.get("metrics", {})

        performance = self.analyze_performance(metrics_data)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"performance_analysis": performance.model_dump()},
            status=TaskStatus.COMPLETED,
        )

    def _recommend_optimizations(self, task: AgentTask) -> AgentOutput:
        """Internal method for optimization recommendations."""
        performance = task.inputs.get("performance_data", {})
        context = task.inputs.get("campaign_context", {})

        recommendations = self.recommend_optimizations(performance, context)

        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"recommendations": recommendations},
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
