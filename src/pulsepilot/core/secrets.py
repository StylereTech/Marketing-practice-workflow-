"""Secure secrets management with support for multiple cloud providers."""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class SecretProvider(str, Enum):
    """Available secret provider types."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ENV = "env"


class SecretsManagerInterface(ABC):
    """Abstract base class for secrets management providers."""

    @abstractmethod
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a secret value.

        Args:
            secret_name: Name/key of the secret
            default: Default value if secret not found

        Returns:
            Secret value or default
        """
        pass

    @abstractmethod
    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """
        Store a secret value.

        Args:
            secret_name: Name/key of the secret
            secret_value: Value to store

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def delete_secret(self, secret_name: str) -> bool:
        """
        Delete a secret.

        Args:
            secret_name: Name/key of the secret

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """
        Rotate a secret to a new value.

        Args:
            secret_name: Name/key of the secret
            new_value: New secret value

        Returns:
            True if successful
        """
        pass

    def get_secret_dict(self, secret_name: str) -> Dict[str, Any]:
        """
        Retrieve a secret that contains JSON data.

        Args:
            secret_name: Name/key of the secret

        Returns:
            Parsed dictionary
        """
        secret_value = self.get_secret(secret_name)
        if secret_value:
            try:
                return json.loads(secret_value)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse secret {secret_name} as JSON")
                return {}
        return {}


class AWSSecretsManager(SecretsManagerInterface):
    """AWS Secrets Manager implementation."""

    def __init__(self, region_name: Optional[str] = None):
        """
        Initialize AWS Secrets Manager.

        Args:
            region_name: AWS region (defaults to AWS_DEFAULT_REGION env var)
        """
        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError:
            raise ImportError(
                "AWS Secrets Manager requires boto3. "
                "Install with: pip install boto3"
            )

        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.client = boto3.client("secretsmanager", region_name=self.region_name)
        self.ClientError = ClientError
        logger.info(f"Initialized AWS Secrets Manager in region {self.region_name}")

    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return response.get("SecretString")
        except self.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                logger.warning(f"Secret {secret_name} not found in AWS Secrets Manager")
                return default
            logger.error(f"Error retrieving secret {secret_name}: {e}")
            return default

    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Store secret in AWS Secrets Manager."""
        try:
            # Try to update existing secret
            self.client.put_secret_value(
                SecretId=secret_name,
                SecretString=secret_value
            )
            logger.info(f"Updated secret {secret_name}")
            return True
        except self.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Create new secret
                try:
                    self.client.create_secret(
                        Name=secret_name,
                        SecretString=secret_value
                    )
                    logger.info(f"Created secret {secret_name}")
                    return True
                except self.ClientError as create_error:
                    logger.error(f"Failed to create secret {secret_name}: {create_error}")
                    return False
            logger.error(f"Failed to set secret {secret_name}: {e}")
            return False

    def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from AWS Secrets Manager."""
        try:
            self.client.delete_secret(
                SecretId=secret_name,
                ForceDeleteWithoutRecovery=False  # Allow 30-day recovery
            )
            logger.info(f"Deleted secret {secret_name}")
            return True
        except self.ClientError as e:
            logger.error(f"Failed to delete secret {secret_name}: {e}")
            return False

    def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """Rotate secret in AWS Secrets Manager."""
        # For manual rotation, we just update the value
        return self.set_secret(secret_name, new_value)


