# Configuration Guide

## Overview

This guide provides comprehensive information about configuring MCP-Mem0 for optimal performance and reliability. The system supports both dual provider and legacy single provider configurations.

## Configuration Modes

### Dual Provider Mode (Recommended)

Use two separate LLM providers for enhanced reliability and redundancy.

#### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `PRIMARY_LLM_PROVIDER` | Yes | Primary LLM provider | `openai` |
| `PRIMARY_LLM_API_KEY` | Yes | API key for primary provider | `sk-proj-...` |
| `PRIMARY_LLM_BASE_URL` | No | Custom base URL for primary | `https://api.openai.com/v1` |
| `SECONDARY_LLM_PROVIDER` | Yes | Secondary LLM provider | `openrouter` |
| `SECONDARY_LLM_API_KEY` | Yes | API key for secondary provider | `sk-or-...` |
| `SECONDARY_LLM_BASE_URL` | No | Custom base URL for secondary | `https://openrouter.ai/api/v1` |
| `LLM_CHOICE` | Yes | Model name (same for both) | `gpt-4o-mini` |
| `EMBEDDING_MODEL_CHOICE` | Yes | Embedding model (same for both) | `text-embedding-3-small` |
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |

#### Example .env Configuration

```env
# Transport Configuration
TRANSPORT=sse
HOST=0.0.0.0
PORT=8050

# Dual Provider Configuration
PRIMARY_LLM_PROVIDER=openai
PRIMARY_LLM_API_KEY=sk-proj-your-openai-key-here
PRIMARY_LLM_BASE_URL=https://api.openai.com/v1

SECONDARY_LLM_PROVIDER=openrouter
SECONDARY_LLM_API_KEY=sk-or-your-openrouter-key-here
SECONDARY_LLM_BASE_URL=https://openrouter.ai/api/v1

# Shared Model Configuration
LLM_CHOICE=gpt-4o-mini
EMBEDDING_MODEL_CHOICE=text-embedding-3-small

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/mem0_db
```

### Legacy Single Provider Mode

Maintains backward compatibility with existing installations.

#### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `LLM_PROVIDER` | Yes | LLM provider | `openai` |
| `LLM_API_KEY` | Yes | API key | `sk-proj-...` |
| `LLM_BASE_URL` | No | Custom base URL | `https://api.openai.com/v1` |
| `LLM_CHOICE` | Yes | Model name | `gpt-4o-mini` |
| `EMBEDDING_MODEL_CHOICE` | Yes | Embedding model | `text-embedding-3-small` |
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |

#### Example Legacy Configuration

```env
# Transport Configuration
TRANSPORT=sse
HOST=0.0.0.0
PORT=8050

# Legacy Single Provider Configuration
LLM_PROVIDER=openai
LLM_API_KEY=sk-proj-your-openai-key-here
LLM_BASE_URL=https://api.openai.com/v1

# Model Configuration
LLM_CHOICE=gpt-4o-mini
EMBEDDING_MODEL_CHOICE=text-embedding-3-small

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/mem0_db
```

## Supported LLM Providers

### OpenAI

#### Configuration
```env
PRIMARY_LLM_PROVIDER=openai
PRIMARY_LLM_API_KEY=sk-proj-your-key-here
PRIMARY_LLM_BASE_URL=https://api.openai.com/v1
```

#### Supported Models
- **LLM Models**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Embedding Models**: `text-embedding-3-large`, `text-embedding-3-small`, `text-embedding-ada-002`

#### Notes
- Most reliable provider with consistent API
- Best performance for embedding models
- Higher cost compared to alternatives

### OpenRouter

#### Configuration
```env
SECONDARY_LLM_PROVIDER=openrouter
SECONDARY_LLM_API_KEY=sk-or-your-key-here
SECONDARY_LLM_BASE_URL=https://openrouter.ai/api/v1
```

#### Supported Models
- **LLM Models**: `openai/gpt-4o-mini`, `anthropic/claude-3-haiku`, `meta-llama/llama-3.1-8b-instruct`
- **Embedding Models**: `openai/text-embedding-3-small`, `openai/text-embedding-ada-002`

