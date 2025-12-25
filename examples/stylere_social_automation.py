#!/usr/bin/env python3
"""
Style.re Social Media Automation Example

This example demonstrates how to use PulsePilot's multi-AI collaboration
to automatically generate and schedule social media posts for Style.re.

Features:
- Claude for strategic content planning
- ChatGPT for creative content generation
- Gemini for brand consistency refinement
- Automated scheduling for Instagram and TikTok
- 3 posts per day at optimal times
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pulsepilot.agents.social_media import SocialMediaAgent
from pulsepilot.agents.deployment import DeploymentAgent
from pulsepilot.core.memory import SharedMemory


def load_brand_guide():
    """Load Style.re brand guidelines."""
    brand_guide_path = Path(__file__).parent.parent / "brand_guide.json"

    try:
        with open(brand_guide_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  Brand guide not found, using basic template")
        return {
            "name": "Style.re",
            "tagline": "Redefine Your Style",
            "voice": "Modern, confident, empowering",
            "tone": "Friendly yet sophisticated",
            "values": ["Authenticity", "Quality", "Innovation"],
            "target_audience": {
                "age_range": "25-45",
                "interests": ["Fashion", "Quality", "Personal style"]
            }
        }


def display_brand_summary(brand_guide):
    """Display a summary of the brand guidelines."""
    print("\n" + "=" * 70)
    print("📊 BRAND PROFILE")
    print("=" * 70)
    print(f"\n   Brand: {brand_guide.get('name', 'Unknown')}")
    print(f"   Tagline: {brand_guide.get('tagline', 'N/A')}")

    if 'brand_identity' in brand_guide:
        print(f"\n   Mission: {brand_guide['brand_identity'].get('mission', 'N/A')}")

    if 'voice_and_tone' in brand_guide:
        print(f"\n   Voice: {brand_guide['voice_and_tone'].get('voice', 'N/A')}")

    print("\n   Content Pillars:")
    if 'content_strategy' in brand_guide and 'pillars' in brand_guide['content_strategy']:
        for pillar in brand_guide['content_strategy']['pillars'][:3]:
            print(f"      • {pillar['name']}: {pillar['description']}")
    else:
        print("      • Quality and style")
        print("      • Customer stories")
        print("      • Brand values")

    print("\n" + "=" * 70 + "\n")


def generate_and_review_posts():
    """Main workflow: Generate posts and display for review."""

    print("\n🚀 Style.re Social Media Post Generator")
    print("   Multi-AI Collaboration: Claude + ChatGPT + Gemini")
    print("   Platforms: Instagram & TikTok")
    print("   Daily Schedule: 3 posts per day\n")

    # Load brand guide
    print("📖 Loading brand guidelines...")
    brand_guide = load_brand_guide()
    display_brand_summary(brand_guide)

    # Initialize components
    print("🤖 Initializing AI agents...")
    memory = SharedMemory()
    social_agent = SocialMediaAgent(memory=memory)
    deployment_agent = DeploymentAgent(memory=memory)
    print("   ✓ Claude (Strategy)")
    print("   ✓ ChatGPT (Creation)")
    print("   ✓ Gemini (Refinement)")

    # Generate posts
    print("\n" + "=" * 70)
    print("🎨 GENERATING CONTENT")
    print("=" * 70)

    assets = social_agent.generate_posts_multi_ai(
        brand_guide=brand_guide,
        num_posts=3,
        platforms=["instagram", "tiktok"]
    )

    # Display generated content
    print("\n" + "=" * 70)
    print("📱 GENERATED POSTS")
    print("=" * 70)

    instagram_posts = [a for a in assets if a.metadata.get('platform') == 'instagram']
    tiktok_posts = [a for a in assets if a.metadata.get('platform') == 'tiktok']

    # Display Instagram posts
    print("\n📸 INSTAGRAM POSTS")
    print("-" * 70)
    for i, post in enumerate(instagram_posts, 1):
        metadata = post.metadata
        strategy = metadata.get('strategy', {})

        print(f"\n[Post {i}] {post.title}")
        print(f"Theme: {strategy.get('theme', 'N/A')}")
        print(f"Best Time: {metadata.get('best_time', 'N/A')}")
        print(f"Brand Score: {metadata.get('brand_score', 0)}/100")
        print(f"\nCaption:\n{post.content[:200]}...")

        hashtags = metadata.get('hashtags', [])
        if hashtags:
            print(f"\nHashtags: {' '.join(['#' + tag for tag in hashtags[:8]])}")

        print(f"\nVisual: {metadata.get('visual_description', 'N/A')[:150]}...")

        refinements = metadata.get('refinements', [])
        if refinements:
            print(f"\nRefinements by Gemini:")
            for refinement in refinements[:3]:
                print(f"   • {refinement}")

        print("-" * 70)

    # Display TikTok posts
    print("\n🎵 TIKTOK POSTS")
    print("-" * 70)
    for i, post in enumerate(tiktok_posts, 1):
        metadata = post.metadata
        strategy = metadata.get('strategy', {})

        print(f"\n[Post {i}] {post.title}")
        print(f"Theme: {strategy.get('theme', 'N/A')}")
        print(f"Best Time: {metadata.get('best_time', 'N/A')}")
        print(f"Brand Score: {metadata.get('brand_score', 0)}/100")

        print(f"\nCaption:\n{post.content[:150]}...")

        script = metadata.get('tiktok_script', '')
        if script:
            print(f"\nVideo Script:\n{script[:200]}...")

        print("-" * 70)

    # Brand consistency check
    print("\n" + "=" * 70)
    print("✅ BRAND CONSISTENCY CHECK")
    print("=" * 70)

    total_score = 0
    for post in assets:
        score = post.metadata.get('brand_score', 0)
        total_score += score

    avg_score = total_score / len(assets) if assets else 0

    print(f"\n   Average Brand Alignment Score: {avg_score:.1f}/100")

    if avg_score >= 85:
        print("   Status: ✅ EXCELLENT - All posts align well with brand")
    elif avg_score >= 70:
        print("   Status: ✓ GOOD - Posts align with brand, minor tweaks possible")
    else:
        print("   Status: ⚠️  NEEDS REVIEW - Some posts may need revision")

    # Show AI collaboration details
    print("\n" + "=" * 70)
    print("🤝 AI COLLABORATION WORKFLOW")
    print("=" * 70)
    print("\n   1. Claude (Strategy Agent)")
    print("      → Analyzed brand guidelines")
    print("      → Developed content themes")
    print("      → Defined target emotions")
    print("      → Set messaging priorities")
    print("\n   2. ChatGPT (Creative Agent)")
    print("      → Generated captions and hooks")
    print("      → Created visual descriptions")
    print("      → Wrote TikTok scripts")
    print("      → Developed hashtag strategies")
    print("\n   3. Gemini (Quality Agent)")
    print("      → Checked brand voice alignment")
    print("      → Refined messaging clarity")
    print("      → Validated tone consistency")
    print("      → Scored brand fit")

    # Scheduling summary
    print("\n" + "=" * 70)
    print("📅 RECOMMENDED POSTING SCHEDULE")
    print("=" * 70)

    schedule = [
        {"time": "9:00 AM", "label": "Morning", "platform": "Instagram"},
        {"time": "9:30 AM", "label": "Morning", "platform": "TikTok"},
        {"time": "2:00 PM", "label": "Afternoon", "platform": "Instagram"},
        {"time": "2:30 PM", "label": "Afternoon", "platform": "TikTok"},
        {"time": "7:00 PM", "label": "Evening", "platform": "Instagram"},
        {"time": "7:30 PM", "label": "Evening", "platform": "TikTok"},
    ]

    for i, slot in enumerate(schedule):
        post_num = (i // 2) + 1
        print(f"\n   {slot['time']} ({slot['label']}) - {slot['platform']}")
        print(f"      Post {post_num}")

    # Next steps
    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS")
    print("=" * 70)
    print("\n   To schedule these posts for automatic publishing:")
    print("\n   1. Review and approve the generated content above")
    print("\n   2. Configure your environment variables (.env):")
    print("      - OPENAI_API_KEY (for ChatGPT)")
    print("      - ANTHROPIC_API_KEY (for Claude)")
    print("      - GOOGLE_API_KEY (for Gemini)")
    print("      - INSTAGRAM_ACCESS_TOKEN")
    print("      - INSTAGRAM_IG_USER_ID")
    print("      - TIKTOK_ACCESS_TOKEN")
    print("\n   3. Run the scheduler:")
    print("      $ python social_media_scheduler.py --mode daemon")
    print("\n   4. The scheduler will:")
    print("      - Generate fresh content daily")
    print("      - Post automatically at scheduled times")
    print("      - Maintain brand consistency")
    print("      - Track performance metrics")

    print("\n" + "=" * 70)
    print("✨ Generation Complete!")
    print("=" * 70 + "\n")

    return assets


def demonstrate_brand_check():
    """Demonstrate the brand consistency checker."""

    print("\n" + "=" * 70)
    print("🔍 BRAND CONSISTENCY CHECKER DEMO")
    print("=" * 70)

    brand_guide = load_brand_guide()
    memory = SharedMemory()
    social_agent = SocialMediaAgent(memory=memory)

    # Test with good content
    good_content = """
    Your style journey is uniquely yours. We're here to help you discover
    what makes you feel most like yourself. Our new collection features
    timeless pieces crafted with care—because your wardrobe should work
    as hard as you do. ✨

    #StyleRe #TimelessFashion #QualityOverQuantity
    """

    print("\n   Testing GOOD example:")
    print(f"   {good_content.strip()[:100]}...")

    result = social_agent.check_brand_consistency(good_content, brand_guide)
    print(f"\n   Overall Score: {result.get('overall_score', 0)}/100")
    print(f"   Approved: {result.get('approved', False)}")
    print(f"   Feedback: {result.get('feedback', 'N/A')[:150]}...")

    # Test with poor content
    bad_content = """
    🔥🔥🔥 SALE ALERT!!! 🔥🔥🔥
    BUY NOW OR MISS OUT FOREVER!!!
    Everyone is buying this, you should too! Limited stock!
    Don't be the only one without this must-have item!!!
    """

    print("\n\n   Testing POOR example:")
    print(f"   {bad_content.strip()[:100]}...")

    result = social_agent.check_brand_consistency(bad_content, brand_guide)
    print(f"\n   Overall Score: {result.get('overall_score', 0)}/100")
    print(f"   Approved: {result.get('approved', False)}")
    print(f"   Feedback: {result.get('feedback', 'N/A')[:200]}...")

    suggestions = result.get('suggestions', [])
    if suggestions:
        print(f"\n   Suggestions for improvement:")
        for suggestion in suggestions[:3]:
            print(f"      • {suggestion}")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Style.re Social Media Automation Demo")
    parser.add_argument(
        "--demo",
        choices=["generate", "brand-check", "all"],
        default="generate",
        help="Which demo to run"
    )

    args = parser.parse_args()

    try:
        if args.demo == "generate":
            generate_and_review_posts()
        elif args.demo == "brand-check":
            demonstrate_brand_check()
        else:  # all
            generate_and_review_posts()
            demonstrate_brand_check()

    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
