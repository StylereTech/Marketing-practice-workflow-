# Secure API Key Management

This document explains PulsePilot's comprehensive secure API key management system, including secrets management, OAuth token handling, and key rotation.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Secrets Providers](#secrets-providers)
4. [Setup Instructions](#setup-instructions)
5. [OAuth Token Management](#oauth-token-management)
6. [Key Rotation](#key-rotation)
7. [Security Best Practices](#security-best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview

PulsePilot implements enterprise-grade security for managing API keys and credentials:

- **Multi-Provider Support**: AWS Secrets Manager, Azure Key Vault, Google Cloud Secret Manager
- **OAuth Token Management**: Automatic token refresh for Instagram, Facebook, and Google
- **Key Rotation**: Built-in support for rotating API keys with validation and rollback
- **Zero Hardcoding**: No API keys in code or version control
- **Environment Fallback**: Use environment variables for local development

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    PulsePilot Agent                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────────┐        ┌──────────────────┐         │
│  │ Deployment     │        │ LLM Providers    │         │
│  │ Agent          │        │ (OpenAI/Claude)  │         │
│  └────────┬───────┘        └────────┬─────────┘         │
│           │                         │                    │
│           └─────────┬───────────────┘                    │
│                     │                                    │
│         ┌───────────▼────────────┐                       │
│         │  Secrets Manager       │                       │
│         │  Factory               │                       │
│         └───────────┬────────────┘                       │
│                     │                                    │
│      ┌──────────────┼──────────────────┐                │
│      │              │                  │                 │
│  ┌───▼────┐   ┌────▼─────┐   ┌───────▼──────┐          │
│  │  AWS   │   │  Azure   │   │  GCP         │          │
│  │Secrets │   │Key Vault │   │Secret Manager│          │
│  └────────┘   └──────────┘   └──────────────┘          │
│                                                          │
│         ┌──────────────────────────────┐                │
│         │  OAuth Token Manager         │                │
│         │  - Instagram                 │                │
│         │  - Facebook                  │                │
│         │  - Google                    │                │
│         └──────────────────────────────┘                │
│                                                          │
│         ┌──────────────────────────────┐                │
│         │  Key Rotation Manager        │                │
│         │  - Validation                │                │
│         │  - Rollback                  │                │
│         └──────────────────────────────┘                │
└─────────────────────────────────────────────────────────┘
```

### Key Features

1. **Automatic Provider Detection**: Selects the appropriate secrets provider based on configuration
2. **Transparent Integration**: Existing code works without modification
3. **Graceful Fallback**: Falls back to environment variables if cloud provider is unavailable
4. **Encrypted Storage**: All cloud providers encrypt secrets at rest

## Secrets Providers

### Environment Variables (Local Development)

**Best for**: Local development, testing

**Setup**:
```bash
# .env
SECRETS_PROVIDER=env
OPENAI_API_KEY=sk-...
INSTAGRAM_ACCESS_TOKEN=...
```

**Pros**:
- Simple setup
- No additional services required
- Good for development

**Cons**:
- Not secure for production
- No encryption at rest
- No audit logging

### AWS Secrets Manager

**Best for**: AWS-hosted applications, AWS-centric infrastructure

**Setup**:

1. **Install dependencies**:
```bash
poetry install -E aws
# or
pip install boto3
```

2. **Configure AWS credentials**:
```bash
aws configure
# or use IAM roles for EC2/ECS/Lambda
```

3. **Set environment variable**:
```bash
export SECRETS_PROVIDER=aws
export AWS_DEFAULT_REGION=us-east-1
```

4. **Store secrets**:
```python
from pulsepilot.core.secrets import get_secrets_manager

sm = get_secrets_manager()
sm.set_secret("OPENAI_API_KEY", "sk-...")
sm.set_secret("INSTAGRAM_ACCESS_TOKEN", "...")
```

Or use AWS CLI:
```bash
aws secretsmanager create-secret \
    --name OPENAI_API_KEY \
    --secret-string "sk-..."
```

**Features**:
- Automatic rotation (with Lambda)
- Encryption with AWS KMS
- Fine-grained IAM permissions
- Audit logging with CloudTrail
- Replication across regions

**IAM Permissions Required**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:PutSecretValue",
        "secretsmanager:CreateSecret",
        "secretsmanager:DeleteSecret"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:*"
    }
  ]
}
```

### Azure Key Vault

**Best for**: Azure-hosted applications, Microsoft ecosystem

**Setup**:

1. **Install dependencies**:
```bash
poetry install -E azure
# or
pip install azure-keyvault-secrets azure-identity
```

2. **Configure Azure authentication**:
```bash
az login
# or use managed identity for Azure VMs
```

3. **Set environment variables**:
```bash
export SECRETS_PROVIDER=azure
export AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/
```

4. **Store secrets**:
```python
from pulsepilot.core.secrets import get_secrets_manager

sm = get_secrets_manager()
sm.set_secret("OPENAI-API-KEY", "sk-...")  # Note: use hyphens, not underscores
```

Or use Azure CLI:
```bash
az keyvault secret set \
    --vault-name your-vault \
    --name OPENAI-API-KEY \
    --value "sk-..."
```

**Features**:
- Hardware security modules (HSMs)
- Azure AD integration
- Soft delete and purge protection
- Automatic key rotation
- Audit logging

**Required Permissions**:
- Key Vault Secrets Officer (for full access)
- Or custom role with: Get, Set, Delete secrets

### Google Cloud Secret Manager

**Best for**: GCP-hosted applications, Google Cloud ecosystem

**Setup**:

1. **Install dependencies**:
```bash
poetry install -E gcp
# or
pip install google-cloud-secret-manager
```

2. **Configure GCP authentication**:
```bash
gcloud auth application-default login
# or use service account key file
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

3. **Set environment variables**:
```bash
export SECRETS_PROVIDER=gcp
export GCP_PROJECT_ID=your-project-id
```

4. **Store secrets**:
```python
from pulsepilot.core.secrets import get_secrets_manager

sm = get_secrets_manager()
sm.set_secret("OPENAI_API_KEY", "sk-...")
```

Or use gcloud CLI:
```bash
echo -n "sk-..." | gcloud secrets create OPENAI_API_KEY \
    --data-file=- \
    --replication-policy="automatic"
```

**Features**:
- Automatic replication
- Versioning
- IAM integration
- Audit logging with Cloud Audit Logs
- Encryption with Cloud KMS

**Required IAM Permissions**:
```
roles/secretmanager.secretAccessor  # Read secrets
roles/secretmanager.secretVersionManager  # Create/update
```

## Setup Instructions

### Initial Setup

1. **Choose your secrets provider** based on your infrastructure:
   - Local development: `env`
   - AWS infrastructure: `aws`
   - Azure infrastructure: `azure`
   - GCP infrastructure: `gcp`

2. **Install required dependencies**:
```bash
# For AWS
poetry install -E aws

# For Azure
poetry install -E azure

# For GCP
poetry install -E gcp

# For all providers
poetry install -E all-secrets
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and set SECRETS_PROVIDER
```

4. **Migrate existing secrets**:

If you have secrets in `.env`, migrate them to your secrets manager:

```python
from pulsepilot.core.secrets import get_secrets_manager
from dotenv import load_dotenv
import os

# Load from .env
load_dotenv()

# Get secrets manager
sm = get_secrets_manager()

# Migrate secrets
secrets_to_migrate = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    # ... add all your secrets
]

for secret_name in secrets_to_migrate:
    value = os.getenv(secret_name)
    if value:
        sm.set_secret(secret_name, value)
        print(f"Migrated {secret_name}")
```

### Using Secrets in Code

The secrets manager is integrated transparently. Your existing code works without modification:

```python
from pulsepilot.agents.deployment import DeploymentAgent
from pulsepilot.core.llm import LLMInterface

# Secrets are automatically fetched from the configured provider
agent = DeploymentAgent(...)
llm = LLMInterface()  # API keys loaded from secrets manager
```

Manual access:

```python
from pulsepilot.core.secrets import get_secret

api_key = get_secret("OPENAI_API_KEY")
```

## OAuth Token Management

PulsePilot includes automatic OAuth token refresh for social media platforms.

### Supported Platforms

1. **Instagram** (via Facebook Graph API)
2. **Facebook** (Page access tokens)
3. **Google** (YouTube, Analytics, etc.)

### Setting Up OAuth

#### Instagram

1. **Get initial OAuth token** from Facebook Developer Portal:
   - Go to Facebook Developer Portal
   - Create an Instagram Business app
   - Generate a long-lived access token

2. **Store token and credentials**:

```python
from pulsepilot.core.oauth import InstagramOAuthManager, OAuthToken
from datetime import datetime
import time

# Create OAuth manager
instagram = InstagramOAuthManager()

# Create token object
token = OAuthToken(
    access_token="YOUR_ACCESS_TOKEN",
    refresh_token="YOUR_ACCESS_TOKEN",  # Instagram uses same token for refresh
    expires_in=5184000,  # 60 days
    token_type="Bearer"
)

# Store token
instagram.set_token(token)

# Store Instagram user ID
instagram.secrets_manager.set_secret("INSTAGRAM_IG_USER_ID", "your_instagram_user_id")
```

3. **Use with automatic refresh**:

```python
from pulsepilot.agents.deployment import DeploymentAgent

agent = DeploymentAgent(...)
# OAuth tokens are automatically refreshed when needed
result = agent.push_to_instagram("Check out our new product!", "https://example.com/image.jpg")
```

#### Facebook

1. **Get Page Access Token** from Facebook Developer Portal

2. **Store token**:

```python
from pulsepilot.core.oauth import FacebookOAuthManager, OAuthToken

facebook = FacebookOAuthManager()

token = OAuthToken(
    access_token="YOUR_PAGE_ACCESS_TOKEN",
    expires_in=5184000,  # 60 days
    token_type="Bearer"
)

facebook.set_token(token)
facebook.secrets_manager.set_secret("FACEBOOK_PAGE_ID", "your_page_id")

# Store OAuth app credentials for token refresh
facebook.secrets_manager.set_secret(
    "FACEBOOK_OAUTH_CREDENTIALS",
    '{"app_id": "your_app_id", "app_secret": "your_app_secret"}'
)
```

#### Google

1. **Create OAuth 2.0 credentials** in Google Cloud Console

2. **Get initial authorization code** and exchange for tokens

3. **Store token**:

```python
from pulsepilot.core.oauth import GoogleOAuthManager, OAuthToken

google = GoogleOAuthManager()

token = OAuthToken(
    access_token="YOUR_ACCESS_TOKEN",
    refresh_token="YOUR_REFRESH_TOKEN",
    expires_in=3600,  # 1 hour
    token_type="Bearer",
    scope="https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/analytics"
)

google.set_token(token)

# Store OAuth client credentials for token refresh
google.secrets_manager.set_secret(
    "GOOGLE_OAUTH_CREDENTIALS",
    '{"client_id": "your_client_id", "client_secret": "your_client_secret"}'
)
```

### Token Lifecycle

```
┌─────────────────────────────────────────────────┐
│  Application requests OAuth token               │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  OAuth Manager checks expiration                │
│  (considers expired if < 5 min remaining)       │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────┴─────────┐
         │                  │
         ▼                  ▼
    ┌────────┐         ┌─────────┐
    │ Valid  │         │ Expired │
    └───┬────┘         └────┬────┘
        │                   │
        │                   ▼
        │       ┌─────────────────────────┐
        │       │ Refresh token           │
        │       │ - Call platform API     │
        │       │ - Get new access token  │
        │       └────┬────────────────────┘
        │            │
        │            ▼
        │       ┌─────────────────────────┐
        │       │ Save new token          │
        │       │ - Update secrets manager│
        │       │ - Update cache          │
        │       └────┬────────────────────┘
        │            │
        └────────────┴──────────┐
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Return valid token    │
                    └───────────────────────┘
```

## Key Rotation

### Overview

The Key Rotation Manager provides safe API key rotation with:
- **Validation**: Test new keys before activation
- **Rollback**: Automatic rollback on failure
- **History**: Track all rotation events
- **Scheduling**: Plan rotation schedules

### Rotating a Single Key

```python
from pulsepilot.core.key_rotation import KeyRotationManager, validate_openai_key

# Create rotation manager
rotation_mgr = KeyRotationManager()

# Rotate with validation
record = rotation_mgr.rotate_key(
    secret_name="OPENAI_API_KEY",
    new_value="sk-new-key-here",
    validator=validate_openai_key,  # Validates before activating
    auto_rollback=True  # Rollback on failure
)

# Check result
if record.status == "completed":
    print(f"✓ Key rotated successfully at {record.timestamp}")
else:
    print(f"✗ Rotation failed: {record.error_message}")
```

### Rotating Multiple Keys (Atomic)

```python
from pulsepilot.core.key_rotation import (
    KeyRotationManager,
    validate_openai_key,
    validate_anthropic_key
)

rotation_mgr = KeyRotationManager()

# Rotate multiple keys atomically (all or nothing)
records = rotation_mgr.rotate_multiple_keys(
    rotations={
        "OPENAI_API_KEY": "sk-new-openai-key",
        "ANTHROPIC_API_KEY": "sk-ant-new-key"
    },
    validators={
        "OPENAI_API_KEY": validate_openai_key,
        "ANTHROPIC_API_KEY": validate_anthropic_key
    },
    atomic=True  # Rollback all if any fails
)

# Check results
for record in records:
    print(f"{record.secret_name}: {record.status}")
```

### Scheduled Rotation

```python
from pulsepilot.core.key_rotation import KeyRotationManager
from datetime import timedelta

rotation_mgr = KeyRotationManager()

# Schedule rotation every 90 days
schedule = rotation_mgr.schedule_rotation(
    secret_name="OPENAI_API_KEY",
    rotation_interval=timedelta(days=90)
)

print(f"Next rotation: {schedule['next_rotation']}")
```

### Custom Validators

Create custom validators for your API keys:

```python
def validate_custom_api_key(api_key: str) -> bool:
    """Validate custom API key."""
    try:
        # Make a test API call
        response = requests.get(
            "https://api.example.com/test",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Validation failed: {e}")
        return False

# Use validator in rotation
rotation_mgr.rotate_key(
    "CUSTOM_API_KEY",
    "new-key-value",
    validator=validate_custom_api_key
)
```

### Built-in Validators

Available validators:
- `validate_openai_key`: OpenAI API keys
- `validate_anthropic_key`: Anthropic API keys
- `validate_instagram_token`: Instagram access tokens
- `validate_google_token`: Google OAuth tokens
- `validate_telegram_token`: Telegram bot tokens

### Rotation History

```python
# Get rotation history
history = rotation_mgr.get_rotation_history(
    secret_name="OPENAI_API_KEY",
    limit=10
)

for record in history:
    print(f"{record['timestamp']}: {record['status']} - {record['secret_name']}")
```

## Security Best Practices

### 1. Use Cloud Secrets Managers in Production

Never use environment variables in production. Always use a cloud secrets manager:

```bash
# ❌ Don't do this in production
SECRETS_PROVIDER=env

# ✓ Do this instead
SECRETS_PROVIDER=aws  # or azure, gcp
```

### 2. Limit Secret Scope

Store only the secrets you need with minimal permissions:

```python
# ❌ Don't use admin/root credentials
INSTAGRAM_ACCESS_TOKEN=full_permissions_token

# ✓ Use limited scope tokens
INSTAGRAM_ACCESS_TOKEN=limited_scope_token  # Only post permissions
```

### 3. Rotate Keys Regularly

Set up a rotation schedule:

```python
# Rotate every 90 days
from datetime import timedelta

rotation_mgr.schedule_rotation(
    "OPENAI_API_KEY",
    rotation_interval=timedelta(days=90)
)
```

### 4. Use IAM Roles (Cloud Deployments)

Avoid storing cloud credentials:

```bash
# ❌ Don't do this
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# ✓ Use IAM roles instead
# EC2: Attach IAM role to instance
# ECS: Use task role
# Lambda: Use execution role
```

### 5. Enable Audit Logging

Track all secret access:

**AWS**: CloudTrail automatically logs Secrets Manager operations

**Azure**: Enable diagnostic logging:
```bash
az monitor diagnostic-settings create \
    --resource /subscriptions/{subscription-id}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vault} \
    --name audit-logs \
    --logs '[{"category": "AuditEvent", "enabled": true}]'
```

**GCP**: Audit logs are automatic in Cloud Audit Logs

### 6. Separate Secrets by Environment

Use different secrets for dev/staging/prod:

```
# Development
OPENAI_API_KEY_DEV=sk-dev-...

# Staging
OPENAI_API_KEY_STAGING=sk-staging-...

# Production
OPENAI_API_KEY_PROD=sk-prod-...
```

### 7. Monitor for Leaked Secrets

Use tools to scan for leaked secrets:
- **git-secrets**: Prevent committing secrets
- **TruffleHog**: Scan repos for secrets
- **GitHub Secret Scanning**: Automatic detection

### 8. Implement Secret Versioning

Keep previous versions for rollback:

```python
# AWS Secrets Manager keeps previous versions automatically
# Azure Key Vault keeps version history
# GCP Secret Manager supports versions natively
```

## Troubleshooting

### "No API key found" Error

**Problem**: Application can't find API keys

**Solution**:
1. Check `SECRETS_PROVIDER` is set correctly
2. Verify cloud provider credentials are configured
3. Ensure secrets exist in the secrets manager:

```python
from pulsepilot.core.secrets import get_secrets_manager

sm = get_secrets_manager()
value = sm.get_secret("OPENAI_API_KEY")
if not value:
    print("Secret not found!")
```

### OAuth Token Expired

**Problem**: OAuth token is expired and refresh fails

**Solution**:
1. Check OAuth credentials are stored correctly
2. Verify refresh token is valid
3. Re-authorize the application:

```python
from pulsepilot.core.oauth import InstagramOAuthManager

instagram = InstagramOAuthManager()
# Get new token from Facebook Developer Portal
new_token = OAuthToken(access_token="...", ...)
instagram.set_token(new_token)
```

### Secrets Manager Permission Denied

**Problem**: Can't access secrets in cloud provider

**Solution**:

**AWS**: Check IAM permissions
```bash
aws iam get-user
aws secretsmanager describe-secret --secret-id OPENAI_API_KEY
```

**Azure**: Check role assignments
```bash
az role assignment list --assignee $(az account show --query user.name -o tsv)
```

**GCP**: Check IAM permissions
```bash
gcloud projects get-iam-policy your-project-id
```

### Key Rotation Failed

**Problem**: Key rotation failed and won't rollback

**Solution**:
1. Check rotation history:
```python
history = rotation_mgr.get_rotation_history("OPENAI_API_KEY", limit=5)
```

2. Manually rollback:
```python
sm = get_secrets_manager()
sm.set_secret("OPENAI_API_KEY", "old-key-value")
```

3. Validate the key:
```python
from pulsepilot.core.key_rotation import validate_openai_key
is_valid = validate_openai_key("your-key")
```

## Additional Resources

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [Azure Key Vault Documentation](https://docs.microsoft.com/en-us/azure/key-vault/)
- [Google Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs with `LOG_LEVEL=DEBUG`
3. Open an issue on GitHub with:
   - Your secrets provider (aws/azure/gcp/env)
   - Error messages
   - Relevant logs (redact sensitive information!)