#### Notes
- Cost-effective alternative to direct OpenAI
- Access to multiple model providers
- May have higher latency than direct providers

### Ollama (Local)

#### Configuration
```env
PRIMARY_LLM_PROVIDER=ollama
PRIMARY_LLM_BASE_URL=http://localhost:11434
```

#### Supported Models
- **LLM Models**: `llama3.2`, `qwen2.5`, `mistral`, `codellama`
- **Embedding Models**: `nomic-embed-text`, `all-minilm`, `mxbai-embed-large`

#### Notes
- Free local deployment
- No API costs
- Requires local Ollama installation
- Lower performance on consumer hardware

## Database Configuration

### Supabase (Recommended)

#### Setup Steps
1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Enable the pgvector extension in SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Get your connection string from Project Settings > Database
4. Set the `DATABASE_URL` environment variable

#### Connection String Format
```
postgresql://postgres.xxx:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

#### Configuration
```env
DATABASE_URL=postgresql://postgres.abcdefghijk:your-password@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

### Self-Hosted PostgreSQL

#### Prerequisites
- PostgreSQL 14+ with pgvector extension
- Appropriate database and user permissions

#### Setup Steps
1. Install PostgreSQL and pgvector extension
2. Create database and user:
   ```sql
   CREATE DATABASE mem0_db;
   CREATE USER mem0_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE mem0_db TO mem0_user;
   ```
3. Enable pgvector extension:
   ```sql
   \c mem0_db
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

#### Connection String Format
```
postgresql://username:password@hostname:port/database
```

#### Configuration
```env
DATABASE_URL=postgresql://mem0_user:secure_password@localhost:5432/mem0_db
```

## Transport Configuration

### SSE (Server-Sent Events)

Recommended for production deployments and web-based clients.

#### Configuration
```env
TRANSPORT=sse
HOST=0.0.0.0
PORT=8050
```

#### Benefits
- HTTP-based communication
- Easy to scale and load balance
- Works through firewalls and proxies
- Better for containerized deployments

#### Client Configuration
```json
{
  "mcpServers": {
    "mem0": {
      "transport": "sse",
      "url": "http://localhost:8050/sse"
    }
  }
}
```

### Stdio (Standard Input/Output)

Best for local development and desktop clients.

#### Configuration
```env
TRANSPORT=stdio
```

#### Benefits
- Direct process communication
- Lower latency
- Simpler for desktop applications
- No network configuration required

#### Client Configuration
```json
{
  "mcpServers": {
    "mem0": {
      "command": "python",
      "args": ["src/main.py"],
      "env": {
        "TRANSPORT": "stdio",
        "PRIMARY_LLM_PROVIDER": "openai",
        "PRIMARY_LLM_API_KEY": "sk-...",
        "DATABASE_URL": "postgresql://..."
      }
    }
  }
}
```

## Advanced Configuration

### Performance Tuning

#### Database Optimization
```env
# Connection pooling
DATABASE_URL=postgresql://user:pass@host:port/db?pool_size=20&max_overflow=30

# Connection timeout
DATABASE_URL=postgresql://user:pass@host:port/db?connect_timeout=10
```

#### Memory Management
```env
# For high-memory environments
EMBEDDING_BATCH_SIZE=100
SEARCH_CACHE_SIZE=1000
```

#### Similarity Thresholds
```python
# In utils.py, modify these constants
SIMILARITY_THRESHOLD = 0.9  # 90% similarity for duplicates
MIN_CONTENT_LENGTH = 20     # Minimum length for similarity checking
```

### Security Configuration

#### API Key Security
```env
# Use strong, unique API keys
PRIMARY_LLM_API_KEY=sk-proj-very-long-and-secure-key-here
SECONDARY_LLM_API_KEY=sk-or-different-secure-key-here

# Rotate keys regularly (recommended: monthly)
```

#### Database Security
```env
# Use SSL connections for production
DATABASE_URL=postgresql://user:pass@host:port/db?sslmode=require

# Use connection pooling with limits
DATABASE_URL=postgresql://user:pass@host:port/db?pool_size=10&max_overflow=20
```

#### Network Security
```env
# Bind to specific interface for security
HOST=127.0.0.1  # Local only
# HOST=0.0.0.0  # All interfaces (use with caution)

