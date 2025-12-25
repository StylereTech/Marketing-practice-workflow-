# 🚀 PulsePilot - Multi-Agent Marketing Orchestration System

<div align="center">

**Autonomous marketing campaign execution powered by specialized AI agents**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 📋 Overview

PulsePilot is a sophisticated multi-agent system that orchestrates end-to-end marketing campaigns through specialized AI agents. Each agent has a distinct role, working together through a shared memory system to execute campaigns from strategy to analytics.

### Architecture

```
🧭 Agent 0: Marketing Orchestrator
   ├── 🧠 Agent 1: Market Intelligence (ICP, messaging, positioning)
   ├── ✍️  Agent 2: Content Production (copy, assets, variations)
   ├── 📣 Agent 3: Distribution & Growth (channels, targeting, budget)
   └── 📊 Agent 4: Analytics & Learning (KPIs, monitoring, optimization)

🗂️  Shared Memory: Single source of truth for all campaign data
```

## 🎯 Key Features

- **Autonomous Campaign Execution**: 30-day campaign cycles with minimal human intervention
- **Multi-AI Collaboration**: Claude, ChatGPT, and Gemini working together for optimal content
- **Social Media Automation**: Automated Instagram & TikTok post generation and scheduling
- **Specialist Agents**: Each agent focuses on a specific domain (strategy, content, distribution, analytics)
- **Shared Memory Architecture**: Centralized knowledge base prevents information silos
- **Human-in-the-Loop Checkpoints**: Strategic approval gates at critical decision points
- **Iterative Optimization**: Weekly performance analysis and automatic adjustments
- **Production-Ready**: Type-safe, well-tested, and properly structured

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Marketing-practice-workflow-

# Install dependencies with Poetry
poetry install

# Or with pip
pip install -e .

# For social media automation (includes Gemini support)
pip install google-generativeai
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# For multi-AI collaboration:
# OPENAI_API_KEY=your_chatgpt_key
# ANTHROPIC_API_KEY=your_claude_key
# GOOGLE_API_KEY=your_gemini_key
#
# For social media deployment:
# INSTAGRAM_ACCESS_TOKEN=your_token
# TIKTOK_ACCESS_TOKEN=your_token
```

### Run Your First Campaign

```bash
# Run the example campaign
poetry run python examples/run_campaign.py

# Or use the CLI
poetry run pulsepilot campaign create \
  --company "Your Company" \
  --icp "B2B SaaS CTOs" \
  --budget 50000 \
  --timeline 30
```

### Social Media Automation (NEW!)

```bash
# Generate social media posts with AI collaboration
python examples/stylere_social_automation.py

# Start the daily scheduler
python social_media_scheduler.py --mode daemon

# See full documentation
cat docs/SOCIAL_MEDIA_AUTOMATION.md
```

## 📖 Campaign Execution Flow

### Phase 1: Initialization (Day 0)
- Company brief intake
- ICP definition
- Budget & timeline setting
- **CHECKPOINT**: Approve overall strategy

### Phase 2: Strategy Definition (Days 1-3)
- Agent 1 refines ICP and pain points
- Creates messaging framework
- Develops value proposition
- **CHECKPOINT**: Approve messaging

### Phase 3: Parallel Execution (Days 4-10)
- Agent 2 creates content assets
- Agent 3 builds distribution plan
- Shared memory coordinates work
- **CHECKPOINT**: Approve launch

### Phase 4: Launch (Day 11)
- Deploy ads and sequences
- Enable sales outbound
- Begin performance tracking

### Phase 5: Feedback Loop (Days 12-30)
- Weekly performance analysis
- Automatic optimization
- Variation testing
- Continuous improvement

### Phase 6: Campaign Close
- Final performance analysis
- Learnings documentation
- Knowledge archival

### Phase 7: External Deployment (Automatic)
Phase 7 runs immediately after Phase 6. It acts as the final bridge between the AI agents and the real world, pushing a summary report to your configured external platforms.

#### What it sends:
A structured summary payload including:
- 🚀 Campaign Name & ID
- 📋 Status (Completed/Interrupted)
- ✍️ Asset count (Landing pages, posts, etc.)
- 📣 Channel count used

#### Environment Variables Required:
| Channel | Env Var | Description |
|---------|---------|-------------|
| **Global** | `DEPLOYMENT_ENABLED` | `true/false` (Master switch) |
| **Global** | `DEPLOYMENT_CHANNELS` | Comma-separated list (e.g., `telegram,email`) |
| **Global** | `DEPLOYMENT_DRY_RUN` | `true/false` (If true, forces simulation) |
| **Telegram**| `TELEGRAM_BOT_TOKEN`| Bot API token from @BotFather |
| **Telegram**| `TELEGRAM_CHAT_ID` | Your Chat ID (Use helper tool below) |
| **X** | `X_API_KEY` / `X_API_SECRET` | Consumer Keys |
| **X** | `X_ACCESS_TOKEN` / `X_ACCESS_SECRET` | Authentication Tokens |
| **Instagram** | `INSTAGRAM_ACCESS_TOKEN` | Meta Graph User Access Token |
| **Instagram** | `INSTAGRAM_IG_USER_ID` | IG Business Account ID |
| **Instagram** | `INSTAGRAM_IMAGE_URL` | Hosted URL of image to post |
| **Facebook** | `FACEBOOK_PAGE_ACCESS_TOKEN` | Page Access Token |
| **Facebook** | `FACEBOOK_PAGE_ID` | Facebook Page ID |
| **WordPress** | `WORDPRESS_BASE_URL` | e.g. `https://yourblog.com` |
| **WordPress** | `WORDPRESS_USERNAME` | Your WP username |
| **WordPress** | `WORDPRESS_APP_PASSWORD` | WP Application Password |
| **WordPress** | `BLOG_POST_STATUS` | `draft` or `publish` (default `draft`) |
| **Email** | `SMTP_USER` / `SMTP_PASS`| SMTP credentials |
| **Email** | `NOTIFY_EMAIL` | Destination address |

