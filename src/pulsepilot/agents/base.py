"""Base agent class for all PulsePilot agents."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from pulsepilot.core.memory import SharedMemory
from pulsepilot.core.llm import LLMInterface
from pulsepilot.core.models import AgentRole, AgentTask, AgentOutput, TaskStatus


class BaseAgent(ABC):
    """
    Abstract base class for all specialist agents.

    Each agent has access to:
    - Shared memory (for reading and writing campaign data)
    - LLM interface (for generating outputs)
    - Role identifier
    """

    def __init__(
        self,
        role: AgentRole,
        memory: SharedMemory,
        llm: Optional[LLMInterface] = None,
    ):
        """
        Initialize base agent.

        Args:
            role: Agent's role identifier
            memory: Shared memory instance
            llm: Optional LLM interface (creates default if not provided)
        """
        self.role = role
        self.memory = memory
        self.llm = llm or LLMInterface()

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the agent's system prompt.

        Returns:
            System prompt defining agent's role and capabilities
        """
        pass

    @abstractmethod
    def execute_task(self, task: AgentTask) -> AgentOutput:
        """
        Execute an assigned task.

        Args:
            task: Task to execute

        Returns:
            Task output
        """
        pass

    def read_memory(self, key: str, default: Any = None) -> Any:
        """
        Read from shared memory.

        Args:
            key: Memory key
            default: Default value if key doesn't exist

        Returns:
            Memory value
        """
        return self.memory.read(key, default)

    def write_memory(self, key: str, value: Any) -> None:
        """
        Write to shared memory.

        Args:
            key: Memory key
            value: Value to store
        """
        self.memory.write(key, value, agent_id=self.role.value)

    def generate_output(
        self, user_prompt: str, temperature: float = 0.7, context: Optional[dict] = None
    ) -> str:
        """
        Generate output using the LLM.

        Args:
            user_prompt: User/task prompt
            temperature: Sampling temperature
            context: Optional context to include

        Returns:
            Generated output
        """
        system_prompt = self.get_system_prompt()

        # Add context to user prompt if provided
        if context:
            context_str = "\n\n## CONTEXT\n"
            for key, value in context.items():
                context_str += f"\n{key}:\n{value}\n"
            user_prompt = context_str + "\n\n## TASK\n" + user_prompt

        return self.llm.generate(system_prompt, user_prompt, temperature)

    def log(self, message: str, level: str = "INFO") -> None:
        """
        Log agent activity.

        Args:
            message: Log message
            level: Log level
        """
        print(f"[{self.role.value.upper()}] {level}: {message}")
