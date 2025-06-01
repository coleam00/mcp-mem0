# Development Guide

## Overview

This guide provides information for developers who want to extend, customize, or contribute to the MCP-Mem0 project. It covers the codebase structure, development setup, testing strategies, and guidelines for adding new features.

## Development Environment Setup

### Prerequisites

- Python 3.12+
- Git
- Docker (optional, for containerized development)
- PostgreSQL with pgvector extension
- VS Code or PyCharm (recommended IDEs)

### Local Development Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/mcp-mem0.git
   cd mcp-mem0
   ```

2. **Set Up Python Environment**
   ```bash
   # Using uv (recommended)
   pip install uv
   uv venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   
   # Install dependencies
   uv pip install -e ".[dev]"
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set Up Database**
   ```bash
   # Using Docker for development
   docker run -d \
     --name mem0-postgres \
     -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=mem0_dev \
     -p 5432:5432 \
     pgvector/pgvector:pg16   ```

5. **Start Development Server**
   ```bash
   python src/main.py
   ```

### Development Tools

#### Recommended VS Code Extensions
- Python
- Pylance
- Python Docstring Generator
- GitLens
- Docker
- PostgreSQL

#### Code Quality Tools
```bash
# Install development dependencies
uv pip install black isort mypy pylint

# Format code
black src/
isort src/

# Type checking
mypy src/

# Linting
pylint src/
```

## Codebase Structure

### Project Layout
```
mcp-mem0/
├── src/
│   ├── main.py           # MCP server entry point
│   ├── utils.py          # Dual provider manager and utilities
│   └── __pycache__/      # Python cache files
├── docs/
│   ├── architecture.md   # System architecture documentation
│   ├── api-reference.md  # API documentation
│   ├── configuration.md  # Configuration guide
│   ├── development.md    # This file
│   └── troubleshooting.md # Troubleshooting guide
├── .env.example          # Environment configuration template
├── pyproject.toml        # Project dependencies and metadata
├── Dockerfile           # Container configuration
├── README.md            # Project overview
└── uv.lock              # Dependency lock file
```

### Core Components

#### 1. main.py - MCP Server Implementation

**Key Components:**
- `Mem0Context`: Context dataclass for sharing state
- `mem0_lifespan()`: Server lifecycle management
- MCP tool implementations
- Transport configuration (SSE/Stdio)

**Adding New Tools:**
```python
@mcp.tool()
async def your_new_tool(ctx: Context, param: str) -> str:
    """Your tool description"""
    try:
        dual_manager = ctx.request_context.lifespan_context.dual_manager
        # Your tool logic here
        return "Success message"
    except Exception as e:
        return f"Error: {str(e)}"
```

#### 2. utils.py - Dual Provider Management

**Key Components:**
- `ProviderConfig`: Provider configuration dataclass
- `DualProviderManager`: Core dual provider logic
- Configuration functions
- Helper utilities

**Key Classes:**
```python
@dataclass
class ProviderConfig:
    provider_name: str
    api_key: str
    base_url: Optional[str]
    model_name: str
    embedding_model: str

class DualProviderManager:
    def __init__(self, primary_config, secondary_config)
    def add(self, messages, user_id, metadata=None)
    def search(self, query, user_id, limit=3)
    def get_all(self, user_id)
    def health_check(self)
```

## Development Workflows

### Adding New Features

#### 1. Planning Phase
- Define feature requirements
- Design API interfaces
- Consider backward compatibility
- Plan testing strategy

#### 2. Implementation Phase
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Implement feature
# Edit relevant files in src/

# Add tests
# Create or update tests in tests/

# Update documentation
# Update relevant docs in docs/
```

#### 3. Testing Phase
```bash
# Run unit tests
pytest tests/test_your_feature.py

# Run integration tests
pytest tests/test_integration.py

# Run all tests
pytest

# Check coverage
pytest --cov=src --cov-report=html
```

#### 4. Code Review Phase
- Create pull request
- Address review feedback
- Ensure all tests pass
- Update documentation

### Testing Strategy

#### Unit Tests

Create focused tests for individual functions:

```python
# tests/test_utils.py
import pytest
from src.utils import DualProviderManager, ProviderConfig

def test_extract_memory_content():
    """Test content extraction from various formats"""
    manager = DualProviderManager(mock_config, mock_config)
    
    # Test string input
    result = manager._extract_memory_content("Test content")
    assert result == "Test content"
    
    # Test message list input
    messages = [{"content": "Hello"}, {"content": "World"}]
    result = manager._extract_memory_content(messages)
    assert result == "Hello World"
```

#### Integration Tests

Test complete workflows:

```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_save_and_search_memory():
    """Test complete save and search workflow"""
    # Setup test environment
    ctx = create_test_context()
    
    # Save memory
    save_result = await save_memory(ctx, "Test memory content")
    assert "Successfully saved" in save_result
    
    # Search memory
    search_result = await search_memories(ctx, "test", limit=1)
    assert "Test memory content" in search_result
