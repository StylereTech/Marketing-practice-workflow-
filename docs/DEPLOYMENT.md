# Deployment Guide

## Production Deployment

### Prerequisites

- Python 3.10+
- OpenAI API key OR Anthropic API key
- 2GB RAM minimum
- Disk space for memory persistence

### Installation

#### Option 1: Poetry (Recommended)

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Clone repository
git clone <repository-url>
cd Marketing-practice-workflow-

# Install dependencies
poetry install --no-dev

# Activate environment
poetry shell
```

#### Option 2: pip

```bash
# Clone repository
git clone <repository-url>
cd Marketing-practice-workflow-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .
```

### Configuration

#### 1. Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env
```

Required variables:
```env
# Choose one:
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...

# Optional
ORCHESTRATOR_MODEL=gpt-4-turbo-preview
AGENT_MODEL=gpt-4-turbo-preview
LOG_LEVEL=INFO
MEMORY_PERSISTENCE=true
```

#### 2. Model Selection

**OpenAI Models**:
- `gpt-4-turbo-preview` (recommended for orchestrator)
- `gpt-4` (slower but reliable)
- `gpt-3.5-turbo` (faster, lower cost, less capable)

**Anthropic Models**:
- `claude-3-5-sonnet-20241022` (recommended)
- `claude-3-opus-20240229` (most capable)
- `claude-3-haiku-20240307` (fastest, lowest cost)

### Running Campaigns

#### CLI Method

```bash
poetry run pulsepilot campaign \
  --company "YourCompany" \
  --product "Your product description" \
  --icp "VP Engineering" \
  --industry "SaaS" \
  --budget 50000 \
  --timeline 30
```

#### Python Script Method

```bash
poetry run python examples/run_campaign.py
```

#### Programmatic Method

```python
from pulsepilot.workflows.campaign import CampaignWorkflow
from pulsepilot.core.models import CampaignInput, CompanyBrief, ICPDefinition, CampaignConstraints

campaign_input = CampaignInput(
    company=CompanyBrief(name="...", ...),
    icp=ICPDefinition(title="...", ...),
    constraints=CampaignConstraints(total_budget=50000, ...)
)

workflow = CampaignWorkflow(campaign_input)
results = workflow.run()
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application
COPY src/ ./src/
COPY examples/ ./examples/

# Create memory storage
RUN mkdir -p /app/memory_store

# Environment
ENV PYTHONPATH=/app/src

CMD ["python", "examples/run_campaign.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  pulsepilot:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MEMORY_PERSISTENCE=true
    volumes:
      - ./memory_store:/app/memory_store
      - ./campaigns:/app/campaigns
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t pulsepilot:latest .

# Run container
docker run -e OPENAI_API_KEY=sk-... \
  -v $(pwd)/memory_store:/app/memory_store \
  pulsepilot:latest
```

---

## Cloud Deployment

### AWS Lambda

**Configuration**:
- Runtime: Python 3.10
- Memory: 2048 MB
- Timeout: 15 minutes (max)
- Layers: Required dependencies

**handler.py**:
```python
import json
from pulsepilot.workflows.campaign import CampaignWorkflow
from pulsepilot.core.models import CampaignInput

def lambda_handler(event, context):
    campaign_input = CampaignInput(**json.loads(event['body']))
    workflow = CampaignWorkflow(campaign_input, auto_approve=True)
    results = workflow.run()

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
```

### Google Cloud Run

**cloudbuild.yaml**:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/pulsepilot', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/pulsepilot']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'pulsepilot'
      - '--image=gcr.io/$PROJECT_ID/pulsepilot'
      - '--region=us-central1'
      - '--platform=managed'
```

### Azure Container Instances

```bash
az container create \
  --resource-group pulsepilot-rg \
  --name pulsepilot \
  --image pulsepilot:latest \
  --environment-variables OPENAI_API_KEY=$OPENAI_API_KEY \
  --cpu 2 \
  --memory 4
```

---

## Monitoring

### Logging

**Configure logging**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pulsepilot.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics to Track

- Campaign execution time
- API call count and latency
- Memory usage
- Error rates by agent
- Checkpoint approval times

### Health Checks

```python
from pulsepilot.core.llm import LLMInterface

