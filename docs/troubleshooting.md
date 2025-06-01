# Troubleshooting Guide

## Overview

This guide provides solutions to common issues encountered when setting up, configuring, and using MCP-Mem0. It covers installation problems, configuration errors, runtime issues, and performance optimization.

## Installation Issues

### Python Version Compatibility

#### Problem: Python Version Mismatch
```
Error: Python 3.12+ required, found Python 3.10
```

**Solutions:**
1. **Install Python 3.12+**
   ```bash
   # Using pyenv (Linux/Mac)
   pyenv install 3.12.0
   pyenv global 3.12.0
   
   # Using python.org installer (Windows)
   # Download from https://www.python.org/downloads/
   ```

2. **Use Virtual Environment with Correct Python**
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

### Dependency Installation Problems

#### Problem: uv Installation Fails
```
Error: Failed to install uv
```

**Solutions:**
1. **Install uv via pip**
   ```bash
   pip install --upgrade pip
   pip install uv
   ```

2. **Alternative Installation Methods**
   ```bash
   # Using pipx
   pipx install uv
   
   # Using conda
   conda install -c conda-forge uv
   ```

#### Problem: Package Conflicts
```
Error: pip's dependency resolver does not currently consider all the packages that are installed
```

**Solutions:**
1. **Use Fresh Virtual Environment**
   ```bash
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   uv pip install -e .
   ```

2. **Force Reinstall**
   ```bash
   uv pip install --force-reinstall -e .
   ```

## Configuration Issues

### Environment Variable Problems

#### Problem: Missing Environment Variables
```
Error: Environment variable PRIMARY_LLM_API_KEY not found
```

**Solutions:**
1. **Check .env File**
   ```bash
   # Verify .env file exists and has correct format
   cat .env
   
   # Ensure no extra spaces or quotes
   PRIMARY_LLM_API_KEY=sk-your-key-here  # Correct
   PRIMARY_LLM_API_KEY = "sk-your-key-here"  # Incorrect
   ```

2. **Set Environment Variables Manually**
   ```bash
   export PRIMARY_LLM_API_KEY=sk-your-key-here
   export SECONDARY_LLM_API_KEY=sk-your-other-key
   ```

3. **Verify Variable Loading**
   ```python
   import os
   print(os.environ.get('PRIMARY_LLM_API_KEY'))
   ```

#### Problem: Invalid Configuration Values
```
Error: Invalid provider name: 'chatgpt'
```

**Supported Values:**
- **LLM Providers**: `openai`, `openrouter`, `ollama`
- **Models**: Check provider documentation for valid model names
- **Transport**: `sse`, `stdio`

### Database Configuration Issues

#### Problem: PostgreSQL Connection Failed
```
Error: A valid PostgreSQL connection string must be provided
```

**Solutions:**
1. **Verify Connection String Format**
   ```bash
   # Correct format
   DATABASE_URL=postgresql://username:password@hostname:port/database
   
   # Example for Supabase
   DATABASE_URL=postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres
   ```

2. **Test Database Connection**
   ```bash
   # Using psql
   psql "postgresql://username:password@hostname:port/database"
   
   # Using Python
   python -c "
   import psycopg2
   conn = psycopg2.connect('your-connection-string')
   print('Connection successful!')
   conn.close()
   "
   ```

3. **Check Database Server Status**
   ```bash
   # For local PostgreSQL
   sudo systemctl status postgresql
   
   # For Docker
   docker ps | grep postgres
   ```

#### Problem: pgvector Extension Missing
```
Error: pgvector extension not found
```

**Solutions:**
1. **Install pgvector Extension**
   ```sql
   -- Connect to your database and run:
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Verify Extension Installation**
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```

3. **For Supabase Users**
   - Go to SQL Editor in Supabase dashboard
   - Run: `CREATE EXTENSION IF NOT EXISTS vector;`

### API Key and Authentication Issues

