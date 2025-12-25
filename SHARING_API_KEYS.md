# How to Share API Keys Securely

This guide explains how to configure and share API keys for your PulsePilot agent.

## 🚀 Quick Setup (Interactive)

The easiest way to set up your API keys:

```bash
python scripts/setup_secrets.py
```

This interactive script will:
1. Ask which provider you want to use (env, AWS, Azure, or GCP)
2. Prompt for your API keys securely (no echo)
3. Store them in your chosen provider
4. Generate the configuration file
5. Show team setup instructions

## 📋 Sharing Options

### Option 1: Local Development (Environment Variables)

**Best for**: Individual developers, testing

**Setup:**

```bash
# Run the setup script
python scripts/setup_secrets.py
# Choose "Environment Variables"
# Enter your API keys when prompted

# Or manually create .env:
cat > .env << EOF
SECRETS_PROVIDER=env
OPENAI_API_KEY=sk-your-key-here
TELEGRAM_BOT_TOKEN=your-token-here
TELEGRAM_CHAT_ID=your-chat-id
EOF
```

**Sharing with team:**
- Share `.env` file via **1Password** / **LastPass** / **Bitwarden**
- Or send via **encrypted email** (GPG/PGP)
- **NEVER commit .env to Git!** (already in `.gitignore`)

**Team member setup:**
```bash
# 1. Receive .env file securely
# 2. Place in project root
# 3. Install dependencies
poetry install
# 4. Test
python examples/secure_secrets_example.py
```

---

### Option 2: AWS Secrets Manager (Recommended for Production)

**Best for**: AWS-based deployments, teams, production

**Your Setup:**

```bash
# Option A: Use the interactive script
python scripts/setup_secrets.py
# Choose "AWS Secrets Manager"

# Option B: Use the bash script
./scripts/setup_aws_secrets.sh

# Option C: Manual setup
aws configure  # Configure AWS credentials
poetry install -E aws  # Install AWS support

# Store secrets
aws secretsmanager create-secret --name OPENAI_API_KEY --secret-string "sk-..."
aws secretsmanager create-secret --name TELEGRAM_BOT_TOKEN --secret-string "..."

# Create .env
echo "SECRETS_PROVIDER=aws" > .env
echo "AWS_DEFAULT_REGION=us-east-1" >> .env
```

**Team Member Setup:**

```bash
# 1. Configure AWS credentials (they need IAM access)
aws configure
# OR use IAM roles (EC2, ECS, Lambda)

# 2. Install AWS support
poetry install -E aws

# 3. Copy .env file (only contains SECRETS_PROVIDER=aws)
echo "SECRETS_PROVIDER=aws" > .env
echo "AWS_DEFAULT_REGION=us-east-1" >> .env

# 4. Test
python examples/secure_secrets_example.py
```

**IAM Policy for Team (attach to users/roles):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:*"
    }
  ]
}
```

**Sharing:**
1. ✅ Store secrets in AWS Secrets Manager (done once by you)
2. ✅ Share AWS account access (IAM users or roles)
3. ✅ Team members configure `aws configure` with their credentials
4. ✅ They automatically get access to secrets!

---

### Option 3: Azure Key Vault

**Best for**: Azure-based deployments, Microsoft ecosystem

**Your Setup:**

```bash
# Interactive setup
python scripts/setup_secrets.py
# Choose "Azure Key Vault"

# Or manual:
az login
poetry install -E azure

# Create Key Vault (if needed)
az keyvault create \
    --name your-pulsepilot-vault \
    --resource-group your-rg \
    --location eastus

# Store secrets (use hyphens, not underscores!)
az keyvault secret set --vault-name your-pulsepilot-vault \
    --name OPENAI-API-KEY --value "sk-..."

# Create .env
cat > .env << EOF
SECRETS_PROVIDER=azure
AZURE_KEY_VAULT_URL=https://your-pulsepilot-vault.vault.azure.net/
EOF
```

**Team Member Setup:**

```bash
# 1. Authenticate with Azure
az login

# 2. Install Azure support
poetry install -E azure

# 3. Copy .env file
cat > .env << EOF
SECRETS_PROVIDER=azure
AZURE_KEY_VAULT_URL=https://your-pulsepilot-vault.vault.azure.net/
EOF

# 4. Test
python examples/secure_secrets_example.py
```

**Grant Access:**

```bash
# Give team member access to Key Vault
az role assignment create \
    --assignee user@example.com \
    --role "Key Vault Secrets User" \
    --scope /subscriptions/YOUR_SUBSCRIPTION/resourceGroups/YOUR_RG/providers/Microsoft.KeyVault/vaults/your-pulsepilot-vault
```

---

### Option 4: Google Cloud Secret Manager

**Best for**: GCP-based deployments

**Your Setup:**

```bash
# Interactive setup
python scripts/setup_secrets.py
# Choose "Google Cloud Secret Manager"

# Or manual:
gcloud auth application-default login
poetry install -E gcp

# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Store secrets
echo -n "sk-..." | gcloud secrets create OPENAI_API_KEY \
    --data-file=- \
    --replication-policy="automatic"

# Create .env
cat > .env << EOF
SECRETS_PROVIDER=gcp
GCP_PROJECT_ID=your-project-id
EOF
```

**Team Member Setup:**

```bash
# 1. Authenticate with GCP
gcloud auth application-default login

# 2. Install GCP support
poetry install -E gcp

# 3. Copy .env file
cat > .env << EOF
SECRETS_PROVIDER=gcp
GCP_PROJECT_ID=your-project-id
EOF

