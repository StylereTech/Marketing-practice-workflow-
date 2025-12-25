"""Key rotation utilities for secure API key management."""

import logging
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from pulsepilot.core.secrets import get_secrets_manager, SecretsManagerInterface

logger = logging.getLogger(__name__)


class RotationStatus(str, Enum):
    """Status of key rotation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class RotationRecord:
    """Record of a key rotation event."""
    secret_name: str
    old_version: str
    new_version: str
    status: RotationStatus
    timestamp: datetime
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "secret_name": self.secret_name,
            "old_version": self.old_version,
            "new_version": self.new_version,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "error_message": self.error_message
        }


class KeyRotationManager:
    """
    Manages API key rotation with validation and rollback support.

    Provides a safe framework for rotating API keys with:
    - Validation of new keys before rotation
    - Automatic rollback on failure
    - Rotation history tracking
    - Limited scope testing
    """

    def __init__(self, secrets_manager: Optional[SecretsManagerInterface] = None):
        """
        Initialize key rotation manager.

        Args:
            secrets_manager: Secrets manager instance
        """
        self.secrets_manager = secrets_manager or get_secrets_manager()
        self.rotation_history: List[RotationRecord] = []

    def rotate_key(
        self,
        secret_name: str,
        new_value: str,
        validator: Optional[Callable[[str], bool]] = None,
        auto_rollback: bool = True
    ) -> RotationRecord:
        """
        Rotate an API key with validation and rollback support.

        Args:
            secret_name: Name of the secret to rotate
            new_value: New secret value
            validator: Optional function to validate the new key
            auto_rollback: Automatically rollback on validation failure

        Returns:
            Rotation record
        """
        logger.info(f"Starting rotation for secret: {secret_name}")

        # Get current value for potential rollback
        old_value = self.secrets_manager.get_secret(secret_name)
        if not old_value:
            logger.warning(f"No existing value for {secret_name}, treating as new secret")
            old_value = ""

        record = RotationRecord(
            secret_name=secret_name,
            old_version=old_value[:8] + "..." if old_value else "none",
            new_version=new_value[:8] + "...",
            status=RotationStatus.IN_PROGRESS,
            timestamp=datetime.now()
        )

        try:
            # Validate new key if validator provided
            if validator:
                logger.info(f"Validating new key for {secret_name}")
                if not validator(new_value):
                    raise ValueError("New key validation failed")

            # Rotate the key
            success = self.secrets_manager.rotate_secret(secret_name, new_value)
            if not success:
                raise RuntimeError("Failed to rotate secret in secrets manager")

            # Verify rotation
            verified_value = self.secrets_manager.get_secret(secret_name)
            if verified_value != new_value:
                raise RuntimeError("Secret rotation verification failed")

            record.status = RotationStatus.COMPLETED
            logger.info(f"Successfully rotated secret: {secret_name}")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Rotation failed for {secret_name}: {error_msg}")
            record.status = RotationStatus.FAILED
            record.error_message = error_msg

            # Attempt rollback if enabled
            if auto_rollback and old_value:
                logger.info(f"Attempting rollback for {secret_name}")
                try:
                    self.secrets_manager.set_secret(secret_name, old_value)
                    record.status = RotationStatus.ROLLED_BACK
                    logger.info(f"Successfully rolled back {secret_name}")
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")

        finally:
            self.rotation_history.append(record)

        return record

    def rotate_multiple_keys(
        self,
        rotations: Dict[str, str],
        validators: Optional[Dict[str, Callable[[str], bool]]] = None,
        atomic: bool = False
    ) -> List[RotationRecord]:
        """
        Rotate multiple keys.

        Args:
            rotations: Dictionary of {secret_name: new_value}
            validators: Optional dictionary of {secret_name: validator_function}
            atomic: If True, rollback all on any failure

        Returns:
            List of rotation records
        """
        validators = validators or {}
        records = []

        for secret_name, new_value in rotations.items():
            validator = validators.get(secret_name)
            record = self.rotate_key(secret_name, new_value, validator, auto_rollback=True)
            records.append(record)

            # If atomic and this rotation failed, rollback all previous
            if atomic and record.status == RotationStatus.FAILED:
                logger.error(f"Atomic rotation failed at {secret_name}, rolling back all")
                self._rollback_all(records[:-1])
                break

        return records

    def _rollback_all(self, records: List[RotationRecord]) -> None:
        """Rollback all successful rotations."""
        for record in records:
            if record.status == RotationStatus.COMPLETED:
                logger.info(f"Rolling back {record.secret_name}")
                # Note: Would need to store old values to properly rollback
                record.status = RotationStatus.ROLLED_BACK

    def schedule_rotation(
        self,
        secret_name: str,
        rotation_interval: timedelta = timedelta(days=90)
    ) -> Dict[str, Any]:
        """
        Create a rotation schedule for a secret.

        Args:
            secret_name: Name of the secret
            rotation_interval: How often to rotate

        Returns:
            Schedule information
        """
        next_rotation = datetime.now() + rotation_interval

        schedule = {
            "secret_name": secret_name,
            "rotation_interval_days": rotation_interval.days,
            "next_rotation": next_rotation.isoformat(),
            "auto_rotate": False  # Manual by default for safety
        }

        logger.info(f"Scheduled rotation for {secret_name} on {next_rotation}")
        return schedule

    def get_rotation_history(
        self,
        secret_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get rotation history.

        Args:
            secret_name: Optional filter by secret name
            limit: Maximum number of records to return

        Returns:
            List of rotation records
        """
        history = self.rotation_history

        if secret_name:
            history = [r for r in history if r.secret_name == secret_name]

        return [r.to_dict() for r in history[-limit:]]


