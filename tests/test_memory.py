"""Tests for SharedMemory system."""

import pytest
from pulsepilot.core.memory import SharedMemory
from pulsepilot.core.models import MessagingFramework, CampaignStrategy


def test_memory_initialization():
    """Test memory initialization."""
    memory = SharedMemory("test_campaign")
    assert memory.campaign_id == "test_campaign"
    assert memory.read("brand_voice_rules") == {}


def test_write_and_read():
    """Test writing and reading from memory."""
    memory = SharedMemory("test_campaign")

    memory.write("test_key", "test_value")
    assert memory.read("test_key") == "test_value"


def test_append_to_list():
    """Test appending to a list in memory."""
    memory = SharedMemory("test_campaign")

    memory.append("test_list", "item1")
    memory.append("test_list", "item2")

    result = memory.read("test_list")
    assert result == ["item1", "item2"]


def test_messaging_framework():
    """Test storing and retrieving messaging framework."""
    memory = SharedMemory("test_campaign")

    framework = MessagingFramework(
        value_proposition="Test value prop",
        key_messages=["Message 1", "Message 2"],
        pain_points=["Pain 1"],
        buying_triggers=["Trigger 1"],
    )

    memory.set_messaging(framework)
    retrieved = memory.get_messaging()

    assert retrieved is not None
    assert retrieved.value_proposition == "Test value prop"
    assert len(retrieved.key_messages) == 2


def test_strategy_storage():
    """Test storing and retrieving campaign strategy."""
    memory = SharedMemory("test_campaign")

    strategy = CampaignStrategy(
        campaign_id="test_campaign",
        campaign_name="Test Campaign",
        objectives=["Obj 1", "Obj 2"],
        approach="Test approach",
        key_decisions={"decision1": "value1"},
        success_criteria=["Criterion 1"],
    )

    memory.set_strategy(strategy)
    retrieved = memory.get_strategy()

    assert retrieved is not None
    assert retrieved.campaign_name == "Test Campaign"
    assert len(retrieved.objectives) == 2
