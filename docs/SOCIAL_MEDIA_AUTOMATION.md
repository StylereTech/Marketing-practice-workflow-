# 📱 Social Media Automation - Multi-AI Collaboration

## Overview

PulsePilot's Social Media Automation system uses **three AI models working together** to generate high-quality, brand-consistent social media posts for Instagram and TikTok. This collaborative approach combines the strengths of each AI:

- **Claude (Anthropic)**: Strategic content planning and brand consistency
- **ChatGPT (OpenAI)**: Creative content generation and copywriting
- **Gemini (Google)**: Refinement and quality assurance

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SOCIAL MEDIA WORKFLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. STRATEGY (Claude)                                        │
│     ├─ Analyze brand guidelines                             │
│     ├─ Define content themes                                │
│     ├─ Set target emotions                                  │
│     └─ Plan messaging priorities                            │
│                                                              │
│  2. CREATION (ChatGPT)                                       │
│     ├─ Generate captions                                    │
│     ├─ Write hooks and CTAs                                 │
│     ├─ Create TikTok scripts                                │
│     └─ Develop hashtag strategies                           │
│                                                              │
│  3. REFINEMENT (Gemini)                                      │
│     ├─ Check brand alignment                                │
│     ├─ Refine messaging clarity                             │
│     ├─ Validate tone consistency                            │
│     └─ Score brand fit (0-100)                              │
│                                                              │
│  4. DEPLOYMENT                                               │
│     ├─ Schedule posts for optimal times                     │
│     ├─ Publish to Instagram & TikTok                        │
│     └─ Track performance metrics                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Installation

```bash
# Install required dependencies
pip install google-generativeai  # For Gemini support

# Or if using Poetry
poetry add google-generativeai
```

### 2. Configuration

Create a `.env` file with your API keys:

```bash
# Required: All three AI providers
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_chatgpt_api_key
GOOGLE_API_KEY=your_gemini_api_key

# Required: Social media platforms
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
INSTAGRAM_IG_USER_ID=your_instagram_user_id
TIKTOK_ACCESS_TOKEN=your_tiktok_token

# Deployment settings
DEPLOYMENT_ENABLED=true
DEPLOYMENT_CHANNELS=instagram,tiktok
DEPLOYMENT_DRY_RUN=false
```

### 3. Create Brand Guidelines

Create a `brand_guide.json` file with your brand information:

```json
{
  "name": "Your Brand",
  "tagline": "Your Tagline",
  "voice": "Modern, confident, empowering",
  "tone": "Friendly yet sophisticated",
  "values": ["Authenticity", "Quality", "Innovation"],
  "content_pillars": [
    {
      "name": "Education",
      "description": "Tips and insights"
    },
    {
      "name": "Product Showcases",
      "description": "Feature products and styling"
    }
  ],
  "hashtag_strategy": {
    "branded_tags": ["#YourBrand"],
    "category_tags": ["#Industry", "#Category"],
    "community_tags": ["#Community"]
  }
}
```

See `brand_guide.json` in the root directory for a complete Style.re example.

### 4. Run the Example

```bash
# Generate sample posts
python examples/stylere_social_automation.py

# Run with brand consistency checking
python examples/stylere_social_automation.py --demo all
```

### 5. Start the Scheduler

```bash
# Generate posts once
python social_media_scheduler.py --mode generate

# Run as a daemon (continuous scheduling)
python social_media_scheduler.py --mode daemon

# Custom check interval (in seconds)
python social_media_scheduler.py --mode daemon --interval 300
```

## Features

### Multi-AI Collaboration

Each AI contributes its strengths:

**Claude's Role:**
- Strategic content planning
- Brand voice analysis
- Message hierarchy development
- Risk identification
- Consistency validation

**ChatGPT's Role:**
- Creative copywriting
- Engaging hooks and CTAs
- Platform-native content
- Hashtag selection
- Visual descriptions

**Gemini's Role:**
- Quality assurance
- Brand alignment scoring
- Message clarity refinement
- Tone consistency checks
- Suggested improvements

### Daily Posting Schedule

**Default Schedule (customizable):**
- 9:00 AM - Morning post (Instagram)
- 9:30 AM - Morning post (TikTok)
- 2:00 PM - Afternoon post (Instagram)
- 2:30 PM - Afternoon post (TikTok)
- 7:00 PM - Evening post (Instagram)
- 7:30 PM - Evening post (TikTok)

