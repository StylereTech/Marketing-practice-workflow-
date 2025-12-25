#!/usr/bin/env python3
"""
Social Media Scheduler for Style.re

Automatically generates and schedules social media posts daily.
Runs as a background service to maintain consistent posting schedule.
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pulsepilot.agents.social_media import SocialMediaAgent
from pulsepilot.agents.deployment import DeploymentAgent
from pulsepilot.core.memory import SharedMemory


class SocialMediaScheduler:
    """
    Daily social media post scheduler.

    Schedule:
    - 3 posts per day
    - Morning: 9:00 AM
    - Afternoon: 2:00 PM
    - Evening: 7:00 PM

    Platforms:
    - Instagram
    - TikTok
    """

    def __init__(self, brand_guide_path: str):
        """
        Initialize scheduler.

        Args:
            brand_guide_path: Path to brand guidelines JSON file
        """
        self.brand_guide = self._load_brand_guide(brand_guide_path)
        self.memory = SharedMemory()
        self.social_agent = SocialMediaAgent(memory=self.memory)
        self.deployment_agent = DeploymentAgent(memory=self.memory)

        # Posting schedule (hour of day in 24h format)
        self.posting_times = [
            {"hour": 9, "label": "morning"},
            {"hour": 14, "label": "afternoon"},
            {"hour": 19, "label": "evening"}
        ]

        print("📱 Social Media Scheduler initialized")
        print(f"   Brand: {self.brand_guide.get('name', 'Unknown')}")
        print(f"   Posts per day: {len(self.posting_times)}")
        print(f"   Platforms: Instagram, TikTok")

    def _load_brand_guide(self, path: str) -> dict:
        """Load brand guidelines from JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Brand guide not found at {path}, using defaults")
            return self._get_default_brand_guide()

    def _get_default_brand_guide(self) -> dict:
        """Get default brand guidelines for Style.re."""
        return {
            "name": "Style.re",
            "tagline": "Redefine Your Style",
            "voice": "Modern, confident, empowering",
            "tone": "Friendly yet sophisticated, inspiring",
            "values": [
                "Authenticity",
                "Self-expression",
                "Quality",
                "Innovation",
                "Inclusivity"
            ],
            "themes": [
                "Personal style transformation",
                "Fashion confidence",
                "Trend curation",
                "Quality craftsmanship",
                "Sustainable fashion"
            ],
            "visual_style": {
                "aesthetic": "Clean, modern, minimalist with bold accents",
                "colors": ["Black", "White", "Gold accents", "Earth tones"],
                "photography": "High-quality product shots, lifestyle imagery, authentic moments"
            },
            "target_audience": {
                "age_range": "25-45",
                "interests": ["Fashion", "Quality", "Self-improvement", "Aesthetics"],
                "values": ["Authenticity", "Quality over quantity", "Personal growth"]
            },
            "content_pillars": [
                "Style education and tips",
                "Product showcases and styling",
                "Customer stories and transformations",
                "Behind-the-scenes and brand values",
                "Trend analysis and commentary"
            ],
            "hashtag_strategy": {
                "branded": ["#StyleRe", "#RedefineYourStyle"],
                "category": ["#FashionStyle", "#OOTD", "#StyleInspo", "#FashionDaily"],
                "community": ["#FashionCommunity", "#StyleTips", "#FashionLovers"]
            },
            "dont_use": [
                "Overly promotional language",
                "Excessive emojis",
                "Clickbait tactics",
                "Negative or comparison-based messaging"
            ]
        }

    def generate_daily_content(self) -> list:
        """
        Generate 3 posts for the day using multi-AI collaboration.

        Returns:
            List of ContentAsset objects
        """
        print("\n🎨 Generating daily content with AI collaboration...")
        print("   Strategy: Claude")
        print("   Creation: ChatGPT")
        print("   Refinement: Gemini")

        assets = self.social_agent.generate_posts_multi_ai(
            brand_guide=self.brand_guide,
            num_posts=3,
            platforms=["instagram", "tiktok"]
        )

        print(f"\n✅ Generated {len(assets)} posts")

        # Display summary
        for asset in assets:
            metadata = asset.metadata
            print(f"\n   📄 {asset.title}")
            print(f"      Platform: {metadata.get('platform', 'unknown')}")
            print(f"      Theme: {metadata.get('strategy', {}).get('theme', 'N/A')}")
            print(f"      Best time: {metadata.get('best_time', 'N/A')}")
            print(f"      Brand score: {metadata.get('brand_score', 0)}/100")

        return assets

    def schedule_posts(self, assets: list) -> None:
        """
        Schedule posts for the day at designated times.

        Args:
            assets: List of ContentAsset objects to schedule
        """
        print("\n📅 Scheduling posts for today...")

        now = datetime.now()
        scheduled_count = 0

        # Group assets by platform
        instagram_posts = [a for a in assets if a.metadata.get('platform') == 'instagram']
        tiktok_posts = [a for a in assets if a.metadata.get('platform') == 'tiktok']

        for i, time_slot in enumerate(self.posting_times):
            # Calculate scheduled time
            scheduled_time = now.replace(
                hour=time_slot['hour'],
                minute=0,
                second=0,
                microsecond=0
            )

            # If time has passed today, schedule for tomorrow
            if scheduled_time < now:
                scheduled_time += timedelta(days=1)

            # Schedule Instagram post
            if i < len(instagram_posts):
                ig_post = instagram_posts[i]
                self._schedule_single_post(
                    platform="instagram",
                    asset=ig_post,
                    scheduled_time=scheduled_time
                )
                scheduled_count += 1

            # Schedule TikTok post (offset by 30 minutes)
            if i < len(tiktok_posts):
                tiktok_time = scheduled_time + timedelta(minutes=30)
                tt_post = tiktok_posts[i]
                self._schedule_single_post(
                    platform="tiktok",
                    asset=tt_post,
                    scheduled_time=tiktok_time
                )
                scheduled_count += 1

        print(f"\n✅ Scheduled {scheduled_count} posts")

    def _schedule_single_post(
        self,
        platform: str,
        asset,
        scheduled_time: datetime
    ) -> None:
        """Schedule a single post."""
        content = {
            "caption": asset.content,
            "hashtags": asset.metadata.get('hashtags', []),
            "visual_description": asset.metadata.get('visual_description', ''),
        }

        # Add platform-specific content
        if platform == "tiktok":
            content["tiktok_script"] = asset.metadata.get('tiktok_script', '')

        result = self.deployment_agent.schedule_post(
            platform=platform,
            content=content,
            scheduled_time=scheduled_time.isoformat()
        )

        time_str = scheduled_time.strftime("%I:%M %p")
        print(f"   ⏰ {platform.capitalize()}: {time_str}")
        print(f"      {asset.title[:60]}...")

    def publish_scheduled_posts(self) -> None:
        """
        Check for and publish any posts scheduled for the current time.

        This should be called every minute by the scheduler daemon.
        """
        now = datetime.now()
        scheduled_posts = self.memory.read("scheduled_posts", default=[])

        for post_record in scheduled_posts:
            if post_record.get("status") != "scheduled":
                continue

            scheduled_time = datetime.fromisoformat(post_record["scheduled_time"])

            # Check if it's time to publish (within 5 minute window)
            time_diff = abs((now - scheduled_time).total_seconds())

            if time_diff <= 300:  # Within 5 minutes
                self._publish_post(post_record)

    def _publish_post(self, post_record: dict) -> None:
        """Publish a scheduled post."""
        platform = post_record["platform"]
        content = post_record["content"]

        print(f"\n📤 Publishing to {platform}...")

        try:
            if platform == "instagram":
                result = self.deployment_agent.push_to_instagram(
                    caption=self._format_instagram_caption(content),
                    image_url=content.get("image_url")
                )
            elif platform == "tiktok":
                result = self.deployment_agent.push_to_tiktok(
                    caption=self._format_tiktok_caption(content),
                    video_url=content.get("video_url")
                )
            else:
                result = {"status": "failed", "error": f"Unknown platform: {platform}"}

            # Update status
            if result.get("status") == "sent":
                post_record["status"] = "published"
                post_record["published_at"] = datetime.now().isoformat()
                print(f"✅ Successfully published to {platform}")
            else:
                print(f"⚠️  Failed to publish: {result.get('error', 'Unknown error')}")
                post_record["status"] = "failed"
                post_record["error"] = result.get("error")

        except Exception as e:
            print(f"❌ Error publishing to {platform}: {e}")
            post_record["status"] = "failed"
            post_record["error"] = str(e)

    def _format_instagram_caption(self, content: dict) -> str:
        """Format Instagram caption with hashtags."""
        caption = content.get("caption", "")
        hashtags = content.get("hashtags", [])

        if hashtags:
            hashtag_str = " ".join(f"#{tag}" for tag in hashtags)
            return f"{caption}\n\n{hashtag_str}"

        return caption

    def _format_tiktok_caption(self, content: dict) -> str:
        """Format TikTok caption."""
        caption = content.get("caption", "")
        hashtags = content.get("hashtags", [])[:5]  # TikTok recommends 3-5 hashtags

        if hashtags:
            hashtag_str = " ".join(f"#{tag}" for tag in hashtags)
            return f"{caption} {hashtag_str}"

        return caption

    def run_daily_generation(self) -> None:
        """Run the daily content generation and scheduling workflow."""
        print("\n" + "=" * 60)
        print("🚀 Starting Daily Social Media Generation")
        print("=" * 60)

        # Generate content
        assets = self.generate_daily_content()

        # Schedule posts
        self.schedule_posts(assets)

        print("\n" + "=" * 60)
        print("✅ Daily generation complete!")
        print("=" * 60)

    def run_daemon(self, check_interval: int = 60) -> None:
        """
        Run as a daemon that generates content daily and publishes on schedule.

        Args:
            check_interval: Seconds between checks for scheduled posts (default: 60)
        """
        print("\n" + "=" * 60)
        print("🤖 Social Media Scheduler - Daemon Mode")
        print("=" * 60)
        print(f"   Check interval: {check_interval} seconds")
        print("   Press Ctrl+C to stop\n")

        last_generation_day = None

        try:
            while True:
                now = datetime.now()

                # Generate new content once per day (at midnight or first run)
                if last_generation_day != now.date():
                    self.run_daily_generation()
                    last_generation_day = now.date()

                # Check for posts to publish
                self.publish_scheduled_posts()

                # Wait for next check
                time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n\n👋 Scheduler stopped by user")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Social Media Scheduler for Style.re"
    )
    parser.add_argument(
        "--brand-guide",
        default="brand_guide.json",
        help="Path to brand guidelines JSON file"
    )
    parser.add_argument(
        "--mode",
        choices=["generate", "daemon"],
        default="generate",
        help="Run mode: 'generate' for one-time generation, 'daemon' for continuous scheduling"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds for daemon mode (default: 60)"
    )

    args = parser.parse_args()

    # Initialize scheduler
    scheduler = SocialMediaScheduler(args.brand_guide)

    if args.mode == "generate":
        # One-time generation
        scheduler.run_daily_generation()
    else:
        # Daemon mode
        scheduler.run_daemon(check_interval=args.interval)


if __name__ == "__main__":
    main()
