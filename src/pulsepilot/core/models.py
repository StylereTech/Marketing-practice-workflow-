"""Core data models for PulsePilot."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class CampaignPhase(str, Enum):
    """Campaign execution phases."""

    INITIALIZATION = "initialization"
    STRATEGY = "strategy"
    EXECUTION = "execution"
    LAUNCH = "launch"
    FEEDBACK = "feedback"
    CLOSED = "closed"


class AgentRole(str, Enum):
    """Agent roles in the system."""

    ORCHESTRATOR = "orchestrator"
    MARKET_INTEL = "market_intelligence"
    CONTENT = "content_production"
    DISTRIBUTION = "distribution_growth"
    ANALYTICS = "analytics_learning"


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_APPROVAL = "requires_approval"


# Campaign Configuration Models


class CompanyBrief(BaseModel):
    """Company information and context."""

    name: str
    industry: str
    product_description: str
    unique_value_prop: Optional[str] = None
    brand_voice: Optional[str] = "Professional and approachable"
    competitors: list[str] = Field(default_factory=list)


class ICPDefinition(BaseModel):
    """Ideal Customer Profile definition."""

    title: str
    industry: str
    company_size: str
    pain_points: list[str] = Field(default_factory=list)
    buying_triggers: list[str] = Field(default_factory=list)
    decision_criteria: list[str] = Field(default_factory=list)


class CampaignConstraints(BaseModel):
    """Campaign budget and timeline constraints."""

    total_budget: float
    timeline_days: int
    start_date: Optional[datetime] = None
    priority_channels: list[str] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)


class CampaignInput(BaseModel):
    """Complete campaign input specification."""

    company: CompanyBrief
    icp: ICPDefinition
    constraints: CampaignConstraints
    objectives: list[str] = Field(default_factory=list)
    additional_context: dict[str, Any] = Field(default_factory=dict)


# Agent Task Models


class AgentTask(BaseModel):
    """Task assigned to an agent."""

    task_id: str
    agent_role: AgentRole
    description: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class AgentOutput(BaseModel):
    """Output from an agent task."""

    task_id: str
    agent_role: AgentRole
    outputs: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Memory Models


class MessagingFramework(BaseModel):
    """Messaging framework from Market Intelligence agent."""

    value_proposition: str
    key_messages: list[str]
    pain_points: list[str]
    buying_triggers: list[str]
    proof_points: list[str] = Field(default_factory=list)
    objection_handling: dict[str, str] = Field(default_factory=dict)


class ContentAsset(BaseModel):
    """Content asset created by Content Production agent."""

    asset_id: str
    asset_type: str  # landing_page, linkedin_post, email, whitepaper
    title: str
    content: str
    variations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChannelPlan(BaseModel):
    """Distribution channel plan."""

    channel: str
    budget_allocation: float
    targeting_criteria: dict[str, Any]
    timeline: dict[str, Any]
    success_metrics: list[str]
    rollout_sequence: list[dict[str, Any]] = Field(default_factory=list)


class DistributionPlan(BaseModel):
    """Complete distribution plan from Distribution agent."""

    channels: list[ChannelPlan]
    total_budget: float
    launch_date: datetime
    sequence: list[dict[str, Any]]


class PerformanceMetrics(BaseModel):
    """Performance metrics tracked by Analytics agent."""

    campaign_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metrics: dict[str, float]  # CTR, CVR, CPA, etc.
    channel_breakdown: dict[str, dict[str, float]] = Field(default_factory=dict)
    insights: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class CampaignStrategy(BaseModel):
    """Overall campaign strategy from Orchestrator."""

    campaign_id: str
    campaign_name: str
    objectives: list[str]
    approach: str
    key_decisions: dict[str, str]
    success_criteria: list[str]
    risk_mitigation: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Campaign State


class CampaignState(BaseModel):
    """Complete state of a campaign."""

    campaign_id: str
    phase: CampaignPhase
    strategy: Optional[CampaignStrategy] = None
    messaging: Optional[MessagingFramework] = None
    assets: list[ContentAsset] = Field(default_factory=list)
    distribution_plan: Optional[DistributionPlan] = None
    performance: list[PerformanceMetrics] = Field(default_factory=list)
    tasks: list[AgentTask] = Field(default_factory=list)
    checkpoints_approved: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Checkpoint(BaseModel):
    """Human approval checkpoint."""

    checkpoint_id: str
    phase: CampaignPhase
    title: str
    description: str
    data_to_review: dict[str, Any]
    approved: bool = False
    feedback: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