#### Problem: API Authentication Failed
```
Error: Authentication failed for OpenAI API
```

**Solutions:**
1. **Verify API Key Format**
   ```bash
   # OpenAI keys start with 'sk-proj-' or 'sk-'
   # OpenRouter keys start with 'sk-or-'
   # Check for extra spaces or characters
   ```

2. **Test API Key Manually**
   ```bash
   # Test OpenAI API
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $PRIMARY_LLM_API_KEY"
   
   # Test OpenRouter API
   curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer $SECONDARY_LLM_API_KEY"
   ```

3. **Check API Key Permissions**
   - Ensure API key has required permissions
   - Check usage limits and quotas
   - Verify API key is not expired

#### Problem: Base URL Configuration Issues
```
Error: Invalid base URL format
```

**Solutions:**
1. **Use Correct Base URLs**
   ```env
   # OpenAI
   PRIMARY_LLM_BASE_URL=https://api.openai.com/v1
   
   # OpenRouter
   SECONDARY_LLM_BASE_URL=https://openrouter.ai/api/v1
   
   # Ollama (local)
   PRIMARY_LLM_BASE_URL=http://localhost:11434
   ```

2. **Test URL Accessibility**
   ```bash
   curl -I https://api.openai.com/v1/models
   ```

## Runtime Issues

### Memory Operations Failing

#### Problem: Memory Save Failures
```
Error: Failed to save memory to both providers
```

**Diagnostic Steps:**
1. **Check Provider Health**
   ```python
   # Use the check_provider_health tool
   health_status = await check_provider_health(ctx)
   print(health_status)
   ```

2. **Test Individual Providers**
   ```python
   # Test primary provider
   try:
       result = manager.primary_client.add("test", user_id="test")
       print("Primary OK")
   except Exception as e:
       print(f"Primary failed: {e}")
   
   # Test secondary provider
   try:
       result = manager.secondary_client.add("test", user_id="test")
       print("Secondary OK")
   except Exception as e:
       print(f"Secondary failed: {e}")
   ```

3. **Check Input Validation**
   ```python
   # Ensure input is not empty or invalid
   if not text or not text.strip():
       return "Error: Empty input provided"
   ```

#### Problem: Search Not Finding Results
```
No memories found for query: "user preferences"
```

**Solutions:**
1. **Verify Memories Exist**
   ```python
   all_memories = await get_all_memories(ctx)
   print(f"Total memories: {len(all_memories)}")
   ```

2. **Check Search Query**
   ```python
   # Try broader search terms
   result = await search_memories(ctx, "preferences", limit=10)
   
   # Try exact content search
   result = await search_memories(ctx, "exact memory content")
   ```

3. **Check Embedding Model**
   ```python
   # Ensure embedding model is consistent
   # Both providers should use same EMBEDDING_MODEL_CHOICE
   ```

### Synchronization Issues

#### Problem: Providers Out of Sync
```
Warning: Memory not synchronized between providers
```

**Solutions:**
1. **Manual Synchronization**
   ```python
   sync_result = await sync_providers(ctx)
   print(sync_result)
   ```

2. **Check Provider Connectivity**
   ```python
   health = await check_provider_health(ctx)
   # Fix any unhealthy providers before syncing
   ```

3. **Verify Database Collections**
   ```sql
   -- Check if both collections exist
   SELECT collection_name FROM vector_collections 
   WHERE collection_name IN ('mem0_memories_primary', 'mem0_memories_secondary');
   ```

### Performance Issues

#### Problem: Slow Response Times
```
Warning: Operation took 30+ seconds to complete
```

**Solutions:**
1. **Check Database Performance**
   ```sql
   -- Monitor active connections
   SELECT count(*) FROM pg_stat_activity;
   
   -- Check slow queries
   SELECT query, mean_exec_time 
   FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC;
   ```

2. **Optimize Search Limits**
   ```python
   # Use reasonable limits
   result = await search_memories(ctx, query, limit=5)  # Instead of 50
   ```

