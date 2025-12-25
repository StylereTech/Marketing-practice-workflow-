# Security Policy

## Overview

PulsePilot handles sensitive API keys and credentials for multiple external services. This document outlines security best practices and policies.

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please email [security contact] or open a private security advisory on GitHub. Do not create public issues for security vulnerabilities.

## API Key Management

### Supported API Keys

PulsePilot requires the following API keys depending on your configuration:

**LLM Providers:**
- `OPENAI_API_KEY` - OpenAI GPT models
- `ANTHROPIC_API_KEY` - Anthropic Claude models

**Deployment Channels:**
- `SMTP_USER` and `SMTP_PASS` - Email deployment
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` - Telegram notifications
- `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET` - Twitter/X posting
- `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_IG_USER_ID` - Instagram posting
- `FACEBOOK_PAGE_ACCESS_TOKEN` and `FACEBOOK_PAGE_ID` - Facebook posting
- `WORDPRESS_BASE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD` - WordPress publishing

### Best Practices

#### 1. Never Commit Secrets

**NEVER commit API keys or secrets to version control**

✅ **CORRECT:**
```bash
# Set environment variable
export OPENAI_API_KEY="sk-proj-..."

# Or use .env file (already in .gitignore)
echo "OPENAI_API_KEY=sk-proj-..." >> .env
```

❌ **INCORRECT:**
```python
# NEVER do this!
api_key = "sk-proj-abc123..."  # Hardcoded secret
```

#### 2. Use Environment Variables

All secrets should be stored in environment variables or `.env` files:

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual keys
nano .env

# NEVER commit .env to git (it's already in .gitignore)
```

#### 3. Rotate Compromised Keys Immediately

If you accidentally expose an API key:

1. **Revoke it immediately** in the provider's dashboard
2. **Generate a new key**
3. **Update your environment variables**
4. **Audit your git history** - if the key was committed, consider it permanently compromised
5. **Use tools like git-secrets** to prevent future commits

#### 4. Use Different Keys for Different Environments

```bash
# Development
OPENAI_API_KEY=sk-proj-dev-...

# Production
OPENAI_API_KEY=sk-proj-prod-...
```

#### 5. Implement Key Rotation

Regularly rotate API keys:
- **Critical services:** Every 30-90 days
- **Less critical:** Every 90-180 days
- **After team member departures:** Immediately

### Key Scoping and Permissions

When creating API keys:

1. **Use minimal permissions** - Only grant what's necessary
2. **Set usage limits** - Configure spending caps and rate limits
3. **Enable monitoring** - Set up alerts for unusual usage
4. **Use project-specific keys** - Don't share keys across projects

### Example .env Configuration

```bash
# LLM API Keys (use one or both)
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Model Configuration
ORCHESTRATOR_MODEL=gpt-4-turbo-preview
AGENT_MODEL=gpt-4-turbo-preview

# System Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
MAX_ITERATIONS=10
MEMORY_PERSISTENCE=true

# Deployment Configuration
DEPLOYMENT_ENABLED=true
DEPLOYMENT_DRY_RUN=true  # Set to false for real deployments
DEPLOYMENT_CHANNELS=email,telegram

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Social Media (optional - only if using deployment features)
X_API_KEY=your-x-api-key
X_API_SECRET=your-x-api-secret
X_ACCESS_TOKEN=your-x-access-token
X_ACCESS_SECRET=your-x-access-secret

INSTAGRAM_ACCESS_TOKEN=your-instagram-token
INSTAGRAM_IG_USER_ID=your-instagram-user-id

FACEBOOK_PAGE_ACCESS_TOKEN=your-facebook-token
FACEBOOK_PAGE_ID=your-facebook-page-id

# WordPress (optional)
WORDPRESS_BASE_URL=https://yourblog.com
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=your-app-password
BLOG_POST_STATUS=draft  # or 'publish'
```

## Security Features

### 1. .gitignore Protection

The following patterns are excluded from version control:

```gitignore
.env
.env.local
.env.*.local
*.key
*.pem
secrets/
credentials/
```

### 2. Dry Run Mode

Enable dry run to test deployments without actually publishing:

```bash
export DEPLOYMENT_DRY_RUN=true
```

This prevents accidental posts to social media or emails during testing.

### 3. Channel Controls

Selectively enable deployment channels:

```bash
# Only enable specific channels
export DEPLOYMENT_CHANNELS=email,telegram

# Disable all deployment
export DEPLOYMENT_ENABLED=false
```

## Production Security Checklist

Before deploying to production:

- [ ] All API keys are set as environment variables (not hardcoded)
- [ ] `.env` file is in `.gitignore` and never committed
- [ ] API keys have appropriate scopes and permissions
- [ ] Usage limits and spending caps are configured
- [ ] Monitoring and alerts are enabled for all API keys
- [ ] Dry run mode is disabled only after testing
- [ ] Different keys are used for dev/staging/production
- [ ] Team members have individual keys (not shared)
- [ ] Key rotation schedule is documented
- [ ] Incident response plan is in place

## Automated Security Tools

### Pre-commit Hooks

Install git-secrets to prevent committing credentials:

```bash
# Install git-secrets
brew install git-secrets  # macOS
# or
apt-get install git-secrets  # Linux

# Set up hooks
git secrets --install
git secrets --register-aws
git secrets --add 'sk-[a-zA-Z0-9]{48}'
git secrets --add 'sk-proj-[a-zA-Z0-9_-]+'
git secrets --add 'sk-ant-[a-zA-Z0-9_-]+'
```

### Environment Validation

Before running campaigns, validate your environment:

```python
from pulsepilot.core.llm import LLMInterface

try:
    llm = LLMInterface()
    print("✅ API keys configured correctly")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
```

## Incident Response

If you discover a security incident:

1. **Immediately revoke compromised credentials**
2. **Assess the scope of exposure**
3. **Generate new credentials**
4. **Review audit logs** for unauthorized access
5. **Update all affected systems**
6. **Document the incident**
7. **Review and improve security processes**

## Security Updates

This project uses the following security practices:

- **Dependency scanning:** Regular updates to patch vulnerabilities
- **Code review:** All changes reviewed before merging
- **Principle of least privilege:** Minimal permissions by default
- **Defense in depth:** Multiple layers of security controls

## Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [OpenAI API Best Practices](https://platform.openai.com/docs/guides/production-best-practices)
- [Anthropic Security Guidelines](https://docs.anthropic.com/claude/docs/security)
- [12 Factor App - Config](https://12factor.net/config)

## Questions?

For security-related questions or concerns, please reach out through the appropriate channels. Never share sensitive information in public forums or issues.

---

**Last Updated:** 2025-12-25
