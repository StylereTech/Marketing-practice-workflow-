# Quick Start: Secure API Key Management

Get started with secure API key management in 5 minutes.

## Option 1: Local Development (Environment Variables)

**Perfect for**: Getting started, local testing

### Steps

1. **Create `.env` file**:
```bash
cp .env.example .env
```

2. **Add your API keys**:
```bash
# Edit .env
SECRETS_PROVIDER=env
OPENAI_API_KEY=sk-your-key-here
TELEGRAM_BOT_TOKEN=your-token-here
```

3. **Install dependencies**:
```bash
poetry install
```

4. **You're done!** The application will automatically use your environment variables.

```python
from pulsepilot.agents.deployment import DeploymentAgent

# Keys are automatically loaded from .env
agent = DeploymentAgent(...)
```

## Option 2: AWS Secrets Manager (Production)

**Perfect for**: AWS deployments, production environments

### Steps

1. **Install AWS dependencies**:
```bash
poetry install -E aws
```

2. **Configure AWS credentials**:
```bash
aws configure
# Enter your AWS Access Key ID and Secret Access Key
```

3. **Store your secrets**:
```bash
aws secretsmanager create-secret \
    --name OPENAI_API_KEY \
    --secret-string "sk-your-key-here"

aws secretsmanager create-secret \
    --name TELEGRAM_BOT_TOKEN \
    --secret-string "your-token-here"
```

4. **Update your `.env`**:
```bash
SECRETS_PROVIDER=aws
AWS_DEFAULT_REGION=us-east-1
```

5. **Done!** Your application now uses AWS Secrets Manager.

### Quick Migration Script

Migrate from `.env` to AWS Secrets Manager:

```python
#!/usr/bin/env python3
"""Migrate secrets from .env to AWS Secrets Manager."""

from dotenv import load_dotenv
from pulsepilot.core.secrets import SecretsManagerFactory, SecretProvider
import os

# Load from .env
load_dotenv()

# Create AWS secrets manager
aws_sm = SecretsManagerFactory.create(SecretProvider.AWS)

# Secrets to migrate
secrets = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "SMTP_USER",
    "SMTP_PASS",
]

# Migrate each secret
for secret_name in secrets:
    value = os.getenv(secret_name)
    if value:
        print(f"Migrating {secret_name}...")
        aws_sm.set_secret(secret_name, value)
        print(f"✓ {secret_name} migrated")
    else:
        print(f"⊘ {secret_name} not found in .env")

print("\n✓ Migration complete!")
print("Update your .env: SECRETS_PROVIDER=aws")
```

Save as `migrate_to_aws.py` and run:
```bash
python migrate_to_aws.py
```

## Option 3: Azure Key Vault (Production)

**Perfect for**: Azure deployments, Microsoft ecosystem

### Steps

1. **Install Azure dependencies**:
```bash
poetry install -E azure
```

2. **Configure Azure authentication**:
```bash
az login
```