3. **Check Network Latency**
   ```bash
   # Test API latency
   curl -w "@curl-format.txt" -s -o /dev/null https://api.openai.com/v1/models
   ```

#### Problem: High Memory Usage
```
Warning: Memory usage exceeding 2GB
```

**Solutions:**
1. **Implement Memory Limits**
   ```python
   # Add memory usage monitoring
   import psutil
   
   def check_memory_usage():
       memory = psutil.virtual_memory()
       if memory.percent > 80:
           logger.warning(f"High memory usage: {memory.percent}%")
   ```

2. **Optimize Duplicate Detection**
   ```python
   # Process in batches for large datasets
   def _memory_exists_batch(self, contents: List[str], user_id: str) -> List[bool]:
       # Process in chunks of 100
       batch_size = 100
       results = []
       for i in range(0, len(contents), batch_size):
           batch = contents[i:i + batch_size]
           batch_results = [self._memory_exists(content, user_id) for content in batch]
           results.extend(batch_results)
       return results
   ```

## Transport-Specific Issues

### SSE Transport Issues

#### Problem: SSE Connection Fails
```
Error: Unable to connect to SSE endpoint
```

**Solutions:**
1. **Check Server Status**
   ```bash
   # Verify server is running
   curl http://localhost:8050/health
   
   # Check server logs
   docker logs container-name
   ```

2. **Verify Port Configuration**
   ```env
   # Ensure port is available
   PORT=8050  # or another available port
   ```

3. **Test with Different Client**
   ```bash
   # Test SSE endpoint directly
   curl -N -H "Accept: text/event-stream" http://localhost:8050/sse
   ```

#### Problem: CORS Issues (Web Clients)
```
Error: CORS policy blocks request
```

**Solutions:**
1. **Configure CORS Headers**
   ```python
   # Add to main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # Configure appropriately for production
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### Stdio Transport Issues

#### Problem: Stdio Communication Fails
```
Error: Broken pipe in stdio transport
```

**Solutions:**
1. **Check Process Permissions**
   ```bash
   # Ensure Python executable is accessible
   which python
   python --version
   ```

2. **Verify Environment Variables**
   ```json
   {
     "mcpServers": {
       "mem0": {
         "command": "/full/path/to/python",
         "args": ["/full/path/to/src/main.py"],
         "env": {
           "TRANSPORT": "stdio"
         }
       }
     }
   }
   ```

3. **Test Manual Execution**
   ```bash
   TRANSPORT=stdio python src/main.py
   # Should show MCP initialization messages
   ```

## Docker-Specific Issues

### Container Build Issues

#### Problem: Docker Build Fails
```
Error: Failed to build Docker image
```

**Solutions:**
1. **Check Dockerfile Syntax**
   ```dockerfile
   # Verify base image is available
   FROM python:3.12-slim
   
   # Check file paths
   COPY src/ /app/src/
   COPY pyproject.toml /app/
   ```

2. **Build with Verbose Output**
   ```bash
   docker build --no-cache --progress=plain -t mcp/mem0 .
   ```

3. **Check Available Disk Space**
   ```bash
   df -h
   docker system prune  # Clean up if needed
   ```

### Container Runtime Issues

#### Problem: Container Exits Immediately
```
Error: Container exited with code 1
```

**Solutions:**
1. **Check Container Logs**
   ```bash
   docker logs container-name
   docker logs --tail 50 container-name
   ```

2. **Debug with Interactive Shell**
   ```bash
   docker run -it --entrypoint /bin/bash mcp/mem0
   # Then manually run the application
   ```

3. **Verify Environment Variables**
   ```bash
   docker run --env-file .env mcp/mem0
   ```

## Logging and Debugging

### Enable Debug Logging

#### Configure Detailed Logging
```python
# Add to main.py or create debug_config.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Set specific logger levels
logging.getLogger('mem0').setLevel(logging.DEBUG)
logging.getLogger('httpx').setLevel(logging.INFO)  # Reduce HTTP noise
```

#### Environment-Based Logging
```env
# Add to .env
LOG_LEVEL=DEBUG
LOG_FILE=logs/mcp-mem0.log
```

### Common Log Messages and Solutions

#### Warning: Memory Not Synchronized
```log
WARNING - Memory not synchronized between providers
```

**Meaning:** One provider failed during memory save operation.

**Solutions:**
- Check provider health
- Verify API keys and connectivity
- Try manual synchronization

#### Error: Duplicate Detection Failed
```log
ERROR - Error checking memory existence: Connection timeout
```

**Meaning:** Database connection issue during duplicate checking.

**Solutions:**
- Check database connectivity
- Verify connection string
- Monitor database performance

#### Info: Memory Already Exists
```log
INFO - Memory already exists, skipping: User prefers coffee...
```

**Meaning:** Duplicate prevention working correctly.

**Action:** This is normal behavior, no action needed.

### Debug Mode Activation

#### Python Debug Mode
```bash
# Run with Python debugger
python -m pdb src/main.py

