#!/bin/bash
# setup_aws_secrets.sh
# Script to set up all secrets in AWS Secrets Manager

set -e

echo "🔐 Setting up secrets in AWS Secrets Manager"
echo ""

# Check AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Run: aws configure"
    exit 1
fi

# Prompt for secrets
echo "Enter your API keys (they will be stored securely in AWS):"
echo ""

read -sp "OpenAI API Key: " OPENAI_KEY
echo ""
read -sp "Anthropic API Key (optional): " ANTHROPIC_KEY
echo ""
read -sp "Telegram Bot Token (optional): " TELEGRAM_TOKEN
echo ""
read -p "Telegram Chat ID (optional): " TELEGRAM_CHAT
echo ""

# Create secrets in AWS
echo ""
echo "📤 Uploading secrets to AWS Secrets Manager..."

if [ ! -z "$OPENAI_KEY" ]; then
    aws secretsmanager create-secret \
        --name OPENAI_API_KEY \
        --secret-string "$OPENAI_KEY" \
        --description "OpenAI API key for PulsePilot" 2>/dev/null \
    || aws secretsmanager update-secret \
        --secret-id OPENAI_API_KEY \
        --secret-string "$OPENAI_KEY"
    echo "✓ OPENAI_API_KEY"
fi

if [ ! -z "$ANTHROPIC_KEY" ]; then
    aws secretsmanager create-secret \
        --name ANTHROPIC_API_KEY \
        --secret-string "$ANTHROPIC_KEY" \
        --description "Anthropic API key for PulsePilot" 2>/dev/null \
    || aws secretsmanager update-secret \
        --secret-id ANTHROPIC_API_KEY \
        --secret-string "$ANTHROPIC_KEY"
    echo "✓ ANTHROPIC_API_KEY"
fi

if [ ! -z "$TELEGRAM_TOKEN" ]; then
    aws secretsmanager create-secret \
        --name TELEGRAM_BOT_TOKEN \
        --secret-string "$TELEGRAM_TOKEN" \
        --description "Telegram bot token for PulsePilot" 2>/dev/null \
    || aws secretsmanager update-secret \
        --secret-id TELEGRAM_BOT_TOKEN \
        --secret-string "$TELEGRAM_TOKEN"
    echo "✓ TELEGRAM_BOT_TOKEN"
fi

if [ ! -z "$TELEGRAM_CHAT" ]; then
    aws secretsmanager create-secret \
        --name TELEGRAM_CHAT_ID \
        --secret-string "$TELEGRAM_CHAT" \
        --description "Telegram chat ID for PulsePilot" 2>/dev/null \
    || aws secretsmanager update-secret \
        --secret-id TELEGRAM_CHAT_ID \
        --secret-string "$TELEGRAM_CHAT"
    echo "✓ TELEGRAM_CHAT_ID"
fi

echo ""
echo "✅ All secrets uploaded successfully!"
echo ""
echo "Next steps for team members:"
echo "1. Configure AWS credentials: aws configure"
echo "2. Update .env: SECRETS_PROVIDER=aws"
echo "3. Run: poetry install -E aws"
echo "4. Test: python examples/secure_secrets_example.py"
echo ""
echo "IAM Policy needed (attach to users/roles):"
cat << 'POLICY'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:*"
    }
  ]
}
POLICY
