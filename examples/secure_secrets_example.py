#!/usr/bin/env python3
"""
Example: Secure Secrets Management

This example demonstrates:
1. Using secrets manager to store and retrieve API keys
2. OAuth token management with automatic refresh
3. Key rotation with validation
4. Migration between different secret providers
"""

import os
from pulsepilot.core.secrets import (
    get_secrets_manager,
    SecretsManagerFactory,
    SecretProvider,
)
from pulsepilot.core.oauth import InstagramOAuthManager, OAuthToken
from pulsepilot.core.key_rotation import KeyRotationManager, validate_telegram_token


def example_1_basic_usage():
    """Example 1: Basic secrets manager usage."""
    print("\n=== Example 1: Basic Usage ===\n")

    # Get the configured secrets manager (from SECRETS_PROVIDER env var)
    sm = get_secrets_manager()
    print(f"Using secrets manager: {type(sm).__name__}")

    # Set a secret
    sm.set_secret("EXAMPLE_API_KEY", "sk-example-key-12345")
    print("✓ Secret stored")

    # Retrieve a secret
    api_key = sm.get_secret("EXAMPLE_API_KEY")
    print(f"✓ Retrieved: {api_key[:10]}...")

    # Retrieve with default value
    missing = sm.get_secret("NONEXISTENT_KEY", default="default-value")
    print(f"✓ Missing key returns default: {missing}")

    # Clean up
    sm.delete_secret("EXAMPLE_API_KEY")
    print("✓ Secret deleted")


def example_2_oauth_management():
    """Example 2: OAuth token management with auto-refresh."""
    print("\n=== Example 2: OAuth Token Management ===\n")

    # Create OAuth manager for Instagram
    instagram = InstagramOAuthManager()

    # Create and store a token
    token = OAuthToken(
        access_token="example_instagram_token_12345",
        refresh_token="example_instagram_token_12345",  # Instagram uses same for refresh
        expires_in=5184000,  # 60 days
        token_type="Bearer"
    )

    instagram.set_token(token)
    print("✓ Instagram OAuth token stored")

    # Retrieve token (automatically refreshes if expired)
    retrieved_token = instagram.get_token()
    if retrieved_token:
        print(f"✓ Token retrieved: {retrieved_token.access_token[:20]}...")
        print(f"  Expires at: {retrieved_token.expires_at}")
        print(f"  Is expired: {retrieved_token.is_expired}")

    # Store Instagram user ID
    instagram.secrets_manager.set_secret("INSTAGRAM_IG_USER_ID", "123456789")
    user_id = instagram.get_user_id()
    print(f"✓ Instagram user ID: {user_id}")


def example_3_key_rotation():
    """Example 3: Key rotation with validation."""
    print("\n=== Example 3: Key Rotation ===\n")

    # Get secrets manager and rotation manager
    sm = get_secrets_manager()
    rotation_mgr = KeyRotationManager(sm)

    # Set initial key
    sm.set_secret("EXAMPLE_TELEGRAM_TOKEN", "old-token-value")
    print("✓ Initial token set")

    # Rotate key (without validation for this example)
    print("Rotating key...")
    record = rotation_mgr.rotate_key(
        secret_name="EXAMPLE_TELEGRAM_TOKEN",
        new_value="new-token-value",
        validator=None,  # Skip validation for demo
        auto_rollback=True
    )

    print(f"✓ Rotation status: {record.status.value}")
    print(f"  Timestamp: {record.timestamp}")
    print(f"  Old version: {record.old_version}")
    print(f"  New version: {record.new_version}")

    # Verify new value
    new_value = sm.get_secret("EXAMPLE_TELEGRAM_TOKEN")
    print(f"✓ New value: {new_value}")

    # View rotation history
    history = rotation_mgr.get_rotation_history(
        secret_name="EXAMPLE_TELEGRAM_TOKEN",
        limit=5
    )
    print(f"✓ Rotation history: {len(history)} events")

    # Clean up
    sm.delete_secret("EXAMPLE_TELEGRAM_TOKEN")