### Brand Consistency Scoring

Every post receives a brand alignment score (0-100) based on:
- Voice/tone alignment
- Message consistency
- Visual alignment
- Values alignment
- Overall brand fit

**Scoring Guide:**
- 85-100: Excellent alignment
- 70-84: Good alignment, minor tweaks possible
- Below 70: Needs review and revision

## Platform-Specific Features

### Instagram

**Caption Guidelines:**
- Length: 125-150 words ideal
- Structure: Hook → Value/Story → CTA
- Hashtags: 8-12 relevant tags
- Emojis: Used sparingly

**Content Types:**
- Product showcases
- Lifestyle imagery
- Customer stories
- Behind-the-scenes
- Educational content

### TikTok

**Video Script Guidelines:**
- Length: 15-30 seconds ideal
- Hook: First 3 seconds critical
- Format: Authentic and trend-aware
- Style: Conversational and native

**Caption Guidelines:**
- Length: 100 words maximum
- Hashtags: 3-5 relevant tags
- Style: Platform-native, conversational

## API Integration

### Instagram (Facebook Graph API)

**Setup:**
1. Create a Facebook Developer account
2. Create an app and configure Instagram Basic Display
3. Generate access token for Instagram Business account
4. Get your Instagram User ID

**Required Environment Variables:**
```bash
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_IG_USER_ID=your_user_id
INSTAGRAM_IMAGE_URL=https://url-to-default-image.jpg
```

### TikTok (Content Posting API)

**Setup:**
1. Apply for TikTok for Developers access
2. Create an app in TikTok Developer Portal
3. Request Content Posting API permissions
4. Generate access token

**Required Environment Variables:**
```bash
TIKTOK_ACCESS_TOKEN=your_token
TIKTOK_VIDEO_URL=https://url-to-default-video.mp4
```

**Note:** TikTok requires videos to be pre-uploaded and accessible via URL.

## Usage Examples

### Programmatic Usage

```python
from pulsepilot.agents.social_media import SocialMediaAgent
from pulsepilot.core.memory import SharedMemory
import json

# Load brand guide
with open('brand_guide.json') as f:
    brand_guide = json.load(f)

# Initialize agent
memory = SharedMemory()
social_agent = SocialMediaAgent(memory=memory)

# Generate posts
assets = social_agent.generate_posts_multi_ai(
    brand_guide=brand_guide,
    num_posts=3,
    platforms=["instagram", "tiktok"]
)

# Review results
for asset in assets:
    print(f"Platform: {asset.metadata['platform']}")
    print(f"Caption: {asset.content}")
    print(f"Brand Score: {asset.metadata['brand_score']}/100")
    print("-" * 50)
```

### Brand Consistency Check

```python
# Check if content aligns with brand
result = social_agent.check_brand_consistency(
    content="Your post caption here...",
    brand_guide=brand_guide
)

print(f"Overall Score: {result['overall_score']}/100")
print(f"Approved: {result['approved']}")
print(f"Feedback: {result['feedback']}")

if result['suggestions']:
    print("Suggestions:")
    for suggestion in result['suggestions']:
        print(f"  - {suggestion}")
```

### Scheduling Posts

```python
from pulsepilot.agents.deployment import DeploymentAgent
from datetime import datetime, timedelta

deployment_agent = DeploymentAgent(memory=memory)

# Schedule a post for tomorrow at 9 AM
tomorrow_9am = datetime.now() + timedelta(days=1)
tomorrow_9am = tomorrow_9am.replace(hour=9, minute=0, second=0)

deployment_agent.schedule_post(
    platform="instagram",
    content={
        "caption": "Your caption here...",
        "hashtags": ["tag1", "tag2"],
        "image_url": "https://..."
    },
    scheduled_time=tomorrow_9am.isoformat()
)
```

## Best Practices

### Content Strategy

1. **Maintain Brand Voice:**
   - Always use the brand guide as the source of truth
   - Review generated content before publishing
   - Adjust AI outputs to match evolving brand needs

2. **Diversify Content:**
   - Mix educational, promotional, and community content
   - Follow the 80/20 rule: 80% value, 20% promotion
   - Rotate through content pillars