class AzureKeyVault(SecretsManagerInterface):
    """Azure Key Vault implementation."""

    def __init__(self, vault_url: Optional[str] = None):
        """
        Initialize Azure Key Vault.

        Args:
            vault_url: Key Vault URL (defaults to AZURE_KEY_VAULT_URL env var)
        """
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
        except ImportError:
            raise ImportError(
                "Azure Key Vault requires azure-keyvault-secrets and azure-identity. "
                "Install with: pip install azure-keyvault-secrets azure-identity"
            )

        self.vault_url = vault_url or os.getenv("AZURE_KEY_VAULT_URL")
        if not self.vault_url:
            raise ValueError("AZURE_KEY_VAULT_URL must be set")

        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=self.vault_url, credential=credential)
        logger.info(f"Initialized Azure Key Vault: {self.vault_url}")

    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve secret from Azure Key Vault."""
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.warning(f"Secret {secret_name} not found in Azure Key Vault: {e}")
            return default

    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Store secret in Azure Key Vault."""
        try:
            self.client.set_secret(secret_name, secret_value)
            logger.info(f"Set secret {secret_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to set secret {secret_name}: {e}")
            return False

    def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from Azure Key Vault."""
        try:
            delete_operation = self.client.begin_delete_secret(secret_name)
            delete_operation.wait()
            logger.info(f"Deleted secret {secret_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_name}: {e}")
            return False

    def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """Rotate secret in Azure Key Vault."""
        return self.set_secret(secret_name, new_value)


class GCPSecretManager(SecretsManagerInterface):
    """Google Cloud Secret Manager implementation."""

    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize Google Cloud Secret Manager.

        Args:
            project_id: GCP project ID (defaults to GCP_PROJECT_ID env var)
        """
        try:
            from google.cloud import secretmanager
        except ImportError:
            raise ImportError(
                "GCP Secret Manager requires google-cloud-secret-manager. "
                "Install with: pip install google-cloud-secret-manager"
            )

        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID must be set")

        self.client = secretmanager.SecretManagerServiceClient()
        self.project_path = f"projects/{self.project_id}"
        logger.info(f"Initialized GCP Secret Manager for project {self.project_id}")

    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve secret from GCP Secret Manager."""
        try:
            name = f"{self.project_path}/secrets/{secret_name}/versions/latest"
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.warning(f"Secret {secret_name} not found in GCP Secret Manager: {e}")
            return default

    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Store secret in GCP Secret Manager."""
        try:
            # Check if secret exists
            parent = self.project_path
            secret_path = f"{parent}/secrets/{secret_name}"

            try:
                self.client.get_secret(request={"name": secret_path})
                # Secret exists, add new version
                payload = secret_value.encode("UTF-8")
                self.client.add_secret_version(
                    request={
                        "parent": secret_path,
                        "payload": {"data": payload}
                    }
                )
                logger.info(f"Updated secret {secret_name}")
            except Exception:
                # Secret doesn't exist, create it
                secret = self.client.create_secret(
                    request={
                        "parent": parent,
                        "secret_id": secret_name,
                        "secret": {"replication": {"automatic": {}}}
                    }
                )
                # Add version
                payload = secret_value.encode("UTF-8")
                self.client.add_secret_version(
                    request={
                        "parent": secret.name,
                        "payload": {"data": payload}
                    }
                )
                logger.info(f"Created secret {secret_name}")

            return True
        except Exception as e:
            logger.error(f"Failed to set secret {secret_name}: {e}")
            return False

    def delete_secret(self, secret_name: str) -> bool:
        """Delete secret from GCP Secret Manager."""
        try:
            name = f"{self.project_path}/secrets/{secret_name}"
            self.client.delete_secret(request={"name": name})
            logger.info(f"Deleted secret {secret_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_name}: {e}")
            return False

    def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """Rotate secret in GCP Secret Manager."""
        return self.set_secret(secret_name, new_value)


class EnvironmentSecretsManager(SecretsManagerInterface):
    """Environment variables-based secrets manager (for local development)."""

    def __init__(self):
        """Initialize environment-based secrets manager."""
        logger.info("Using environment variables for secrets (local development mode)")

    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve secret from environment variables."""
        value = os.getenv(secret_name, default)
        if value is None:
            logger.warning(f"Secret {secret_name} not found in environment")
        return value

    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """Set environment variable (runtime only, not persistent)."""
        os.environ[secret_name] = secret_value
        logger.warning(
            f"Set secret {secret_name} in environment (not persistent). "
            "Consider using a cloud secrets manager for production."
        )
        return True

    def delete_secret(self, secret_name: str) -> bool:
        """Delete environment variable."""
        if secret_name in os.environ:
            del os.environ[secret_name]
            logger.info(f"Deleted secret {secret_name} from environment")
            return True
        return False

    def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """Rotate secret (update environment variable)."""
        return self.set_secret(secret_name, new_value)


class SecretsManagerFactory:
    """Factory for creating secrets manager instances."""

    @staticmethod
    def create(
        provider: Optional[SecretProvider] = None,
        **kwargs: Any
    ) -> SecretsManagerInterface:
        """
        Create a secrets manager instance.

        Args:
            provider: Provider type (auto-detected if not specified)
            **kwargs: Provider-specific configuration

        Returns:
            Secrets manager instance

        Raises:
            ValueError: If provider is invalid or required config is missing
        """
        # Auto-detect provider if not specified
        if provider is None:
            provider_str = os.getenv("SECRETS_PROVIDER", "env").lower()
            try:
                provider = SecretProvider(provider_str)
            except ValueError:
                logger.warning(
                    f"Invalid SECRETS_PROVIDER '{provider_str}', falling back to env"
                )
                provider = SecretProvider.ENV

        # Create provider instance
        if provider == SecretProvider.AWS:
            return AWSSecretsManager(**kwargs)
        elif provider == SecretProvider.AZURE:
            return AzureKeyVault(**kwargs)
        elif provider == SecretProvider.GCP:
            return GCPSecretManager(**kwargs)
        elif provider == SecretProvider.ENV:
            return EnvironmentSecretsManager()
        else:
            raise ValueError(f"Unknown provider: {provider}")


# Global secrets manager instance
_secrets_manager: Optional[SecretsManagerInterface] = None


def get_secrets_manager() -> SecretsManagerInterface:
    """
    Get or create the global secrets manager instance.

    Returns:
        Secrets manager instance
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManagerFactory.create()
    return _secrets_manager


def set_secrets_manager(manager: SecretsManagerInterface) -> None:
    """
    Set the global secrets manager instance.

    Args:
        manager: Secrets manager instance to use
    """
    global _secrets_manager
    _secrets_manager = manager


def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to get a secret.

    Args:
        secret_name: Name of the secret
        default: Default value if not found

    Returns:
        Secret value or default
    """
    return get_secrets_manager().get_secret(secret_name, default)
