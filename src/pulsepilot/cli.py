"""Command-line interface for PulsePilot."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

from pulsepilot.core.models import CompanyBrief, ICPDefinition, CampaignConstraints, CampaignInput
from pulsepilot.workflows.campaign import CampaignWorkflow

app = typer.Typer(help="🚀 PulsePilot - Multi-Agent Marketing Orchestration")
console = Console()


@app.command()
def campaign(
    company: str = typer.Option(..., help="Company name"),
    product: str = typer.Option(..., help="Product description"),
    icp: str = typer.Option(..., help="ICP title (e.g., 'VP Engineering')"),
    industry: str = typer.Option(..., help="Target industry"),
    budget: float = typer.Option(..., help="Campaign budget in USD"),
    timeline: int = typer.Option(30, help="Campaign timeline in days"),
    auto_approve: bool = typer.Option(True, help="Auto-approve checkpoints"),
) -> None:
    """Create and run a new marketing campaign."""

    console.print(f"\n[bold cyan]Creating campaign for {company}...[/bold cyan]\n")

    # Build campaign input
    campaign_input = CampaignInput(
        company=CompanyBrief(
            name=company,
            industry=industry,
            product_description=product,
        ),
        icp=ICPDefinition(
            title=icp,
            industry=industry,
            company_size="100-1000",
            pain_points=["Enter pain points in future version"],
        ),
        constraints=CampaignConstraints(
            total_budget=budget,
            timeline_days=timeline,
        ),
        objectives=["Generate leads", "Book demos"],
    )

    # Run workflow
    workflow = CampaignWorkflow(campaign_input, auto_approve=auto_approve)
    results = workflow.run()

    # Display results
    console.print(f"\n[bold green]✅ Campaign completed![/bold green]")
    console.print(f"Campaign ID: {results['campaign_id']}\n")


@app.command()
def list_campaigns() -> None:
    """List all campaigns."""
    from pathlib import Path
    import json

    memory_path = Path("memory_store")

    if not memory_path.exists():
        console.print("[yellow]No campaigns found[/yellow]")
        return

    table = Table(title="PulsePilot Campaigns")
    table.add_column("Campaign ID", style="cyan")
    table.add_column("Created", style="green")
    table.add_column("Version", style="yellow")

    for campaign_file in memory_path.glob("*.json"):
        with open(campaign_file) as f:
            data = json.load(f)
            metadata = data.get("metadata", {})
            table.add_row(
                campaign_file.stem,
                metadata.get("created_at", "Unknown"),
                str(metadata.get("version", "1")),
            )

    console.print(table)


@app.command()
def version() -> None:
    """Show PulsePilot version."""
    from pulsepilot import __version__

    console.print(f"PulsePilot v{__version__}")


if __name__ == "__main__":
    app()