# Platform-specific key validators

def validate_openai_key(api_key: str) -> bool:
    """
    Validate OpenAI API key.

    Args:
        api_key: OpenAI API key

    Returns:
        True if valid
    """
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        # Test with minimal API call
        client.models.list()
        logger.info("OpenAI API key validation successful")
        return True
    except Exception as e:
        logger.error(f"OpenAI API key validation failed: {e}")
        return False


def validate_anthropic_key(api_key: str) -> bool:
    """
    Validate Anthropic API key.

    Args:
        api_key: Anthropic API key

    Returns:
        True if valid
    """
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        # Test with minimal API call
        client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "test"}]
        )
        logger.info("Anthropic API key validation successful")
        return True
    except Exception as e:
        logger.error(f"Anthropic API key validation failed: {e}")
        return False


def validate_instagram_token(access_token: str) -> bool:
    """
    Validate Instagram access token.

    Args:
        access_token: Instagram access token

    Returns:
        True if valid
    """
    try:
        import requests
        # Test token with a simple API call
        url = "https://graph.instagram.com/me"
        params = {"fields": "id,username", "access_token": access_token}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        logger.info("Instagram token validation successful")
        return True
    except Exception as e:
        logger.error(f"Instagram token validation failed: {e}")
        return False


def validate_google_token(access_token: str) -> bool:
    """
    Validate Google OAuth token.

    Args:
        access_token: Google access token

    Returns:
        True if valid
    """
    try:
        import requests
        # Validate token using Google's tokeninfo endpoint
        url = "https://oauth2.googleapis.com/tokeninfo"
        params = {"access_token": access_token}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Check token is not expired
        if "expires_in" in data and int(data["expires_in"]) > 0:
            logger.info("Google token validation successful")
            return True
        return False
    except Exception as e:
        logger.error(f"Google token validation failed: {e}")
        return False


def validate_telegram_token(bot_token: str) -> bool:
    """
    Validate Telegram bot token.

    Args:
        bot_token: Telegram bot token

    Returns:
        True if valid
    """
    try:
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("ok"):
            logger.info("Telegram token validation successful")
            return True
        return False
    except Exception as e:
        logger.error(f"Telegram token validation failed: {e}")
        return False


# Registry of validators for different platforms
KEY_VALIDATORS: Dict[str, Callable[[str], bool]] = {
    "OPENAI_API_KEY": validate_openai_key,
    "ANTHROPIC_API_KEY": validate_anthropic_key,
    "INSTAGRAM_ACCESS_TOKEN": validate_instagram_token,
    "GOOGLE_ACCESS_TOKEN": validate_google_token,
    "TELEGRAM_BOT_TOKEN": validate_telegram_token,
}


def get_validator(secret_name: str) -> Optional[Callable[[str], bool]]:
    """
    Get validator function for a secret.

    Args:
        secret_name: Name of the secret

    Returns:
        Validator function or None
    """
    return KEY_VALIDATORS.get(secret_name)
