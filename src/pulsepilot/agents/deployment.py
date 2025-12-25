"""Agent 5: Deployment - Publishing to External Platforms."""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Optional, Dict, List
import requests
from requests_oauthlib import OAuth1
from pulsepilot.agents.base import BaseAgent
from pulsepilot.core.models import (
    AgentRole,
    AgentTask,
    AgentOutput,
    TaskStatus,
)
from pulsepilot.core.secrets import get_secrets_manager, SecretsManagerInterface
from pulsepilot.core.oauth import (
    InstagramOAuthManager,
    FacebookOAuthManager,
    OAuthTokenManager
)


class DeploymentAgent(BaseAgent):
    """
    Agent 5: Deployment
    
    Responsibilities:
    - Publish content to social media (X, Instagram, Facebook)
    - Send email notifications/campaigns
    - Send alerts to Telegram
    - Publish to blogs (WordPress)
    - Manage external platform API integrations
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(AgentRole.ORCHESTRATOR, *args, **kwargs)
        self.role_name = "deployment"
        self.secrets_manager = get_secrets_manager()
        self.instagram_oauth = InstagramOAuthManager(self.secrets_manager)
        self.facebook_oauth = FacebookOAuthManager(self.secrets_manager)
        self._load_config()

    def _load_config(self):
        """Load deployment configuration from environment."""
        self.enabled = os.getenv("DEPLOYMENT_ENABLED", "true").lower() == "true"
        self.dry_run = os.getenv("DEPLOYMENT_DRY_RUN", "false").lower() == "true"
        
        channels_raw = os.getenv("DEPLOYMENT_CHANNELS", "email,telegram")
        if channels_raw:
            self.active_channels = [c.strip().lower() for c in channels_raw.split(",")]
        else:
            self.active_channels = []

    def get_system_prompt(self) -> str:
        return """You are the Deployment Agent, responsible for the final execution and distribution of campaign assets to external platforms.