# Use non-default ports
PORT=8051  # Custom port
```

### Logging Configuration

#### Development Logging
```env
LOG_LEVEL=DEBUG
LOG_FORMAT=detailed
```

#### Production Logging
```env
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/mcp-mem0/server.log
```

### Docker Configuration

#### Environment File
```env
# docker-compose.yml environment
TRANSPORT=sse
HOST=0.0.0.0
PORT=8050
PRIMARY_LLM_PROVIDER=openai
PRIMARY_LLM_API_KEY=${OPENAI_API_KEY}
SECONDARY_LLM_PROVIDER=openrouter  
SECONDARY_LLM_API_KEY=${OPENROUTER_API_KEY}
DATABASE_URL=${DATABASE_URL}
```

#### Volume Mounts
```yaml
# docker-compose.yml
volumes:
  - ./logs:/app/logs
  - ./config:/app/config
```

## Configuration Validation

### Startup Checks

The system performs these validation checks on startup:

1. **Environment Variables**: Verifies required variables are set
2. **API Keys**: Tests connectivity to LLM providers
3. **Database Connection**: Validates PostgreSQL connection
4. **Model Availability**: Confirms specified models are accessible
5. **Permissions**: Checks database read/write permissions

### Health Monitoring

#### Automated Checks
- Provider connectivity every 5 minutes
- Database health every 1 minute
- Memory usage monitoring
- Error rate tracking

#### Manual Checks
Use the `check_provider_health` tool to manually verify system status.

## Troubleshooting Configuration

### Common Issues

#### 1. Database Connection Errors
```
Error: A valid PostgreSQL connection string must be provided
```

**Solutions:**
- Verify `DATABASE_URL` format
- Check database server is running
- Confirm user permissions
- Test connection with `psql`

#### 2. API Key Authentication Errors
```
Error: Authentication failed for provider
```

**Solutions:**
- Verify API key format and validity
- Check API key permissions
- Confirm base URL is correct
- Test with curl or API client

#### 3. Model Not Found Errors
```
Error: Model 'gpt-4o-mini' not found
```

**Solutions:**
- Verify model name spelling
- Check provider model availability
- Confirm API key has model access
- Try alternative model names

#### 4. Vector Extension Errors
```
Error: pgvector extension not found
```

**Solutions:**
- Install pgvector extension
- Check PostgreSQL version compatibility
- Verify extension permissions
- Contact database administrator

### Configuration Validation Script

Create a validation script to test your configuration:

```python
# validate_config.py
import os
from src.utils import get_dual_provider_manager

def validate_configuration():
    """Validate MCP-Mem0 configuration"""
    try:
        # Test dual provider initialization
        manager = get_dual_provider_manager()
        
        # Test provider health
        health = manager.health_check()
        print(f"Primary: {health['primary']['status']}")
        print(f"Secondary: {health['secondary']['status']}")
        
        # Test basic operations
        result = manager.add("Test memory", "test_user")
        print(f"Memory save test: {'✅' if result['synchronized'] else '❌'}")
        
        print("✅ Configuration validation passed!")
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")

if __name__ == "__main__":
    validate_configuration()
```

Run with:
```bash
python validate_config.py
```

## Best Practices

### Configuration Management

1. **Use Environment Files**: Store configuration in `.env` files
2. **Separate Environments**: Different configs for dev/staging/prod
3. **Secret Management**: Use secure secret management systems
4. **Version Control**: Track configuration changes (excluding secrets)
5. **Documentation**: Document all configuration options

### Security Best Practices

1. **Rotate API Keys**: Regular key rotation schedule
2. **Principle of Least Privilege**: Minimal required permissions
3. **Secure Transport**: Use HTTPS/TLS for all connections
4. **Input Validation**: Validate all configuration inputs
5. **Audit Logging**: Log configuration changes

### Performance Optimization

1. **Connection Pooling**: Use database connection pooling
2. **Caching**: Implement appropriate caching strategies
3. **Batch Processing**: Group operations when possible
4. **Resource Limits**: Set appropriate memory and CPU limits
5. **Monitoring**: Implement comprehensive monitoring