3. **Create Key Vault** (if you don't have one):
```bash
az keyvault create \
    --name your-vault-name \
    --resource-group your-resource-group \
    --location eastus
```

4. **Store your secrets**:
```bash
az keyvault secret set \
    --vault-name your-vault-name \
    --name OPENAI-API-KEY \
    --value "sk-your-key-here"

az keyvault secret set \
    --vault-name your-vault-name \
    --name TELEGRAM-BOT-TOKEN \
    --value "your-token-here"
```

Note: Azure Key Vault requires hyphens instead of underscores in secret names.

5. **Update your `.env`**:
```bash
SECRETS_PROVIDER=azure
AZURE_KEY_VAULT_URL=https://your-vault-name.vault.azure.net/
```

6. **Done!** Your application now uses Azure Key Vault.

## Option 4: Google Cloud Secret Manager (Production)

**Perfect for**: GCP deployments, Google Cloud ecosystem

### Steps

1. **Install GCP dependencies**:
```bash
poetry install -E gcp
```

2. **Configure GCP authentication**:
```bash
gcloud auth application-default login
```

3. **Enable Secret Manager API**:
```bash
gcloud services enable secretmanager.googleapis.com
```

4. **Store your secrets**:
```bash
echo -n "sk-your-key-here" | gcloud secrets create OPENAI_API_KEY \
    --data-file=- \
    --replication-policy="automatic"

echo -n "your-token-here" | gcloud secrets create TELEGRAM_BOT_TOKEN \
    --data-file=- \
    --replication-policy="automatic"
```

5. **Update your `.env`**:
```bash
SECRETS_PROVIDER=gcp
GCP_PROJECT_ID=your-project-id
```

6. **Done!** Your application now uses Google Secret Manager.

## Setting Up OAuth for Social Media

### Instagram Quick Setup

1. **Get Instagram access token** from [Facebook Developer Portal](https://developers.facebook.com/)

2. **Store the token**:

```python
from pulsepilot.core.oauth import InstagramOAuthManager, OAuthToken

# Create manager
instagram = InstagramOAuthManager()

# Create token (Instagram tokens last 60 days)
token = OAuthToken(
    access_token="YOUR_INSTAGRAM_TOKEN",
    refresh_token="YOUR_INSTAGRAM_TOKEN",  # Same as access token
    expires_in=5184000,  # 60 days
)

# Store token
instagram.set_token(token)

# Store Instagram user ID
instagram.secrets_manager.set_secret(
    "INSTAGRAM_IG_USER_ID",
    "your_instagram_business_account_id"
)
```

3. **Enable automatic refresh**:

The token will automatically refresh 5 minutes before expiration!

### Facebook Quick Setup

1. **Get Page Access Token** from [Facebook Developer Portal](https://developers.facebook.com/)

2. **Store the token**:

```python
from pulsepilot.core.oauth import FacebookOAuthManager, OAuthToken

facebook = FacebookOAuthManager()

token = OAuthToken(
    access_token="YOUR_PAGE_TOKEN",
    expires_in=5184000,  # 60 days
)

facebook.set_token(token)
facebook.secrets_manager.set_secret("FACEBOOK_PAGE_ID", "your_page_id")

# For automatic token refresh, store app credentials
facebook.secrets_manager.set_secret(
    "FACEBOOK_OAUTH_CREDENTIALS",
    '{"app_id": "your_app_id", "app_secret": "your_app_secret"}'
)
```

### Google Quick Setup

1. **Create OAuth credentials** in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

2. **Get authorization code**:
   - Use OAuth 2.0 Playground or implement authorization flow
   - Exchange code for tokens

3. **Store the token**:

```python
from pulsepilot.core.oauth import GoogleOAuthManager, OAuthToken

google = GoogleOAuthManager()

token = OAuthToken(
    access_token="YOUR_ACCESS_TOKEN",
    refresh_token="YOUR_REFRESH_TOKEN",
    expires_in=3600,  # 1 hour
    scope="https://www.googleapis.com/auth/youtube"
)

google.set_token(token)

# Store client credentials for automatic refresh
google.secrets_manager.set_secret(
    "GOOGLE_OAUTH_CREDENTIALS",
    '{"client_id": "your_client_id", "client_secret": "your_client_secret"}'
)
```

## Key Rotation Quick Start

Rotate API keys safely:

```python
from pulsepilot.core.key_rotation import KeyRotationManager, validate_openai_key

# Create manager
rotation = KeyRotationManager()

# Rotate with automatic validation and rollback
result = rotation.rotate_key(
    secret_name="OPENAI_API_KEY",
    new_value="sk-new-key-here",
    validator=validate_openai_key,
    auto_rollback=True
)

if result.status == "completed":
    print("✓ Key rotated successfully!")
else:
    print(f"✗ Rotation failed: {result.error_message}")
    print("Old key is still active (automatic rollback)")
```

## Testing Your Setup

Verify everything works:

```python
from pulsepilot.core.secrets import get_secret
from pulsepilot.core.llm import LLMInterface
from pulsepilot.agents.deployment import DeploymentAgent

# Test 1: Check secrets are accessible
openai_key = get_secret("OPENAI_API_KEY")
print(f"OpenAI key found: {openai_key[:10]}...")

# Test 2: Test LLM connection
llm = LLMInterface()
response = llm.generate(
    system_prompt="You are a helpful assistant.",
    user_prompt="Say 'Hello!'",
    temperature=0.7
)
print(f"LLM response: {response}")

# Test 3: Test deployment agent
agent = DeploymentAgent(...)
# Try a dry-run push
result = agent.push_to_telegram("Test message")
print(f"Deployment test: {result['status']}")
```

## Next Steps

1. **Read the full documentation**: `docs/SECURITY.md`
2. **Set up key rotation schedules**: Rotate keys every 90 days
3. **Enable audit logging**: Track all secret access
4. **Configure OAuth for all platforms**: Instagram, Facebook, Google
5. **Implement monitoring**: Alert on failed rotations or expired tokens

## Common Issues

### "No API key found"

**Solution**: Check your `SECRETS_PROVIDER` is set correctly and secrets exist:

```python
from pulsepilot.core.secrets import get_secrets_manager

sm = get_secrets_manager()
print(f"Provider: {type(sm).__name__}")
value = sm.get_secret("OPENAI_API_KEY")
print(f"Key exists: {value is not None}")
```

### "Permission denied" (Cloud Providers)

**AWS**: Check IAM permissions include `secretsmanager:GetSecretValue`

**Azure**: Check you have "Key Vault Secrets User" role

**GCP**: Check IAM includes `roles/secretmanager.secretAccessor`

### OAuth token expired

**Solution**: Tokens automatically refresh, but if refresh fails:

```python
from pulsepilot.core.oauth import InstagramOAuthManager

instagram = InstagramOAuthManager()
# Force refresh
token = instagram.get_token(force_refresh=True)
```

## Getting Help

- **Documentation**: `docs/SECURITY.md`
- **Examples**: `examples/` directory
- **Issues**: Open on GitHub

---

**You're all set!** Your API keys are now securely managed. 🔐
