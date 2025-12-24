"""
Simple Example: Quick campaign setup with minimal configuration
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pulsepilot.core.models import CompanyBrief, ICPDefinition, CampaignConstraints, CampaignInput
from pulsepilot.workflows.campaign import CampaignWorkflow
from pulsepilot.core.llm import LLMInterface
try:
    from mock_llm import MockLLMProvider
except ImportError:
    from examples.mock_llm import MockLLMProvider


def main() -> None:
    """Run a simple campaign with minimal setup."""

    # Initialize Mock LLM to avoid needing API keys
    # We pass a dummy key to satisfy the constructor, then swap the provider
    llm = LLMInterface(provider="openai", api_key="dummy")
    llm.provider = MockLLMProvider()

    # Quick setup
    campaign_input = CampaignInput(
        company=CompanyBrief(
            name="TechCorp",
            industry="B2B SaaS",
            product_description="Cloud-based project management platform for remote teams",
        ),
        icp=ICPDefinition(
            title="Head of Operations",
            industry="Technology",
            company_size="50-200 employees",
            pain_points=["Scattered tools", "Poor visibility", "Team misalignment"],
        ),
        constraints=CampaignConstraints(
            total_budget=25000.0,
            timeline_days=30,
        ),
        objectives=["Generate 50 MQLs", "Book 15 demos"],
    )

    # Run campaign
    workflow = CampaignWorkflow(campaign_input, llm=llm, auto_approve=True)
    results = workflow.run()

    print(f"\n✅ Campaign {results['campaign_id']} completed!")
    print(f"   Created {results['assets_created']} assets across {results['channels_used']} channels\n")


if __name__ == "__main__":
    main()