```

#### Mock Testing

Use mocks for external dependencies:

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_mem0_client():
    """Mock Mem0 client for testing"""
    client = Mock()
    client.add.return_value = {"id": "test-id"}
    client.search.return_value = [{"memory": "test memory"}]
    client.get_all.return_value = [{"memory": "test memory"}]
    return client

@pytest.fixture
def mock_dual_manager(mock_mem0_client):
    """Mock dual provider manager"""
    with patch('src.utils.get_dual_provider_manager') as mock:
        manager = Mock()
        manager.primary_client = mock_mem0_client
        manager.secondary_client = mock_mem0_client
        manager.add.return_value = {
            "primary": {"id": "test-id"},
            "secondary": {"id": "test-id"},
            "synchronized": True,
            "already_exists": False
        }
        mock.return_value = manager
        yield manager
```

### Debugging

#### Logging Configuration
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# In your code
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

#### Debug Mode
```bash
# Run with debug mode
PYTHONPATH=. python -m pdb src/main.py

# Or use debugger in VS Code
# Set breakpoints and press F5
```

#### Common Debug Points
- Provider initialization
- Memory operations
- Database connections
- API calls
- Error handling

## Extending the System

### Adding New LLM Providers

#### 1. Update Provider Configuration
```python
# In utils.py, update _create_mem0_client()
elif config.provider_name == 'your_provider':
    llm_config = {
        "provider": "your_provider",
        "config": {
            "model": config.model_name,
            "api_key": config.api_key,
            "base_url": config.base_url,
            # Provider-specific configuration
        }
    }
```

#### 2. Add Provider Documentation
Update `docs/configuration.md` with new provider details.

#### 3. Add Tests
```python
def test_your_provider_configuration():
    """Test your provider configuration"""
    config = ProviderConfig(
        provider_name="your_provider",
        api_key="test-key",
        model_name="your-model",
        embedding_model="your-embedding"
    )
    # Test configuration logic
```

### Adding New MCP Tools

#### 1. Define Tool Function
```python
@mcp.tool()
async def your_tool_name(
    ctx: Context,
    parameter1: str,
    parameter2: Optional[int] = None
) -> str:
    """
    Tool description that will appear in MCP documentation.
    
    Args:
        ctx: MCP server context
        parameter1: Description of parameter1
        parameter2: Optional parameter with default value
    
    Returns:
        Human-readable result message
    """
    try:
        dual_manager = ctx.request_context.lifespan_context.dual_manager
        
        # Your tool logic here
        result = dual_manager.your_method(parameter1, parameter2)
        
        return f"Success: {result}"
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return f"Error: {str(e)}"
```

#### 2. Add Tool Method to DualProviderManager
```python
def your_method(self, param1: str, param2: Optional[int] = None) -> Any:
    """Implementation of your tool logic"""
    results = {"primary": None, "secondary": None}
    
    try:
        if self.primary_client:
            results["primary"] = self.primary_client.your_operation(param1, param2)
    except Exception as e:
        self.logger.error(f"Primary provider error: {e}")
    
    try:
        if self.secondary_client:
            results["secondary"] = self.secondary_client.your_operation(param1, param2)
    except Exception as e:
        self.logger.error(f"Secondary provider error: {e}")
    
    return results
```

#### 3. Add Tests
```python
@pytest.mark.asyncio
async def test_your_tool_name():
    """Test your new tool"""
    ctx = create_test_context()
    result = await your_tool_name(ctx, "test_param")
    assert "Success" in result
```

#### 4. Update Documentation
Add tool documentation to `docs/api-reference.md`.

### Adding New Vector Stores

#### 1. Update Vector Store Configuration
```python
# In _create_mem0_client(), add new vector store option
if vector_store_type == "your_vector_store":
    vector_store_config = {
        "provider": "your_vector_store",
        "config": {
            "connection_string": os.environ.get('YOUR_VECTOR_STORE_URL'),
            "collection_name": f"mem0_memories_{provider_type}",
            # Your vector store specific config
        }
    }
```

#### 2. Add Configuration Documentation
Update `docs/configuration.md` with setup instructions.

### Custom Similarity Algorithms

#### 1. Implement New Algorithm
```python
def _calculate_custom_similarity(self, text1: str, text2: str) -> float:
    """Custom similarity calculation"""
    # Your algorithm implementation
    return similarity_score
```

#### 2. Update Duplicate Detection
```python
def _memory_exists(self, memory_content: str, user_id: str) -> bool:
    """Enhanced duplicate detection with custom similarity"""
    # Use your custom similarity algorithm
    similarity = self._calculate_custom_similarity(normalized_input, existing_content)
    if similarity > self.similarity_threshold:
        return True
```

## Performance Optimization

### Profiling

#### 1. Memory Profiling
```bash
pip install memory-profiler
python -m memory_profiler src/main.py
```