def health_check():
    try:
        llm = LLMInterface()
        llm.generate("Test", "Respond OK", temperature=0)
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

---

## Scaling

### Horizontal Scaling

Run multiple campaign workflows in parallel:

```python
from concurrent.futures import ThreadPoolExecutor

campaigns = [campaign1, campaign2, campaign3]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(CampaignWorkflow(c).run) for c in campaigns]
    results = [f.result() for f in futures]
```

### Vertical Scaling

For large campaigns:
- Increase LLM temperature for creativity
- Use more powerful models (GPT-4, Claude Opus)
- Allocate more memory for persistence

### Cost Optimization

**Reduce API Costs**:
1. Use cheaper models for non-critical tasks
2. Cache frequent queries
3. Batch operations where possible
4. Set max_tokens limits

**Example**:
```python
# Use Haiku for simple tasks
analytics_llm = LLMInterface(
    provider="anthropic",
    model="claude-3-haiku-20240307"
)

analytics = AnalyticsAgent(memory=memory, llm=analytics_llm)
```

---

## Backup and Recovery

### Memory Backup

```bash
# Backup all campaigns
tar -czf campaigns_backup_$(date +%Y%m%d).tar.gz memory_store/

# Restore
tar -xzf campaigns_backup_20250115.tar.gz
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * tar -czf /backups/pulsepilot_$(date +\%Y\%m\%d).tar.gz /app/memory_store
```

### Campaign Recovery

```python
from pulsepilot.core.memory import SharedMemory

# Load existing campaign
memory = SharedMemory("campaign_abc123")
campaign_state = memory.get_all()

# Resume or analyze
print(f"Phase: {campaign_state['campaign_phase']}")
print(f"Assets: {len(campaign_state['draft_assets'])}")
```

---

## Security

### API Key Management

**Use environment variables**:
```bash
export OPENAI_API_KEY=$(cat /secure/path/openai_key.txt)
```

**Use secrets management**:
- AWS Secrets Manager
- Google Secret Manager
- Azure Key Vault
- HashiCorp Vault

### Data Protection

**Encrypt memory at rest**:
```python
from cryptography.fernet import Fernet

class EncryptedMemory(SharedMemory):
    def __init__(self, campaign_id, encryption_key):
        super().__init__(campaign_id)
        self.cipher = Fernet(encryption_key)

    def _persist(self):
        encrypted = self.cipher.encrypt(json.dumps(self._memory).encode())
        # Save encrypted data
```

### Network Security

- Use HTTPS for all API calls
- Implement rate limiting
- Add request validation
- Use API gateways

---

## Troubleshooting

### Common Issues

**Issue**: "No API key found"
```bash
# Solution
export OPENAI_API_KEY=sk-...
# or
export ANTHROPIC_API_KEY=sk-ant-...
```

**Issue**: JSON parsing errors
```python
# Solution: Increase temperature for more valid JSON
llm = LLMInterface()
# Set temperature to 0.6 or lower for structured outputs
```

**Issue**: Memory not persisting
```bash
# Solution: Check permissions
chmod 755 memory_store/
```

**Issue**: Rate limit errors
```python
# Solution: Add retry logic with exponential backoff
import time
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
def call_llm():
    return llm.generate(...)
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
workflow = CampaignWorkflow(campaign_input)
results = workflow.run()
```

---

## Performance Tuning

### Optimize LLM Calls

```python
# Use lower temperature for deterministic tasks
analytics_response = llm.generate(prompt, temperature=0.3)

# Use higher temperature for creative tasks
content_response = llm.generate(prompt, temperature=0.9)
```

### Parallel Agent Execution

Already optimized in Phase 3 - Agents 2, 3, 4 run in parallel.

### Memory Optimization

```python
# Clear old campaigns
from pathlib import Path
import time

memory_path = Path("memory_store")
cutoff = time.time() - (90 * 24 * 60 * 60)  # 90 days

for file in memory_path.glob("*.json"):
    if file.stat().st_mtime < cutoff:
        file.unlink()
```

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/pulsepilot/issues
- Documentation: See `/docs` folder
- Examples: See `/examples` folder