#### Running Locally:
1. **Simulated Mode**: Run without any env vars. Phase 7 will log "simulated" for active channels.
2. **Real Mode**: Fill in `.env` with real credentials.
3. **Telegram Helper**: Run `python -m pulsepilot.tools.telegram_get_chat_id` to find your Chat ID after messaging your bot.

### ♾️ 24/7 Monitoring (Scheduler)

PulsePilot includes a scheduler to monitor your campaigns in the background once they have launched.

**How to run**:
```bash
python scheduler.py 24
```
*(The number `24` is the interval in hours between checks)*

**What it does**:
1. Scans `memory_store/` for any campaigns in the `feedback` phase.
2. Runs a performance analysis step for each active campaign.
3. If the AI finds new optimization recommendations, it sends a summary alert to your **Telegram**.
4. Sleeps until the next interval.

### Real Deployment Example (.env)

```env
# Master Switches
DEPLOYMENT_ENABLED=true
DEPLOYMENT_CHANNELS=telegram,x,blog
DEPLOYMENT_DRY_RUN=false

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=987654321

# X (Twitter) - OAuth 1.0a
X_API_KEY=your_consumer_key
X_API_SECRET=your_consumer_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_SECRET=your_access_token_secret

# WordPress
WORDPRESS_BASE_URL=https://myblog.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=abcd efgh ijkl mnop
BLOG_POST_STATUS=draft

# Facebook
FACEBOOK_PAGE_ACCESS_TOKEN=EAAG...
FACEBOOK_PAGE_ID=1092837465

# Instagram
INSTAGRAM_ACCESS_TOKEN=EAAG...
INSTAGRAM_IG_USER_ID=178414...
INSTAGRAM_IMAGE_URL=https://example.com/campaign.jpg
```

---

### Verification Checklist

#### 1. WordPress (Blog)
- **Setup**: Set `DEPLOYMENT_CHANNELS=blog` and `BLOG_POST_STATUS=draft`.
- **Run**: `python examples/simple_example.py`
- **Output**: `✅ Blog: sent` in the report table.
- **Verification**: Check your WordPress admin -> Posts. You should see a new draft titled "Campaign Recap: TechCorp".

#### 2. Facebook Page
- **Setup**: Set `DEPLOYMENT_CHANNELS=facebook`.
- **Run**: `python examples/simple_example.py`
- **Output**: `✅ Facebook: sent` with a Post ID.
- **Verification**: Check your Facebook Page. You should see a new post with the campaign summary.

#### 3. Instagram
- **Setup**: Set `DEPLOYMENT_CHANNELS=instagram`. Ensure `INSTAGRAM_IMAGE_URL` is a publicly accessible direct image link.
- **Run**: `python examples/simple_example.py`
- **Output**: `✅ Instagram: sent` with a Media ID.
- **Verification**: Check your Instagram profile. The image should be posted with the summary as a caption.

