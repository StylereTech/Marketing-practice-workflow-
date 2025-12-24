"""24/7 Scheduler for PulsePilot - Monitors and optimizes active campaigns."""

import os
import time
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

from pulsepilot.workflows.campaign import CampaignWorkflow
from pulsepilot.core.models import CampaignPhase
from pulsepilot.core.llm import LLMInterface
from examples.mock_llm import MockLLMProvider  # Use mock by default for safety

# Load environment variables
load_dotenv()

console = Console()

def get_active_campaigns(memory_dir: str = "memory_store") -> list[str]:
    """List all campaign IDs that are in the feedback phase."""
    active_ids = []
    path = Path(memory_dir)
    if not path.exists():
        return []
    
    for file in path.glob("*.json"):
        try:
            with open(file, "r") as f:
                data = json.load(f)
                phase = data.get("current_phase")
                if phase == CampaignPhase.FEEDBACK.value:
                    active_ids.append(file.stem)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read {file}: {e}[/yellow]")
            
    return active_ids

def run_scheduler(interval_hours: float = 1.0):
    """Main scheduler loop."""
    console.print(f"[bold green]🚀 PulsePilot 24/7 Scheduler Started[/bold green]")
    console.print(f"Monitoring interval: {interval_hours} hours\n")

    # Setup LLM (using Mock for now)
    llm = LLMInterface(provider="openai", api_key="dummy")
    llm.provider = MockLLMProvider()

    while True:
        active_campaigns = get_active_campaigns()
        
        if not active_campaigns:
            console.print(f"[{datetime.now().strftime('%H:%M:%S')}] No active campaigns in Feedback phase. Waiting...")
        else:
            table = Table(title=f"Active Campaigns ({len(active_campaigns)})")
            table.add_column("Campaign ID", style="cyan")
            table.add_column("Last Run", style="magenta")
            
            for cid in active_campaigns:
                table.add_row(cid, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                # Initialize workflow for existing campaign
                try:
                    workflow = CampaignWorkflow(campaign_id=cid, llm=llm, auto_approve=True)
                    result = workflow.run_feedback_loop_step()
                    
                    if result:
                        console.print(f"[green]✅ New optimization findings for {cid}![/green]")
                        
                        # Prepare Telegram message
                        recs = result['recommendations']
                        msg = (
                            f"📊 *PulsePilot Daily Optimization Alert*\n\n"
                            f"Campaign: `{cid}`\n"
                            f"Current CTR: {result['metrics']['ctr']}%\n"
                            f"Current CPA: ${result['metrics']['cpa']}\n\n"
                            f"*Top Recommendations:*\n"
                        )
                        for r in recs[:3]:
                            msg += f"• {r['recommendation']} (Impact: {r['expected_impact']})\n"
                        
                        # Send via Telegram
                        workflow.deployment.push_to_telegram(msg)
                    else:
                        console.print(f"[blue]ℹ️ No new changes needed for {cid}[/blue]")
                        
                except Exception as e:
                    console.print(f"[bold red]❌ Failed to process {cid}: {e}[/bold red]")

            console.print(table)

        # Sleep until next check
        console.print(f"\nNext check in {interval_hours} hours...")
        time.sleep(interval_hours * 3600)

if __name__ == "__main__":
    # For demo purposes, we can set a shorter interval (e.g., 0.01 hours = 36 seconds)
    # In production, this would be 24 or 12 hours.
    import sys
    interval = 24.0
    if len(sys.argv) > 1:
        interval = float(sys.argv[1])
        
    run_scheduler(interval)

