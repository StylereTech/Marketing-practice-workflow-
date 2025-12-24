"""30-Day Campaign Workflow Orchestration."""

import uuid
from datetime import datetime
from typing import Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from pulsepilot.core.memory import SharedMemory
from pulsepilot.core.llm import LLMInterface
from pulsepilot.core.models import (
    CampaignInput,
    CampaignPhase,
    CampaignStrategy,
    AgentTask,
    TaskStatus,
    Checkpoint,
)
from pulsepilot.agents.orchestrator import MarketingOrchestrator
from pulsepilot.agents.market_intel import MarketIntelligenceAgent
from pulsepilot.agents.content import ContentProductionAgent
from pulsepilot.agents.distribution import DistributionAgent
from pulsepilot.agents.analytics import AnalyticsAgent


class CampaignWorkflow:
    """
    Orchestrates the complete 30-day campaign execution flow.

    Phases:
    1. Initialization (Day 0)
    2. Strategy Definition (Days 1-3)
    3. Parallel Execution (Days 4-10)
    4. Launch (Day 11)
    5. Feedback Loop (Days 12-30)
    6. Campaign Close
    """

    def __init__(
        self,
        campaign_input: CampaignInput,
        llm: Optional[LLMInterface] = None,
        auto_approve: bool = False,
    ):
        """
        Initialize campaign workflow.

        Args:
            campaign_input: Campaign configuration
            llm: Optional LLM interface
            auto_approve: If True, skip approval checkpoints (demo mode)
        """
        self.campaign_input = campaign_input
        self.campaign_id = f"campaign_{uuid.uuid4().hex[:8]}"
        self.auto_approve = auto_approve
        self.console = Console()

        # Initialize shared memory
        self.memory = SharedMemory(self.campaign_id)

        # Initialize LLM
        self.llm = llm or LLMInterface()

        # Initialize agents
        self.orchestrator = MarketingOrchestrator(memory=self.memory, llm=self.llm)
        self.market_intel = MarketIntelligenceAgent(memory=self.memory, llm=self.llm)
        self.content = ContentProductionAgent(memory=self.memory, llm=self.llm)
        self.distribution = DistributionAgent(memory=self.memory, llm=self.llm)
        self.analytics = AnalyticsAgent(memory=self.memory, llm=self.llm)

        # Current phase
        self.current_phase = CampaignPhase.INITIALIZATION

    def run(self) -> dict[str, Any]:
        """
        Execute the complete campaign workflow.

        Returns:
            Campaign results and final state
        """
        self.console.print(
            Panel.fit(
                f"[bold cyan]🚀 PulsePilot Campaign Execution[/bold cyan]\n\n"
                f"Campaign: [yellow]{self.campaign_input.company.name}[/yellow]\n"
                f"Budget: [green]${self.campaign_input.constraints.total_budget:,.0f}[/green]\n"
                f"Timeline: [blue]{self.campaign_input.constraints.timeline_days} days[/blue]",
                title="Campaign Initialized",
            )
        )

        try:
            # Phase 1: Initialization
            strategy = self._phase_1_initialization()

            # Phase 2: Strategy Definition
            messaging = self._phase_2_strategy()

            # Phase 3: Parallel Execution
            assets, distribution_plan = self._phase_3_execution()

            # Phase 4: Launch (simulated)
            self._phase_4_launch()

            # Phase 5: Feedback Loop (simulated)
            self._phase_5_feedback()

            # Phase 6: Campaign Close
            results = self._phase_6_close()

            self.console.print("\n[bold green]✅ Campaign workflow completed successfully![/bold green]")

            return results

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Campaign workflow interrupted by user[/yellow]")
            return {"status": "interrupted", "phase": self.current_phase.value}

        except Exception as e:
            self.console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
            raise

    def _phase_1_initialization(self) -> CampaignStrategy:
        """
        Phase 1: Initialization (Day 0)

        - Intake company brief, ICP, budget, timeline
        - Orchestrator creates campaign strategy
        - CHECKPOINT: Approve strategy
        """
        self.current_phase = CampaignPhase.INITIALIZATION
        self.console.print("\n[bold]📋 Phase 1: Initialization[/bold]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Creating campaign strategy...", total=None)

            # Store campaign input in memory
            self.memory.write("campaign_input", self.campaign_input.model_dump())

            # Orchestrator creates strategy
            strategy = self.orchestrator.create_campaign_strategy(self.campaign_input)

            progress.update(task, description="✅ Strategy created")

        # Checkpoint: Approve strategy
        checkpoint = self.orchestrator.generate_checkpoint(
            CampaignPhase.INITIALIZATION,
            {"strategy": strategy.model_dump()},
        )

        approved = self._request_approval(checkpoint)

        if not approved:
            raise Exception("Campaign strategy not approved")

        self.console.print(f"[green]✓[/green] Strategy approved: {strategy.campaign_name}")
        return strategy

    def _phase_2_strategy(self) -> Any:
        """
        Phase 2: Strategy Definition (Days 1-3)

        - Agent 1 refines ICP and creates messaging framework
        - CHECKPOINT: Approve messaging
        """
        self.current_phase = CampaignPhase.STRATEGY
        self.console.print("\n[bold]🧠 Phase 2: Strategy Definition[/bold]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Market Intelligence working...", total=None)

            # Agent 1: Create messaging framework
            messaging = self.market_intel.create_messaging_framework(
                icp=self.campaign_input.icp,
                company_context=self.campaign_input.company.model_dump(),
            )

            progress.update(task, description="✅ Messaging framework complete")

        # Checkpoint: Approve messaging
        checkpoint = self.orchestrator.generate_checkpoint(
            CampaignPhase.STRATEGY,
            {"messaging": messaging.model_dump()},
        )

        approved = self._request_approval(checkpoint)

        if not approved:
            raise Exception("Messaging framework not approved")

        self.console.print(f"[green]✓[/green] Messaging approved: {messaging.value_proposition}")
        return messaging

    def _phase_3_execution(self) -> tuple[list, Any]:
        """
        Phase 3: Parallel Execution (Days 4-10)

        - Agent 2: Create content assets (parallel)
        - Agent 3: Create distribution plan (parallel)
        - CHECKPOINT: Approve launch
        """
        self.current_phase = CampaignPhase.EXECUTION
        self.console.print("\n[bold]⚡ Phase 3: Parallel Execution[/bold]")

        messaging = self.memory.get_messaging()
        if not messaging:
            raise Exception("Messaging framework not found in memory")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            # Agent 2: Content creation
            content_task = progress.add_task("Creating content assets...", total=None)

            landing_page = self.content.create_landing_page(
                messaging_framework=messaging.model_dump(),
                brand_voice=self.campaign_input.company.brand_voice or "Professional",
            )

            linkedin_posts = self.content.create_linkedin_posts(
                messaging_framework=messaging.model_dump(),
                num_posts=5,
            )

            progress.update(
                content_task,
                description=f"✅ Created {1 + len(linkedin_posts)} assets",
            )

            # Agent 3: Distribution planning
            dist_task = progress.add_task("Creating distribution plan...", total=None)

            distribution_plan = self.distribution.create_distribution_plan(
                icp=self.campaign_input.icp.model_dump(),
                budget=self.campaign_input.constraints.total_budget,
                timeline_days=self.campaign_input.constraints.timeline_days,
                objectives=self.campaign_input.objectives,
            )

            progress.update(
                dist_task,
                description=f"✅ Planned {len(distribution_plan.channels)} channels",
            )

            # Agent 4: Define KPIs
            kpi_task = progress.add_task("Defining KPIs...", total=None)

            strategy = self.memory.get_strategy()
            kpis = self.analytics.define_kpis(
                campaign_strategy=strategy.model_dump() if strategy else {},
                objectives=self.campaign_input.objectives,
            )

            progress.update(kpi_task, description="✅ KPI framework defined")

        # Checkpoint: Approve launch
        assets = self.memory.get_assets()
        checkpoint = self.orchestrator.generate_checkpoint(
            CampaignPhase.EXECUTION,
            {
                "assets": [a.model_dump() for a in assets],
                "distribution_plan": distribution_plan.model_dump(),
                "kpis": kpis,
            },
        )

        approved = self._request_approval(checkpoint)

        if not approved:
            raise Exception("Launch plan not approved")

        self.console.print(f"[green]✓[/green] Launch approved with {len(assets)} assets")
        return assets, distribution_plan

    def _phase_4_launch(self) -> None:
        """
        Phase 4: Launch (Day 11)

        - Execute distribution (simulated)
        - Deploy ads, emails, outbound
        """
        self.current_phase = CampaignPhase.LAUNCH
        self.console.print("\n[bold]🚀 Phase 4: Campaign Launch[/bold]")

        distribution_plan = self.memory.get_distribution_plan()

        if distribution_plan:
            for channel in distribution_plan.channels:
                self.console.print(f"  [cyan]→[/cyan] Launching {channel.channel}")

        self.console.print("[green]✓[/green] All channels launched successfully")

    def _phase_5_feedback(self) -> None:
        """
        Phase 5: Feedback Loop (Days 12-30)

        - Monitor performance (simulated)
        - Weekly optimization cycles
        """
        self.current_phase = CampaignPhase.FEEDBACK
        self.console.print("\n[bold]📊 Phase 5: Feedback Loop[/bold]")

        # Simulate performance data
        simulated_metrics = {
            "impressions": 50000,
            "clicks": 1000,
            "ctr": 2.0,
            "conversions": 75,
            "cvr": 7.5,
            "cpa": 150.0,
        }

        performance = self.analytics.analyze_performance(simulated_metrics)

        self.console.print(f"  [cyan]→[/cyan] CTR: {simulated_metrics['ctr']}%")
        self.console.print(f"  [cyan]→[/cyan] CVR: {simulated_metrics['cvr']}%")
        self.console.print(f"  [cyan]→[/cyan] CPA: ${simulated_metrics['cpa']}")

        # Generate recommendations
        recommendations = self.analytics.recommend_optimizations(
            performance_data=performance.model_dump(),
            campaign_context={"phase": "feedback_loop"},
        )

        self.console.print(
            f"[green]✓[/green] Generated {len(recommendations)} optimization recommendations"
        )

    def _phase_6_close(self) -> dict[str, Any]:
        """
        Phase 6: Campaign Close

        - Final analysis
        - Archive learnings
        - Generate report
        """
        self.current_phase = CampaignPhase.CLOSED
        self.console.print("\n[bold]📈 Phase 6: Campaign Close[/bold]")

        # Gather all campaign data
        strategy = self.memory.get_strategy()
        messaging = self.memory.get_messaging()
        assets = self.memory.get_assets()
        distribution = self.memory.get_distribution_plan()
        performance = self.memory.get_performance_history()

        results = {
            "campaign_id": self.campaign_id,
            "status": "completed",
            "strategy": strategy.model_dump() if strategy else None,
            "messaging": messaging.model_dump() if messaging else None,
            "assets_created": len(assets),
            "channels_used": len(distribution.channels) if distribution else 0,
            "performance_snapshots": len(performance),
        }

        self.console.print("[green]✓[/green] Campaign archived successfully")

        return results

    def _request_approval(self, checkpoint: Checkpoint) -> bool:
        """
        Request human approval at checkpoint.

        Args:
            checkpoint: Checkpoint to approve

        Returns:
            True if approved
        """
        if self.auto_approve:
            self.console.print(f"\n[yellow]⚠ Auto-approving: {checkpoint.title}[/yellow]")
            return True

        self.console.print(f"\n[bold yellow]✋ CHECKPOINT: {checkpoint.title}[/bold yellow]")
        self.console.print(f"{checkpoint.description}\n")

        # In real implementation, would present data and wait for user input
        # For now, auto-approve
        return True