#### 2. CPU Profiling
```python
import cProfile
import pstats

def profile_function():
    cProfile.run('your_function()', 'profile_output')
    stats = pstats.Stats('profile_output')
    stats.sort_stats('cumulative').print_stats(10)
```

#### 3. Database Query Optimization
```python
# Add query timing
import time

start_time = time.time()
result = client.search(query, user_id=user_id)
query_time = time.time() - start_time
logger.info(f"Query took {query_time:.3f} seconds")
```

### Caching Strategies

#### 1. Memory Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_similarity_calculation(text1: str, text2: str) -> float:
    """Cached similarity calculation"""
    return self._calculate_similarity(text1, text2)
```

#### 2. Redis Caching
```python
import redis

class CachedDualProviderManager(DualProviderManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def search(self, query: str, user_id: str, limit: int = 3):
        cache_key = f"search:{user_id}:{query}:{limit}"
        cached_result = self.redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        result = super().search(query, user_id, limit)
        self.redis_client.setex(cache_key, 300, json.dumps(result))  # 5 min cache
        return result
```

## Contributing Guidelines

### Code Style

#### Python Style Guide
- Follow PEP 8
- Use type hints
- Write docstrings for all public functions
- Use meaningful variable names
- Keep functions focused and small

#### Example Code Style
```python
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def extract_memory_content(
    messages: Union[str, List[Dict[str, Any]]], 
    normalize: bool = True
) -> str:
    """
    Extract and normalize memory content from various message formats.
    
    Args:
        messages: Input messages in various formats
        normalize: Whether to normalize the extracted content
        
    Returns:
        Extracted and optionally normalized content string
        
    Raises:
        ValueError: If messages format is invalid
    """
    if isinstance(messages, str):
        content = messages.strip()
    elif isinstance(messages, list):
        content_parts = []
        for message in messages:
            if isinstance(message, dict) and "content" in message:
                content_parts.append(str(message["content"]).strip())
            else:
                content_parts.append(str(message).strip())
        content = " ".join(content_parts)
    else:
        raise ValueError(f"Unsupported message format: {type(messages)}")
    
    if normalize:
        content = content.lower().strip()
    
    logger.debug(f"Extracted content length: {len(content)}")
    return content
```

### Pull Request Process

#### 1. Before Creating PR
- Ensure all tests pass
- Update relevant documentation
- Follow code style guidelines
- Add appropriate test coverage

#### 2. PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Code comments updated
- [ ] API documentation updated
- [ ] User documentation updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added for new functionality
- [ ] No new warnings introduced
```

#### 3. Review Process
- Code review by maintainers
- Automated testing via CI/CD
- Documentation review
- Final approval and merge

### Release Process

#### 1. Version Bumping
```bash
# Update version in pyproject.toml
# Update CHANGELOG.md
git add .
git commit -m "Bump version to v1.2.0"
git tag v1.2.0
```

#### 2. Documentation Updates
- Update API documentation
- Update configuration guides
- Add migration guides if needed

#### 3. Testing
- Full test suite execution
- Integration testing
- Performance testing
- Security scanning

#### 4. Release Notes
Document:
- New features
- Bug fixes
- Breaking changes
- Migration instructions

## Security Considerations

### Code Security

#### 1. Input Validation
```python
def validate_user_input(user_input: str) -> str:
    """Validate and sanitize user input"""
    if not isinstance(user_input, str):
        raise ValueError("Input must be a string")
    
    if len(user_input) > MAX_INPUT_LENGTH:
        raise ValueError(f"Input too long (max {MAX_INPUT_LENGTH} chars)")
    
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', user_input)
    return sanitized.strip()
```

#### 2. API Key Handling
```python
def mask_api_key(api_key: str) -> str:
    """Mask API key for logging"""
    if len(api_key) < 8:
        return "***"
    return api_key[:4] + "***" + api_key[-4:]

# Never log full API keys
logger.info(f"Using API key: {mask_api_key(api_key)}")
```

#### 3. Error Message Sanitization
```python
def safe_error_message(error: Exception) -> str:
    """Return safe error message without sensitive info"""
    error_str = str(error)
    
    # Remove potential API keys, passwords, etc.
    sanitized = re.sub(r'sk-[a-zA-Z0-9]+', 'sk-***', error_str)
    sanitized = re.sub(r'password[=:]\s*\S+', 'password=***', sanitized, flags=re.IGNORECASE)
    
    return sanitized
```

### Dependency Security

#### 1. Regular Updates
```bash
# Check for security vulnerabilities
pip-audit

# Update dependencies
uv pip upgrade --all

# Review dependency changes
uv pip list --outdated
```

#### 2. Security Scanning
```bash
# Add to CI/CD pipeline
bandit -r src/
safety check
```

This development guide provides a comprehensive foundation for working with the MCP-Mem0 codebase. Regular updates and community contributions help keep the project robust and feature-rich.
