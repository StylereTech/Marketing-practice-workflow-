"""Shared Memory System - Single Source of Truth for all agents."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from pulsepilot.core.models import (
    CampaignState,
    MessagingFramework,
    ContentAsset,
    DistributionPlan,
    PerformanceMetrics,
    CampaignStrategy,
)


class SharedMemory:
    """
    Shared memory system that all agents read from and write to.

    Prevents information silos by providing a single source of truth.
    Implements versioning and persistence for campaign data.
    """

    def __init__(self, campaign_id: str, persistence_path: Optional[Path] = None):
        """
        Initialize shared memory for a campaign.

        Args:
            campaign_id: Unique identifier for the campaign
            persistence_path: Optional path for persisting memory to disk
        """
        self.campaign_id = campaign_id
        self.persistence_path = persistence_path or Path("memory_store")
        self.persistence_path.mkdir(exist_ok=True)

        # Initialize memory structure
        self._memory: dict[str, Any] = {
            "brand_voice_rules": {},
            "icp_definition": {},
            "messaging_hierarchy": {},
            "approved_claims": [],
            "performance_data": [],
            "draft_assets": [],
            "channel_plans": [],
            "campaign_strategy": None,
            "tasks": [],
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "version": 1,
            },
        }

        # Load persisted state if exists
        self._load()

    def write(self, key: str, value: Any, agent_id: Optional[str] = None) -> None:
        """
        Write data to shared memory.

        Args:
            key: Memory key to write to
            value: Data to store
            agent_id: Optional agent identifier for audit trail
        """
        self._memory[key] = value
        self._memory["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        self._memory["metadata"]["version"] += 1

        if agent_id:
            if "write_history" not in self._memory["metadata"]:
                self._memory["metadata"]["write_history"] = []
            self._memory["metadata"]["write_history"].append({
                "agent": agent_id,
                "key": key,
                "timestamp": datetime.utcnow().isoformat(),
            })

        self._persist()

    def read(self, key: str, default: Any = None) -> Any:
        """
        Read data from shared memory.

        Args:
            key: Memory key to read
            default: Default value if key doesn't exist

        Returns:
            Stored value or default
        """
        return self._memory.get(key, default)

    def append(self, key: str, value: Any, agent_id: Optional[str] = None) -> None:
        """
        Append to a list in shared memory.

        Args:
            key: Memory key (must be a list)
            value: Item to append
            agent_id: Optional agent identifier
        """
        if key not in self._memory:
            self._memory[key] = []

        if not isinstance(self._memory[key], list):
            raise ValueError(f"Key '{key}' is not a list")

        self._memory[key].append(value)
        self._memory["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        self._memory["metadata"]["version"] += 1

        self._persist()

    def update_nested(self, key: str, nested_key: str, value: Any) -> None:
        """
        Update a nested dictionary value.

        Args:
            key: Top-level memory key
            nested_key: Nested key within the dictionary
            value: Value to set
        """
        if key not in self._memory:
            self._memory[key] = {}

        if not isinstance(self._memory[key], dict):
            raise ValueError(f"Key '{key}' is not a dictionary")

        self._memory[key][nested_key] = value
        self._memory["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        self._memory["metadata"]["version"] += 1

        self._persist()

    def get_all(self) -> dict[str, Any]:
        """
        Get complete memory state.

        Returns:
            Complete memory dictionary
        """
        return self._memory.copy()

    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear memory (use with caution).

        Args:
            key: Optional specific key to clear. If None, clears all.
        """
        if key:
            self._memory.pop(key, None)
        else:
            # Preserve metadata
            metadata = self._memory.get("metadata", {})
            self._memory.clear()
            self._memory["metadata"] = metadata

        self._persist()

    def snapshot(self) -> dict[str, Any]:
        """
        Create a point-in-time snapshot of memory.

        Returns:
            Immutable copy of current memory state
        """
        snapshot_data = self._memory.copy()
        snapshot_data["metadata"]["snapshot_at"] = datetime.utcnow().isoformat()
        return snapshot_data

    def _persist(self) -> None:
        """Persist memory to disk."""
        if not self.persistence_path:
            return

        file_path = self.persistence_path / f"{self.campaign_id}.json"

        try:
            with open(file_path, "w") as f:
                json.dump(self._memory, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Failed to persist memory: {e}")

    def _load(self) -> None:
        """Load persisted memory from disk."""
        if not self.persistence_path:
            return

        file_path = self.persistence_path / f"{self.campaign_id}.json"

        if file_path.exists():
            try:
                with open(file_path, "r") as f:
                    self._memory = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load persisted memory: {e}")

    # Convenience methods for structured data

    def set_strategy(self, strategy: CampaignStrategy) -> None:
        """Store campaign strategy."""
        self.write("campaign_strategy", strategy.model_dump(), agent_id="orchestrator")

    def get_strategy(self) -> Optional[CampaignStrategy]:
        """Retrieve campaign strategy."""
        data = self.read("campaign_strategy")
        return CampaignStrategy(**data) if data else None

    def set_messaging(self, messaging: MessagingFramework) -> None:
        """Store messaging framework."""
        self.write("messaging_hierarchy", messaging.model_dump(), agent_id="market_intel")

    def get_messaging(self) -> Optional[MessagingFramework]:
        """Retrieve messaging framework."""
        data = self.read("messaging_hierarchy")
        return MessagingFramework(**data) if data else None

    def add_asset(self, asset: ContentAsset) -> None:
        """Add content asset."""
        self.append("draft_assets", asset.model_dump(), agent_id="content")

    def get_assets(self) -> list[ContentAsset]:
        """Retrieve all content assets."""
        assets_data = self.read("draft_assets", [])
        return [ContentAsset(**a) for a in assets_data]

    def set_distribution_plan(self, plan: DistributionPlan) -> None:
        """Store distribution plan."""
        self.write("distribution_plan", plan.model_dump(), agent_id="distribution")

    def get_distribution_plan(self) -> Optional[DistributionPlan]:
        """Retrieve distribution plan."""
        data = self.read("distribution_plan")
        return DistributionPlan(**data) if data else None

    def add_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """Add performance metrics snapshot."""
        self.append("performance_data", metrics.model_dump(), agent_id="analytics")

    def get_performance_history(self) -> list[PerformanceMetrics]:
        """Retrieve performance metrics history."""
        metrics_data = self.read("performance_data", [])
        return [PerformanceMetrics(**m) for m in metrics_data]

    def get_latest_performance(self) -> Optional[PerformanceMetrics]:
        """Get most recent performance metrics."""
        history = self.get_performance_history()
        return history[-1] if history else None