# 4. Test
python examples/secure_secrets_example.py
```

**Grant Access:**

```bash
# Give team member access to secrets
gcloud projects add-iam-policy-binding your-project-id \
    --member="user:teammate@example.com" \
    --role="roles/secretmanager.secretAccessor"
```

---

## 🔑 OAuth Setup (Instagram, Facebook, Google)

After setting up your secrets manager, configure OAuth:

### Instagram

```python
from pulsepilot.core.oauth import InstagramOAuthManager, OAuthToken

instagram = InstagramOAuthManager()

# Get token from Facebook Developer Portal
token = OAuthToken(
    access_token="YOUR_INSTAGRAM_TOKEN",
    refresh_token="YOUR_INSTAGRAM_TOKEN",  # Same for Instagram
    expires_in=5184000,  # 60 days
)

instagram.set_token(token)
instagram.secrets_manager.set_secret("INSTAGRAM_IG_USER_ID", "your_ig_user_id")

print("✓ Instagram OAuth configured")
```

Or use CLI:

```bash
python -m pulsepilot.cli_secrets oauth-set instagram \
    --access-token="YOUR_TOKEN" \
    --expires-in=5184000
```

### Facebook

```bash
python -m pulsepilot.cli_secrets oauth-set facebook \
    --access-token="YOUR_PAGE_TOKEN" \
    --expires-in=5184000

python -m pulsepilot.cli_secrets set FACEBOOK_PAGE_ID --value="your_page_id"
```

### Google

```bash
python -m pulsepilot.cli_secrets oauth-set google \
    --access-token="YOUR_ACCESS_TOKEN" \
    --refresh-token="YOUR_REFRESH_TOKEN" \
    --expires-in=3600
```

---

## 🔄 Managing Secrets with CLI

After setup, use the CLI to manage secrets:

```bash
# View a secret (masked)
python -m pulsepilot.cli_secrets get OPENAI_API_KEY

# View full value
python -m pulsepilot.cli_secrets get OPENAI_API_KEY --show

# Set a new secret
python -m pulsepilot.cli_secrets set NEW_API_KEY --value="sk-..."

# Rotate a key (with validation)
python -m pulsepilot.cli_secrets rotate OPENAI_API_KEY --validate

# Delete a secret
python -m pulsepilot.cli_secrets delete OLD_KEY --force

# Check OAuth token status
python -m pulsepilot.cli_secrets oauth-get instagram

# Manually refresh OAuth token
python -m pulsepilot.cli_secrets oauth-refresh instagram

# Migrate from env to AWS
python -m pulsepilot.cli_secrets migrate \
    --from=env \
    --to=aws \
    --secrets=OPENAI_API_KEY,TELEGRAM_BOT_TOKEN
```

---

## ✅ Verification

Test that everything works:

```python
from pulsepilot.core.secrets import get_secret
from pulsepilot.core.llm import LLMInterface

# Test 1: Check secrets are accessible
openai_key = get_secret("OPENAI_API_KEY")
print(f"✓ OpenAI key: {openai_key[:10]}...")

# Test 2: Test LLM
llm = LLMInterface()
response = llm.generate(
    system_prompt="You are helpful.",
    user_prompt="Say hello!",
)
print(f"✓ LLM works: {response}")

# Test 3: Test deployment agent
from pulsepilot.agents.deployment import DeploymentAgent
from pulsepilot.core.memory import SharedMemory

memory = SharedMemory()
agent = DeploymentAgent(memory=memory)
result = agent.push_to_telegram("Test message")
print(f"✓ Agent works: {result['status']}")
```

---

## 🔒 Security Best Practices

### ✅ DO:
- ✅ Use cloud secrets manager for production (AWS/Azure/GCP)
- ✅ Use environment variables only for local development
- ✅ Share .env via secure channels (1Password, encrypted email)
- ✅ Use IAM roles instead of access keys when possible
- ✅ Rotate keys regularly (every 90 days)
- ✅ Use minimal permissions (read-only for most team members)

### ❌ DON'T:
- ❌ Never commit .env to Git
- ❌ Never share API keys in Slack/email/chat
- ❌ Never use production keys for development
- ❌ Never give admin permissions unless needed
- ❌ Never hard-code API keys in your code

---

## 🚨 If Keys Are Compromised

If API keys are leaked:

1. **Immediately rotate** the compromised keys:
   ```bash
   python -m pulsepilot.cli_secrets rotate COMPROMISED_KEY --validate
   ```

2. **Revoke** the old keys in the platform:
   - OpenAI: https://platform.openai.com/api-keys
   - Telegram: Contact @BotFather
   - Instagram/Facebook: Facebook Developer Portal

3. **Check usage** for unauthorized activity

4. **Update team** to use new keys

---

## 📚 Additional Resources

- **Full Documentation**: `docs/SECURITY.md`
- **Quick Start Guide**: `docs/QUICKSTART_SECURITY.md`
- **Code Examples**: `examples/secure_secrets_example.py`
- **CLI Reference**: `python -m pulsepilot.cli_secrets --help`

---

## ❓ Need Help?

Common issues:

**"No API key found"**
```bash
# Check provider is set
cat .env

# Verify secret exists
python -m pulsepilot.cli_secrets get OPENAI_API_KEY
```

**"Permission denied" (AWS)**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check secret permissions
aws secretsmanager describe-secret --secret-id OPENAI_API_KEY
```

**OAuth token expired**
```bash
# Force refresh
python -m pulsepilot.cli_secrets oauth-refresh instagram
```

For more help, see `docs/SECURITY.md` troubleshooting section.