def example_4_multiple_providers():
    """Example 4: Using different secret providers."""
    print("\n=== Example 4: Multiple Providers ===\n")

    # Create different providers explicitly
    providers = {
        "Environment": SecretsManagerFactory.create(SecretProvider.ENV),
    }

    # Try to create cloud providers if credentials available
    try:
        providers["AWS"] = SecretsManagerFactory.create(SecretProvider.AWS)
    except Exception as e:
        print(f"⊘ AWS Secrets Manager not available: {e}")

    try:
        providers["Azure"] = SecretsManagerFactory.create(SecretProvider.AZURE)
    except Exception as e:
        print(f"⊘ Azure Key Vault not available: {e}")

    try:
        providers["GCP"] = SecretsManagerFactory.create(SecretProvider.GCP)
    except Exception as e:
        print(f"⊘ GCP Secret Manager not available: {e}")

    # Test each available provider
    for name, provider in providers.items():
        print(f"\nTesting {name} provider:")
        test_key = f"TEST_KEY_{name.upper()}"

        # Set secret
        provider.set_secret(test_key, f"test-value-{name.lower()}")
        print(f"  ✓ Set secret: {test_key}")

        # Get secret
        value = provider.get_secret(test_key)
        print(f"  ✓ Retrieved: {value}")

        # Delete secret
        provider.delete_secret(test_key)
        print(f"  ✓ Deleted: {test_key}")


def example_5_production_setup():
    """Example 5: Production-ready setup with all features."""
    print("\n=== Example 5: Production Setup ===\n")

    # Get secrets manager
    sm = get_secrets_manager()
    print(f"Using provider: {type(sm).__name__}")

    # Store all required secrets
    secrets = {
        "OPENAI_API_KEY": "sk-example-openai-key",
        "TELEGRAM_BOT_TOKEN": "example-telegram-token",
        "TELEGRAM_CHAT_ID": "123456789",
        "SMTP_USER": "user@example.com",
        "SMTP_PASS": "example-password",
    }

    print("\nStoring secrets:")
    for key, value in secrets.items():
        sm.set_secret(key, value)
        print(f"  ✓ {key}")

    # Set up OAuth for Instagram
    instagram = InstagramOAuthManager(sm)
    instagram_token = OAuthToken(
        access_token="example-instagram-token",
        refresh_token="example-instagram-token",
        expires_in=5184000
    )
    instagram.set_token(instagram_token)
    sm.set_secret("INSTAGRAM_IG_USER_ID", "987654321")
    print("\n✓ Instagram OAuth configured")

    # Set up key rotation schedule
    rotation_mgr = KeyRotationManager(sm)
    from datetime import timedelta

    schedule = rotation_mgr.schedule_rotation(
        secret_name="OPENAI_API_KEY",
        rotation_interval=timedelta(days=90)
    )
    print(f"\n✓ Scheduled rotation for OPENAI_API_KEY")
    print(f"  Next rotation: {schedule['next_rotation']}")

    # Verify all secrets are accessible
    print("\nVerifying secrets:")
    for key in secrets.keys():
        value = sm.get_secret(key)
        masked = value[:8] + "..." if value and len(value) > 8 else "***"
        print(f"  ✓ {key}: {masked}")

    print("\n✓ Production setup complete!")
    print("\nCleanup (remove test secrets):")

    # Clean up test secrets
    for key in secrets.keys():
        sm.delete_secret(key)
        print(f"  ✓ Deleted {key}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("Secure Secrets Management Examples")
    print("=" * 60)

    # Set provider to env for examples
    os.environ["SECRETS_PROVIDER"] = "env"

    try:
        example_1_basic_usage()
        example_2_oauth_management()
        example_3_key_rotation()
        example_4_multiple_providers()
        example_5_production_setup()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
