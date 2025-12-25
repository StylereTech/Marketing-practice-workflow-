"""Agent 5: Deployment - Publishing to External Platforms."""

import os
import json
import smtplib
from datetime import datetime
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
        
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")

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

            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            return {"status": "sent"}
        except Exception as e:
            self.log(f"Failed to send email: {e}", "ERROR")
            return {"status": "failed", "error": str(e)}

    def push_to_instagram(self, caption: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """Push content to Instagram Business via Graph API."""
        if not self.is_channel_enabled("instagram"):
            return {"status": "skipped", "reason": "channel_not_in_list"}

        self.log("Pushing to Instagram...")
        access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        ig_user_id = os.getenv("INSTAGRAM_IG_USER_ID")
        # Use provided image_url or a placeholder if missing
        image_url = image_url or os.getenv("INSTAGRAM_IMAGE_URL")

        if self.dry_run or not all([access_token, ig_user_id, image_url]):
            reason = "dry_run" if self.dry_run else "missing_credentials"
            self.log(f"Simulating Instagram push ({reason}).", "WARNING")
            return {"status": "simulated", "reason": reason}

        try:
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
        """Push content to Facebook Page feed via Graph API."""
        if not self.is_channel_enabled("facebook"):
            return {"status": "skipped", "reason": "channel_not_in_list"}

        self.log("Pushing to Facebook Page...")
        access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        page_id = os.getenv("FACEBOOK_PAGE_ID")

        if self.dry_run or not all([access_token, page_id]):
            reason = "dry_run" if self.dry_run else "missing_credentials"
            self.log(f"Simulating Facebook push ({reason}).", "WARNING")
            return {"status": "simulated", "reason": reason}

        try:
            url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
            payload = {
                "message": message,
                "access_token": access_token
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
        # X API v2 works well with OAuth 1.0a for simple posting
        api_key = os.getenv("X_API_KEY")
        api_secret = os.getenv("X_API_SECRET")
        access_token = os.getenv("X_ACCESS_TOKEN")
        access_secret = os.getenv("X_ACCESS_SECRET")

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
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

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
        base_url = os.getenv("WORDPRESS_BASE_URL")
        username = os.getenv("WORDPRESS_USERNAME")
        app_password = os.getenv("WORDPRESS_APP_PASSWORD")
        status = os.getenv("BLOG_POST_STATUS", "draft").lower()

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

    def push_to_tiktok(self, caption: str, video_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Push content to TikTok via Content Posting API.

        Note: TikTok API requires pre-uploaded video. This implementation assumes
        video is already hosted and accessible via URL.
        """
        if not self.is_channel_enabled("tiktok"):
            return {"status": "skipped", "reason": "channel_not_in_list"}

        self.log("Pushing to TikTok...")
        access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        video_url = video_url or os.getenv("TIKTOK_VIDEO_URL")

        if self.dry_run or not all([access_token, video_url]):
            reason = "dry_run" if self.dry_run else "missing_credentials"
            self.log(f"Simulating TikTok push ({reason}).", "WARNING")
            return {"status": "simulated", "reason": reason, "message": "TikTok post scheduled"}

        try:
            # TikTok Content Posting API v2
            url = "https://open.tiktokapis.com/v2/post/publish/video/init/"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "post_info": {
                    "title": caption[:150],  # TikTok has character limits
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": video_url
                }
            }

            res = requests.post(url, headers=headers, json=payload, timeout=30)
            data = res.json()

            if res.status_code == 200 and data.get("data", {}).get("publish_id"):
                publish_id = data["data"]["publish_id"]
                self.log(f"TikTok video queued for publishing: {publish_id}")
                return {"status": "sent", "publish_id": publish_id}
            else:
                error_msg = data.get("error", {}).get("message", "Unknown error")
                return {"status": "failed", "error": error_msg}

        except Exception as e:
            self.log(f"Failed to push to TikTok: {e}", "ERROR")
            return {"status": "failed", "error": str(e)}

    def schedule_post(
        self,
        platform: str,
        content: Dict[str, Any],
        scheduled_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a post for future publication.

        Args:
            platform: Target platform (instagram, tiktok, facebook, x)
            content: Content dictionary with caption, media URLs, etc.
            scheduled_time: ISO format timestamp for scheduling

        Returns:
            Status dictionary
        """
        self.log(f"Scheduling {platform} post for {scheduled_time or 'immediate'} publication...")

        # For now, this creates a scheduling record in memory
        # In production, this would integrate with platform scheduling APIs or cron jobs
        schedule_record = {
            "platform": platform,
            "content": content,
            "scheduled_time": scheduled_time or datetime.utcnow().isoformat(),
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        }

        # Store in memory for tracking
        self.memory.append("scheduled_posts", schedule_record, agent_id=self.role_name)

        return {"status": "scheduled", "record": schedule_record}

    def _generic_execution(self, task: AgentTask) -> AgentOutput:
        return AgentOutput(
            task_id=task.task_id,
            agent_role=self.role,
            outputs={"result": "Generic execution not implemented"},
            status=TaskStatus.COMPLETED,
        )
