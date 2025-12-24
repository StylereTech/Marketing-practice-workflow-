"""LLM interface layer supporting multiple providers."""

import os
from typing import Any, Optional
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def complete(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.7
    ) -> str:
        """Generate completion from the LLM."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, model: str = "gpt-4-turbo-preview", api_key: Optional[str] = None):
        """
        Initialize OpenAI provider.

        Args:
            model: Model identifier
            api_key: Optional API key (defaults to OPENAI_API_KEY env var)
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")

        self.model = model
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def complete(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.7
    ) -> str:
        """Generate completion using OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(
        self, model: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None
    ):
        """
        Initialize Anthropic provider.

        Args:
            model: Model identifier
            api_key: Optional API key (defaults to ANTHROPIC_API_KEY env var)
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

        self.model = model
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))

    def complete(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.7
    ) -> str:
        """Generate completion using Anthropic."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature,
        )
        return response.content[0].text


class LLMInterface:
    """
    High-level LLM interface that abstracts provider details.

    Automatically selects provider based on available API keys.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize LLM interface.

        Args:
            provider: Optional provider name ('openai' or 'anthropic')
            model: Optional model identifier
            api_key: Optional API key
        """
        # Auto-detect provider if not specified
        if provider is None:
            if os.getenv("ANTHROPIC_API_KEY"):
                provider = "anthropic"
            elif os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            else:
                raise ValueError(
                    "No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY"
                )

        # Initialize provider
        if provider == "openai":
            self.provider: LLMProvider = OpenAIProvider(
                model=model or os.getenv("ORCHESTRATOR_MODEL", "gpt-4-turbo-preview"),
                api_key=api_key,
            )
        elif provider == "anthropic":
            self.provider = AnthropicProvider(
                model=model or "claude-3-5-sonnet-20241022", api_key=api_key
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def generate(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.7
    ) -> str:
        """
        Generate completion from LLM.

        Args:
            system_prompt: System/instruction prompt
            user_prompt: User input prompt
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        return self.provider.complete(system_prompt, user_prompt, temperature)

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_format: str,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate structured output (JSON, YAML, etc.).

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            output_format: Expected format description
            temperature: Sampling temperature

        Returns:
            Structured output
        """
        enhanced_system = f"{system_prompt}\n\nIMPORTANT: Return output in {output_format} format."
        return self.generate(enhanced_system, user_prompt, temperature)