#### 4. X (Twitter)
- **Setup**: Set `DEPLOYMENT_CHANNELS=x`.
- **Run**: `python examples/simple_example.py`
- **Output**: `✅ X: sent` with a Tweet ID.
- **Verification**: Check your X profile for the new tweet. Note: Text is truncated to 280 chars.

## 🏗️ Project Structure

```
pulsepilot/
├── src/pulsepilot/
│   ├── agents/              # Specialist agent implementations
│   │   ├── orchestrator.py  # Agent 0: Campaign coordinator
│   │   ├── market_intel.py  # Agent 1: Market intelligence
│   │   ├── content.py       # Agent 2: Content production
│   │   ├── distribution.py  # Agent 3: Distribution strategy
│   │   └── analytics.py     # Agent 4: Analytics & learning
│   ├── core/
│   │   ├── memory.py        # Shared memory system
│   │   ├── models.py        # Pydantic data models
│   │   └── llm.py           # LLM interface layer
│   ├── workflows/
│   │   └── campaign.py      # Campaign orchestration logic
│   └── cli.py               # Command-line interface
├── examples/
│   └── run_campaign.py      # Example campaign execution
├── tests/                   # Test suite
├── docs/                    # Additional documentation
└── diagrams/                # Mermaid workflow diagrams
```

## 🔧 Advanced Usage

### Custom Agent Prompts

Each agent uses carefully crafted system prompts stored in `src/pulsepilot/prompts/`. Customize these to match your brand voice and requirements.

### Extending Agents

```python
from pulsepilot.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    async def execute(self, task: dict) -> dict:
        # Your custom logic here
        return {"status": "success", "output": "..."}
```

### Memory Inspection

```python
from pulsepilot.core.memory import SharedMemory

memory = SharedMemory()
messaging = memory.get("messaging_framework")
performance = memory.get("performance_data")
```

## 📊 Example Output

```
🧭 Campaign: B2B SaaS Product Launch
📅 Timeline: 30 days | 💰 Budget: $50,000

✅ Phase 1 Complete: Strategy approved
✅ Phase 2 Complete: Messaging framework ready
  → Pain Point: Legacy systems slow innovation
  → Value Prop: Ship features 3x faster

🔄 Phase 3 In Progress:
  ✍️  Content: 5 LinkedIn posts, 1 landing page, 1 whitepaper
  📣 Distribution: LinkedIn Ads + Email + Outbound

⏳ Next checkpoint: Approve launch (in 2 days)
```

## 📱 Social Media Automation

PulsePilot now includes automated social media post generation using **multi-AI collaboration**:

### How It Works

1. **Claude (Strategy)**: Analyzes brand guidelines and develops content themes
2. **ChatGPT (Creation)**: Generates engaging captions, hooks, and hashtags
3. **Gemini (Refinement)**: Ensures brand consistency and quality

### Features

- ✅ **Automated Daily Posts**: 3 posts per day on Instagram & TikTok
- ✅ **Brand Consistency**: AI-powered brand alignment scoring (0-100)
- ✅ **Smart Scheduling**: Posts at optimal times for maximum engagement
- ✅ **Platform-Specific**: Tailored content for each platform's best practices
- ✅ **Quality Assurance**: Multi-AI review ensures high-quality output

### Quick Start

```bash
# 1. Configure your brand guide
cp brand_guide.json my_brand_guide.json
# Edit with your brand information

# 2. Set up API keys in .env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key
INSTAGRAM_ACCESS_TOKEN=your_token
TIKTOK_ACCESS_TOKEN=your_token

# 3. Generate posts
python examples/stylere_social_automation.py

# 4. Start automated scheduling
python social_media_scheduler.py --mode daemon
```

### Example Output

```
📱 GENERATED POSTS

[Post 1] Instagram Post 1: Style Education
Theme: Building a versatile wardrobe
Best Time: morning
Brand Score: 92/100

Caption:
Your style journey is uniquely yours. We're here to help you
discover what makes you feel most like yourself...

Hashtags: #StyleRe #TimelessFashion #QualityOverQuantity...
```

See [Social Media Automation Documentation](docs/SOCIAL_MEDIA_AUTOMATION.md) for full details.

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pulsepilot

# Run specific test
poetry run pytest tests/test_orchestrator.py
```

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with:
- OpenAI GPT-4 / Anthropic Claude for agent intelligence
- Pydantic for type safety
- Rich for beautiful CLI output

---

**Built with ❤️ by the PulsePilot team**
