# Contributing to PulsePilot

Thank you for your interest in contributing to PulsePilot! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork and Clone**
   ```bash
   git fork https://github.com/yourusername/pulsepilot
   git clone https://github.com/yourusername/pulsepilot
   cd pulsepilot
   ```

2. **Install Development Dependencies**
   ```bash
   poetry install
   ```

3. **Set Up Pre-commit Hooks**
   ```bash
   poetry run pre-commit install
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

Follow the code style:
- Use type hints
- Write docstrings for all public methods
- Keep functions focused and small
- Add tests for new features

### 3. Run Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pulsepilot

# Run specific test file
poetry run pytest tests/test_agents.py
```

### 4. Format Code

```bash
# Format with Black
poetry run black src/ tests/

# Lint with Ruff
poetry run ruff check src/ tests/

# Type check with mypy
poetry run mypy src/
```

### 5. Commit Changes

Use conventional commit messages:

```bash
git commit -m "feat: add new agent capability"
git commit -m "fix: resolve memory persistence issue"
git commit -m "docs: update deployment guide"
git commit -m "test: add analytics agent tests"
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `chore`: Maintenance

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python Style

- Follow PEP 8
- Use type hints everywhere
- Maximum line length: 100 characters
- Use descriptive variable names

**Good**:
```python
def create_messaging_framework(
    self, icp: ICPDefinition, company_context: dict[str, Any]
) -> MessagingFramework:
    """Create comprehensive messaging framework."""
    ...
```

**Bad**:
```python
def create_msg(self, i, c):
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def create_campaign_strategy(self, campaign_input: CampaignInput) -> CampaignStrategy:
    """
    Create overall campaign strategy from inputs.

    Args:
        campaign_input: Campaign specifications including company, ICP, and constraints

    Returns:
        Complete campaign strategy with objectives and key decisions

    Raises:
        ValueError: If campaign_input is invalid
    """
```

### Type Hints

Always use type hints:

```python
from typing import Optional, Any

def process_data(
    data: dict[str, Any],
    options: Optional[list[str]] = None
) -> tuple[bool, str]:
    ...
```

## Testing

### Writing Tests

- Use `pytest`
- Test files: `tests/test_*.py`
- Test functions: `def test_*():`
- Use fixtures for common setup

**Example**:
```python
import pytest
from pulsepilot.core.memory import SharedMemory

@pytest.fixture
def memory():
    return SharedMemory("test_campaign")

def test_memory_write_and_read(memory):
    memory.write("key", "value")
    assert memory.read("key") == "value"
```

### Test Coverage

Aim for >80% coverage:

```bash
poetry run pytest --cov=pulsepilot --cov-report=html
```

View report: `open htmlcov/index.html`

## Adding New Agents

1. **Create Agent Class**
   ```python
   # src/pulsepilot/agents/my_agent.py
   from pulsepilot.agents.base import BaseAgent
   from pulsepilot.core.models import AgentRole

   class MyCustomAgent(BaseAgent):
       def __init__(self, *args, **kwargs):
           super().__init__(AgentRole.CUSTOM, *args, **kwargs)

       def get_system_prompt(self) -> str:
           return """You are..."""

       def execute_task(self, task: AgentTask) -> AgentOutput:
           ...
   ```

2. **Add Tests**
   ```python
   # tests/test_my_agent.py
   def test_my_agent_initialization(memory):
       agent = MyCustomAgent(memory=memory)
       assert agent.role.value == "custom"
   ```

3. **Update Documentation**
   - Add to `docs/AGENTS.md`
   - Update README if significant

4. **Register in `__init__.py`**
   ```python
   from pulsepilot.agents.my_agent import MyCustomAgent

   __all__ = [..., "MyCustomAgent"]
   ```

## Adding New Features

### Feature Checklist

- [ ] Implementation
- [ ] Tests (>80% coverage)
- [ ] Documentation
- [ ] Examples (if user-facing)
- [ ] Type hints
- [ ] Docstrings
- [ ] CHANGELOG update

### Documentation

Update relevant docs:
- `README.md` - Overview and quick start
- `docs/AGENTS.md` - Agent reference
- `docs/DEPLOYMENT.md` - Deployment info
- `docs/QUICKSTART.md` - Quick start examples

## Pull Request Process

1. **Update CHANGELOG.md**
   ```markdown
   ## [Unreleased]
   ### Added
   - New feature X that does Y
   ```

2. **Ensure Tests Pass**
   ```bash
   poetry run pytest
   poetry run black --check src/ tests/
   poetry run ruff check src/ tests/
   ```

3. **Update Documentation**

4. **Create PR with Description**
   - What does this PR do?
   - Why is this change needed?
   - How was it tested?
   - Screenshots (if UI changes)

5. **Respond to Feedback**

## Code Review

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation
- Breaking changes
- Security implications

## Release Process

(For maintainers)

1. **Update Version**
   ```bash
   poetry version minor  # or major/patch
   ```

2. **Update CHANGELOG**
   ```markdown
   ## [0.2.0] - 2025-01-15
   ### Added
   - Feature X
   ### Fixed
   - Bug Y
   ```

3. **Tag Release**
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

4. **Publish to PyPI**
   ```bash
   poetry build
   poetry publish
   ```

## Questions?

- Open an issue for bugs
- Discussions for questions
- PRs for improvements

Thank you for contributing! 🚀
