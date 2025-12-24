"""Tests for agent implementations."""

import pytest
from pulsepilot.core.memory import SharedMemory
from pulsepilot.core.models import ICPDefinition, AgentTask, TaskStatus
from pulsepilot.agents.market_intel import MarketIntelligenceAgent
from pulsepilot.agents.orchestrator import MarketingOrchestrator


@pytest.fixture
def memory():
    """Create test memory instance."""
    return SharedMemory("test_campaign")


@pytest.fixture
def icp():
    """Create test ICP."""
    return ICPDefinition(
        title="VP Engineering",
        industry="SaaS",
        company_size="100-500",
        pain_points=["Pain 1", "Pain 2"],
        buying_triggers=["Trigger 1"],
    )


def test_market_intel_agent_initialization(memory):
    """Test Market Intelligence agent initialization."""
    agent = MarketIntelligenceAgent(memory=memory)
    assert agent.role.value == "market_intelligence"


def test_orchestrator_initialization(memory):
    """Test Orchestrator initialization."""
    orchestrator = MarketingOrchestrator(memory=memory)
    assert orchestrator.role.value == "orchestrator"


def test_agent_system_prompt(memory):
    """Test that agents have system prompts."""
    agent = MarketIntelligenceAgent(memory=memory)
    prompt = agent.get_system_prompt()
    assert len(prompt) > 0
    assert "Market Intelligence" in prompt


def test_memory_read_write(memory):
    """Test agent memory operations."""
    agent = MarketIntelligenceAgent(memory=memory)

    agent.write_memory("test_key", "test_value")
    value = agent.read_memory("test_key")

    assert value == "test_value"