# Set breakpoints in code
import pdb; pdb.set_trace()
```

#### VS Code Debug Configuration
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug MCP Server",
            "type": "python",
            "request": "launch",
            "program": "src/main.py",
            "env": {
                "TRANSPORT": "stdio",
                "LOG_LEVEL": "DEBUG"
            },
            "console": "integratedTerminal"
        }
    ]
}
```

## Performance Monitoring

### System Resource Monitoring

#### Monitor CPU and Memory Usage
```bash
# Install monitoring tools
pip install psutil

# Create monitoring script
python -c "
import psutil
import time

while True:
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    print(f'CPU: {cpu}%, Memory: {memory.percent}%')
    time.sleep(5)
"
```

#### Database Performance Monitoring
```sql
-- Monitor database connections
SELECT 
    datname,
    numbackends,
    xact_commit,
    xact_rollback
FROM pg_stat_database;

-- Check slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Application Performance Tuning

#### Optimize Similarity Calculations
```python
# Profile similarity calculations
import cProfile

def profile_similarity():
    cProfile.run('manager._calculate_similarity(text1, text2)')

# Use faster algorithms for large datasets
def _calculate_similarity_optimized(self, text1: str, text2: str) -> float:
    """Optimized similarity calculation using sets"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0
```

## Getting Help

### Community Resources

1. **GitHub Issues**: Report bugs and request features
2. **Documentation**: Check docs/ folder for detailed guides
3. **Examples**: Review test files for usage examples

### Diagnostic Information to Include

When reporting issues, include:

1. **System Information**
   ```bash
   python --version
   uv --version
   docker --version  # if using Docker
   ```

2. **Environment Configuration**
   ```bash
   # Sanitized environment variables (remove API keys)
   env | grep -E "(LLM|DATABASE|TRANSPORT)" | sed 's/=.*/=***/'
   ```

3. **Error Logs**
   ```bash
   # Recent error logs
   tail -50 debug.log
   ```

4. **Reproduction Steps**
   - Exact commands used
   - Input data that caused the issue
   - Expected vs actual behavior

### Emergency Recovery

#### Complete System Reset
```bash
# Stop all services
docker stop $(docker ps -q)

# Clean environment
rm -rf .venv
rm -f debug.log

# Fresh installation
python -m venv .venv
source .venv/bin/activate
uv pip install -e .

# Restore configuration
cp .env.backup .env

# Test basic functionality
python -c "from src.utils import get_dual_provider_manager; print('OK')"
```

#### Data Recovery
```sql
-- Backup existing data
pg_dump -h hostname -U username database_name > backup.sql

-- Restore data if needed
psql -h hostname -U username database_name < backup.sql
```

This troubleshooting guide covers the most common issues encountered with MCP-Mem0. For issues not covered here, please check the GitHub repository or create a new issue with detailed information.