3. **Optimize Timing:**
   - Analyze your audience's active hours
   - Adjust posting times based on engagement data
   - Test different time slots for optimal reach

### Quality Assurance

1. **Review Brand Scores:**
   - Aim for 85+ on all posts
   - Investigate scores below 70
   - Use feedback to refine brand guide

2. **A/B Testing:**
   - Test different hooks and CTAs
   - Compare performance across content types
   - Iterate based on results

3. **Monitor Performance:**
   - Track engagement metrics
   - Identify top-performing content
   - Adjust strategy accordingly

### Safety and Compliance

1. **Review Before Publishing:**
   - Always review AI-generated content
   - Verify factual accuracy
   - Ensure compliance with platform policies

2. **Respect Platform Guidelines:**
   - Follow Instagram and TikTok community guidelines
   - Avoid prohibited content
   - Use authentic imagery and videos

3. **Protect Brand Reputation:**
   - Avoid controversial topics without review
   - Maintain consistent quality standards
   - Have a crisis management plan

## Troubleshooting

### Common Issues

**Issue: Low brand consistency scores**
- Solution: Review and enhance your brand guide
- Ensure brand guide includes clear examples
- Provide more detailed voice/tone guidelines

**Issue: Posts not publishing to social media**
- Solution: Check API credentials and permissions
- Verify access tokens are valid
- Ensure media URLs are accessible
- Check DEPLOYMENT_DRY_RUN setting

**Issue: Generic or repetitive content**
- Solution: Provide more diverse content pillars
- Include specific brand examples in guide
- Adjust temperature settings for more creativity

**Issue: AI provider errors**
- Solution: Verify all API keys are correct
- Check API rate limits and quotas
- Ensure sufficient API credits

### Debug Mode

Enable detailed logging:

```bash
LOG_LEVEL=DEBUG python social_media_scheduler.py
```

### Dry Run Mode

Test without publishing:

```bash
DEPLOYMENT_DRY_RUN=true python examples/stylere_social_automation.py
```

## Advanced Configuration

### Custom Posting Schedule

Modify `social_media_scheduler.py`:

```python
self.posting_times = [
    {"hour": 10, "label": "morning"},
    {"hour": 15, "label": "afternoon"},
    {"hour": 20, "label": "evening"}
]
```

### Custom AI Models

Specify different models:

```python
social_agent = SocialMediaAgent(memory=memory)

# Override with specific models
social_agent.claude = LLMInterface(
    provider="anthropic",
    model="claude-3-opus-20240229"
)

social_agent.chatgpt = LLMInterface(
    provider="openai",
    model="gpt-4-turbo-preview"
)

social_agent.gemini = LLMInterface(
    provider="google",
    model="gemini-1.5-pro"
)
```

### Add More Platforms

Extend `DeploymentAgent` to support additional platforms:

```python
def push_to_linkedin(self, content: str) -> Dict[str, Any]:
    """Add LinkedIn support"""
    # Implementation here
    pass
```

## Performance Optimization

### Rate Limiting

Respect API rate limits:
- Instagram: 200 calls per hour
- TikTok: Varies by endpoint
- AI APIs: Check provider limits

### Caching

Cache generated content in memory:

```python
# Content is automatically cached in SharedMemory
assets = memory.read("generated_assets", default=[])
```

### Cost Management

Monitor AI API usage:
- Use appropriate model sizes
- Cache reusable content
- Batch operations when possible

## Support and Resources

### Getting API Keys

- **Anthropic (Claude):** https://console.anthropic.com/
- **OpenAI (ChatGPT):** https://platform.openai.com/api-keys
- **Google (Gemini):** https://makersuite.google.com/app/apikey
- **Instagram/Facebook:** https://developers.facebook.com/
- **TikTok:** https://developers.tiktok.com/

### Documentation

- Instagram Graph API: https://developers.facebook.com/docs/instagram-api
- TikTok API: https://developers.tiktok.com/doc/content-posting-api-get-started
- PulsePilot Docs: See `/docs` directory

### Examples

- Basic Usage: `examples/stylere_social_automation.py`
- Scheduler: `social_media_scheduler.py`
- Brand Guide: `brand_guide.json`

---

**Built with ❤️ using Claude, ChatGPT, and Gemini**
