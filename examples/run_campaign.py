"""
Example: Run a complete PulsePilot campaign

This demonstrates the full 30-day campaign workflow from initialization to close.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pulsepilot.core.models import (
    CompanyBrief,
    ICPDefinition,
    CampaignConstraints,
    CampaignInput,
)
from pulsepilot.workflows.campaign import CampaignWorkflow


def main() -> None:
    """Run example B2B SaaS campaign."""

    # 1. Define Company Brief
    company = CompanyBrief(
        name="DataFlow",
        industry="B2B SaaS",
        product_description="Real-time data pipeline automation platform that helps engineering teams move data 10x faster with zero-code integrations.",
        unique_value_prop="The only data platform that auto-scales pipelines and self-heals errors without engineer intervention.",
        brand_voice="Technical but accessible, confident without being arrogant",
        competitors=["Fivetran", "Airbyte", "Stitch Data"],
    )

    # 2. Define ICP
    icp = ICPDefinition(
        title="VP of Engineering / CTO",
        industry="SaaS, E-commerce, FinTech",
        company_size="100-1000 employees",
        pain_points=[
            "Data engineers spend 70% of time on pipeline maintenance instead of analytics",
            "Pipeline failures cause hours of downtime and missed business insights",
            "Scaling data infrastructure requires expensive hiring and complex tools",
        ],
        buying_triggers=[
            "Recent data outage that impacted the business",
            "Planning to hire more data engineers but facing budget constraints",
            "Need to support new data-driven initiatives (ML, analytics, etc.)",
        ],
        decision_criteria=[
            "Proven reduction in engineering time spent on pipelines",
            "Reliability and uptime guarantees",
            "Easy integration with existing stack",
            "ROI within 6 months",
        ],
    )

    # 3. Define Budget and Timeline
    constraints = CampaignConstraints(
        total_budget=50000.0,  # $50K campaign
        timeline_days=30,  # 30-day campaign
        priority_channels=["LinkedIn", "Google Search"],
        constraints={
            "geographic_focus": "North America",
            "must_have_gated_asset": True,
        },
    )

    # 4. Create Campaign Input
    campaign_input = CampaignInput(
        company=company,
        icp=icp,
        constraints=constraints,
        objectives=[
            "Generate 100 marketing qualified leads (MQLs)",
            "Book 25 sales demos",
            "Achieve <$500 cost per MQL",
            "Build awareness among target personas on LinkedIn",
        ],
        additional_context={
            "recent_product_launch": "Just launched v2.0 with AI-powered auto-healing",
            "competitive_advantage": "Only platform with ML-based error prediction",
        },
    )

    # 5. Execute Campaign Workflow
    print("\n" + "=" * 60)
    print("🚀 PULSEPILOT CAMPAIGN EXECUTION DEMO")
    print("=" * 60 + "\n")

    workflow = CampaignWorkflow(
        campaign_input=campaign_input,
        auto_approve=True,  # Auto-approve checkpoints for demo
    )

    # Run the complete 30-day campaign workflow
    results = workflow.run()

    # 6. Display Results
    print("\n" + "=" * 60)
    print("📊 CAMPAIGN RESULTS")
    print("=" * 60)
    print(f"\nCampaign ID: {results['campaign_id']}")
    print(f"Status: {results['status']}")
    print(f"Assets Created: {results['assets_created']}")
    print(f"Channels Used: {results['channels_used']}")
    print(f"Performance Snapshots: {results['performance_snapshots']}")

    if results.get('strategy'):
        print(f"\nCampaign Name: {results['strategy']['campaign_name']}")
        print(f"Approach: {results['strategy']['approach']}")

    if results.get('messaging'):
        print(f"\nValue Proposition: {results['messaging']['value_proposition']}")

    print("\n" + "=" * 60)
    print("✅ Campaign workflow completed!")
    print("=" * 60 + "\n")

    # Show where data is stored
    print(f"📁 Campaign data saved to: memory_store/{results['campaign_id']}.json\n")


if __name__ == "__main__":
    main()