"""

    def is_channel_enabled(self, channel: str) -> bool:
        """Check if a channel is enabled in config."""
        return channel.lower() in self.active_channels

    def execute_task(self, task: AgentTask) -> AgentOutput:
        """Execute deployment task."""
        if not self.enabled:
            self.log("Deployment globally disabled via DEPLOYMENT_ENABLED=false")
            return AgentOutput(
                task_id=task.task_id,
                agent_role=self.role,
                outputs={"status": "skipped", "reason": "deployment_disabled"},
                status=TaskStatus.COMPLETED,
            )
        return self._generic_execution(task)

    def push_to_email(self, subject: str, body: str, recipient: str) -> Dict[str, Any]:
        """Push content via email (SMTP)."""
        if not self.is_channel_enabled("email"):
            return {"status": "skipped", "reason": "channel_not_in_list"}

        self.log(f"Sending email to {recipient}...")

        # Get credentials from secrets manager
        smtp_user = self.secrets_manager.get_secret("SMTP_USER")
        smtp_pass = self.secrets_manager.get_secret("SMTP_PASS")

        if self.dry_run or not all([smtp_user, smtp_pass]):
            reason = "dry_run" if self.dry_run else "missing_credentials"
            self.log(f"Simulating email send ({reason}).", "WARNING")
            return {"status": "simulated", "reason": reason}

        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            smtp_server = self.secrets_manager.get_secret("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(self.secrets_manager.get_secret("SMTP_PORT", "587"))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            return {"status": "sent"}
        except Exception as e:
            self.log(f"Failed to send email: {e}", "ERROR")
            return {"status": "failed", "error": str(e)}

    def push_to_instagram(self, caption: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """Push content to Instagram Business via Graph API with OAuth."""
        if not self.is_channel_enabled("instagram"):
            return {"status": "skipped", "reason": "channel_not_in_list"}

        self.log("Pushing to Instagram...")

        # Get OAuth token with automatic refresh
        token = self.instagram_oauth.get_token()
        ig_user_id = self.instagram_oauth.get_user_id()

        # Use provided image_url or get from secrets
        image_url = image_url or self.secrets_manager.get_secret("INSTAGRAM_IMAGE_URL")

        if self.dry_run or not all([token, ig_user_id, image_url]):
            reason = "dry_run" if self.dry_run else "missing_credentials"
            self.log(f"Simulating Instagram push ({reason}).", "WARNING")
            return {"status": "simulated", "reason": reason}

        try:
            access_token = token.access_token

            # Step 1: Create media container
            container_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
            payload = {
                "image_url": image_url,
                "caption": caption,
                "access_token": access_token
            }
            res = requests.post(container_url, data=payload, timeout=15)
            res_data = res.json()

            if "id" not in res_data:
                return {"status": "failed", "error": f"Container creation failed: {res_data.get('error', {}).get('message', 'Unknown error')}"}

            creation_id = res_data["id"]

            # Step 2: Publish container
            publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": access_token
            }
            pub_res = requests.post(publish_url, data=publish_payload, timeout=15)
            pub_data = pub_res.json()

            if "id" in pub_data:
                return {"status": "sent", "id": pub_data["id"]}
            else:
                return {"status": "failed", "error": f"Publish failed: {pub_data.get('error', {}).get('message', 'Unknown error')}"}

        except Exception as e:
            self.log(f"Failed to push to Instagram: {e}", "ERROR")
            return {"status": "failed", "error": str(e)}

    def push_to_facebook(self, message: str) -> Dict[str, Any]:
        """Push content to Facebook Page feed via Graph API with OAuth."""
        if not self.is_channel_enabled("facebook"):
            return {"status": "skipped", "reason": "channel_not_in_list"}

        self.log("Pushing to Facebook Page...")

        # Get OAuth token with automatic refresh
        token = self.facebook_oauth.get_token()
        page_id = self.facebook_oauth.get_page_id()

        if self.dry_run or not all([token, page_id]):
            reason = "dry_run" if self.dry_run else "missing_credentials"
            self.log(f"Simulating Facebook push ({reason}).", "WARNING")
            return {"status": "simulated", "reason": reason}

        try:
            url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
            payload = {
                "message": message,
                "access_token": token.access_token
            }
            res = requests.post(url, data=payload, timeout=15)
            data = res.json()

            if "id" in data:
                return {"status": "sent", "id": data["id"]}
            else:
                return {"status": "failed", "error": data.get("error", {}).get("message", "Unknown error")}
        except Exception as e:
            self.log(f"Failed to push to Facebook: {e}", "ERROR")
            return {"status": "failed", "error": str(e)}

    def push_to_x(self, text: str) -> Dict[str, Any]:
        """Push content to X/Twitter via API v2 (OAuth 1.0a)."""
        if not self.is_channel_enabled("x"):
            return {"status": "skipped", "reason": "channel_not_in_list"}

        self.log("Pushing to X...")

        # Get credentials from secrets manager
        api_key = self.secrets_manager.get_secret("X_API_KEY")
        api_secret = self.secrets_manager.get_secret("X_API_SECRET")
        access_token = self.secrets_manager.get_secret("X_ACCESS_TOKEN")
        access_secret = self.secrets_manager.get_secret("X_ACCESS_SECRET")

        if self.dry_run or not all([api_key, api_secret, access_token, access_secret]):
            reason = "dry_run" if self.dry_run else "missing_credentials"
            self.log(f"Simulating X push ({reason}).", "WARNING")
            return {"status": "simulated", "reason": reason}

        try:
            auth = OAuth1(api_key, api_secret, access_token, access_secret)
            url = "https://api.twitter.com/2/tweets"
            payload = {"text": text[:280]}  # Hard truncate for safety

            res = requests.post(url, auth=auth, json=payload, timeout=15)
            data = res.json()

            if res.status_code == 201 and "data" in data:
                return {"status": "sent", "id": data["data"]["id"]}
            else:
                error_msg = data.get("detail") or data.get("errors", [{}])[0].get("message", "Unknown error")
                return {"status": "failed", "error": error_msg}
        except Exception as e:
            self.log(f"Failed to push to X: {e}", "ERROR")
            return {"status": "failed", "error": str(e)}

    def push_to_telegram(self, message: str) -> Dict[str, Any]:
        """Push content to Telegram Bot API."""
        if not self.is_channel_enabled("telegram"):
            return {"status": "skipped", "reason": "channel_not_in_list"}

        self.log("Pushing to Telegram...")

        # Get credentials from secrets manager
        bot_token = self.secrets_manager.get_secret("TELEGRAM_BOT_TOKEN")
        chat_id = self.secrets_manager.get_secret("TELEGRAM_CHAT_ID")

        if self.dry_run or not bot_token or not chat_id:
            reason = "dry_run" if self.dry_run else "missing_credentials"
            self.log(f"Simulating Telegram push ({reason}).", "WARNING")
            return {"status": "simulated", "reason": reason}

        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload, timeout=10)
            res_data = response.json()

            if res_data.get("ok"):
                return {"status": "sent", "id": res_data["result"]["message_id"]}
            else:
                return {"status": "failed", "error": res_data.get("description")}
        except Exception as e:
            self.log(f"Failed to push to Telegram: {e}", "ERROR")
            return {"status": "failed", "error": str(e)}

    def push_to_blog(self, title: str, content: str) -> Dict[str, Any]:
        """Push content to blog (WordPress REST API)."""
        if not self.is_channel_enabled("blog"):
            return {"status": "skipped", "reason": "channel_not_in_list"}

        self.log("Pushing to WordPress blog...")

        # Get credentials from secrets manager
        base_url = self.secrets_manager.get_secret("WORDPRESS_BASE_URL")
        username = self.secrets_manager.get_secret("WORDPRESS_USERNAME")
        app_password = self.secrets_manager.get_secret("WORDPRESS_APP_PASSWORD")
        status = self.secrets_manager.get_secret("BLOG_POST_STATUS", "draft").lower()

        if self.dry_run or not all([base_url, username, app_password]):
            reason = "dry_run" if self.dry_run else "missing_credentials"
            self.log(f"Simulating WordPress push ({reason}).", "WARNING")
            return {"status": "simulated", "reason": reason}

        try:
            from requests.auth import HTTPBasicAuth
            url = f"{base_url.rstrip('/')}/wp-json/wp/v2/posts"
            payload = {
                "title": title,
                "content": content,
                "status": status
            }
            res = requests.post(
                url,
                auth=HTTPBasicAuth(username, app_password),
                json=payload,
                timeout=15
            )
            data = res.json()

            if res.status_code in [201, 200] and "id" in data:
                return {"status": "sent", "id": data["id"], "url": data.get("link")}
            else:
                error_msg = data.get("message", "Unknown error")
                return {"status": "failed", "error": error_msg}
        except Exception as e:
            self.log(f"Failed to push to WordPress: {e}", "ERROR")
            return {"status": "failed", "error": str(e)}

    def _generic_execution(self, task: AgentTask) -> AgentOutput:
        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"result": "Generic execution not implemented"},
            status=TaskStatus.COMPLETED,
        )
