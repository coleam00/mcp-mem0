<h1 align="center">MCP-Mem0: Long-Term Memory for AI Agents</h1>

<p align="center">
  <img src="public/Mem0AndMCP.png" alt="Mem0 and MCP Integration" width="600">
</p>

A template implementation of the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server integrated with [Mem0](https://mem0.ai) for providing AI agents with persistent memory capabilities.

Use this as a reference point to build your MCP servers yourself, or give this as an example to an AI coding assistant and tell it to follow this example for structure and code correctness!

## Overview

This project demonstrates how to build an MCP server that enables AI agents to store, retrieve, and search memories using semantic search. It serves as a practical template for creating your own MCP servers, simply using Mem0 and a practical example.

The implementation follows the best practices laid out by Anthropic for building MCP servers, allowing seamless integration with any MCP-compatible client.

## Features

The server provides comprehensive memory management tools with **dual provider support** for enhanced reliability:

### Core Memory Tools
1. **`save_memory`**: Store information in long-term memory with dual provider redundancy and duplicate prevention
2. **`get_all_memories`**: Retrieve all stored memories from both providers with intelligent deduplication
3. **`search_memories`**: Find relevant memories using semantic search across both providers

### Dual Provider Management
4. **`check_provider_health`**: Monitor the health status of both primary and secondary providers
5. **`sync_providers`**: Manually trigger synchronization between providers

### Key Benefits
- **🔄 Redundancy**: Memories are stored in two separate providers for fault tolerance
- **⚡ Perfect Synchronization**: Both providers use the same model and embedding configurations
- **🛡️ Failover Support**: Automatic fallback when one provider is unavailable
- **🚫 Duplicate Prevention**: Smart detection prevents saving duplicate memories using content similarity
- **🔍 Intelligent Deduplication**: Advanced algorithms merge results from both providers seamlessly
- **⚙️ Conflict Prevention**: Separate vector collections prevent data conflicts
- **📊 Health Monitoring**: Real-time status checking for both providers
- **🔧 Graceful Error Handling**: Robust error handling with fail-safe mechanisms

## Prerequisites

- Python 3.12+
- Supabase or any PostgreSQL database (for vector storage of memories)
- API keys for your chosen LLM provider (OpenAI, OpenRouter, or Ollama)
- Docker if running the MCP server as a container (recommended)

## Installation

### Using uv

1. Install uv if you don't have it:
   ```bash
   pip install uv
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/coleam00/mcp-mem0.git
   cd mcp-mem0
   ```

3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Configure your environment variables in the `.env` file (see Configuration section)

### Using Docker (Recommended)

1. Build the Docker image:
   ```bash
   docker build -t mcp/mem0 --build-arg PORT=8050 .
   ```

2. Create a `.env` file based on `.env.example` and configure your environment variables

## Configuration

### Dual Provider Setup

This server now supports dual provider configuration for enhanced reliability. Both providers use the same model and embedding configurations to ensure consistency.

The following environment variables can be configured in your `.env` file:

| Variable | Description | Example |
|----------|-------------|----------|
| `TRANSPORT` | Transport protocol (sse or stdio) | `sse` |
| `HOST` | Host to bind to when using SSE transport | `0.0.0.0` |
| `PORT` | Port to listen on when using SSE transport | `8050` |
| `PRIMARY_LLM_PROVIDER` | Primary LLM provider (openai, openrouter, or ollama) | `openai` |
| `PRIMARY_LLM_BASE_URL` | Base URL for the primary LLM API | `https://api.openai.com/v1` |
| `PRIMARY_LLM_API_KEY` | API key for the primary LLM provider | `sk-...` |
| `SECONDARY_LLM_PROVIDER` | Secondary LLM provider (openai, openrouter, or ollama) | `openrouter` |
| `SECONDARY_LLM_BASE_URL` | Base URL for the secondary LLM API | `https://openrouter.ai/api/v1` |
| `SECONDARY_LLM_API_KEY` | API key for the secondary LLM provider | `sk-...` |
| `LLM_CHOICE` | LLM model to use (same for both providers) | `gpt-4o-mini` |
| `EMBEDDING_MODEL_CHOICE` | Embedding model to use (same for both providers) | `text-embedding-3-small` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |

### Legacy Single Provider Configuration

For backward compatibility, you can still use the old single provider configuration:

| Variable | Description | Example |
|----------|-------------|----------|
| `LLM_PROVIDER` | LLM provider (openai, openrouter, or ollama) | `openai` |
| `LLM_BASE_URL` | Base URL for the LLM API | `https://api.openai.com/v1` |
| `LLM_API_KEY` | API key for the LLM provider | `sk-...` |

**How Legacy Mode Works:**
- If dual provider variables (`PRIMARY_*` and `SECONDARY_*`) are not configured, the system automatically falls back to legacy mode
- In legacy mode, the same provider configuration is duplicated for both primary and secondary instances
- This ensures backward compatibility with existing installations while still providing the dual provider architecture benefits

## Running the Server

### Using uv

#### SSE Transport

```bash
# Set TRANSPORT=sse in .env then:
uv run src/main.py
```

The MCP server will essentially be run as an API endpoint that you can then connect to with config shown below.

#### Stdio Transport

With stdio, the MCP client iself can spin up the MCP server, so nothing to run at this point.

### Using Docker

#### SSE Transport

```bash
docker run --env-file .env -p:8050:8050 mcp/mem0
```

The MCP server will essentially be run as an API endpoint within the container that you can then connect to with config shown below.

#### Stdio Transport

With stdio, the MCP client iself can spin up the MCP server container, so nothing to run at this point.

## Integration with MCP Clients

### SSE Configuration

Once you have the server running with SSE transport, you can connect to it using this configuration:

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

> **Note for Windsurf users**: Use `serverUrl` instead of `url` in your configuration:
> ```json
> {
>   "mcpServers": {
>     "mem0": {
>       "transport": "sse",
>       "serverUrl": "http://localhost:8050/sse"
>     }
>   }
> }
> ```

> **Note for n8n users**: Use host.docker.internal instead of localhost since n8n has to reach outside of it's own container to the host machine:
> 
> So the full URL in the MCP node would be: http://host.docker.internal:8050/sse

Make sure to update the port if you are using a value other than the default 8050.

### Python with Stdio Configuration

Add this server to your MCP configuration for Claude Desktop, Windsurf, or any other MCP client:

**Dual Provider Configuration:**
```json
{
  "mcpServers": {
    "mem0": {
      "command": "your/path/to/mcp-mem0/.venv/Scripts/python.exe",
      "args": ["your/path/to/mcp-mem0/src/main.py"],
      "env": {
        "TRANSPORT": "stdio",
        "PRIMARY_LLM_PROVIDER": "openai",
        "PRIMARY_LLM_BASE_URL": "https://api.openai.com/v1",
        "PRIMARY_LLM_API_KEY": "YOUR-OPENAI-API-KEY",
        "SECONDARY_LLM_PROVIDER": "openrouter",
        "SECONDARY_LLM_BASE_URL": "https://openrouter.ai/api/v1",
        "SECONDARY_LLM_API_KEY": "YOUR-OPENROUTER-API-KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR-DATABASE-URL"
      }
    }
  }
}
```

**Legacy Single Provider Configuration:**
```json
{
  "mcpServers": {
    "mem0": {
      "command": "your/path/to/mcp-mem0/.venv/Scripts/python.exe",
      "args": ["your/path/to/mcp-mem0/src/main.py"],
      "env": {
        "TRANSPORT": "stdio",
        "LLM_PROVIDER": "openai",
        "LLM_BASE_URL": "https://api.openai.com/v1",
        "LLM_API_KEY": "YOUR-API-KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR-DATABASE-URL"
      }
    }
  }
}
```

### Docker with Stdio Configuration

**Dual Provider Configuration:**
```json
{
  "mcpServers": {
    "mem0": {
      "command": "docker",
      "args": ["run", "--rm", "-i", 
               "-e", "TRANSPORT", 
               "-e", "PRIMARY_LLM_PROVIDER", 
               "-e", "PRIMARY_LLM_BASE_URL", 
               "-e", "PRIMARY_LLM_API_KEY", 
               "-e", "SECONDARY_LLM_PROVIDER", 
               "-e", "SECONDARY_LLM_BASE_URL", 
               "-e", "SECONDARY_LLM_API_KEY", 
               "-e", "LLM_CHOICE", 
               "-e", "EMBEDDING_MODEL_CHOICE", 
               "-e", "DATABASE_URL", 
               "mcp/mem0"],
      "env": {
        "TRANSPORT": "stdio",
        "PRIMARY_LLM_PROVIDER": "openai",
        "PRIMARY_LLM_BASE_URL": "https://api.openai.com/v1",
        "PRIMARY_LLM_API_KEY": "YOUR-OPENAI-API-KEY",
        "SECONDARY_LLM_PROVIDER": "openrouter",
        "SECONDARY_LLM_BASE_URL": "https://openrouter.ai/api/v1",
        "SECONDARY_LLM_API_KEY": "YOUR-OPENROUTER-API-KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR-DATABASE-URL"
      }
    }
  }
}
```

**Legacy Single Provider Configuration:**
```json
{
  "mcpServers": {
    "mem0": {
      "command": "docker",
      "args": ["run", "--rm", "-i", 
               "-e", "TRANSPORT", 
               "-e", "LLM_PROVIDER", 
               "-e", "LLM_BASE_URL", 
               "-e", "LLM_API_KEY", 
               "-e", "LLM_CHOICE", 
               "-e", "EMBEDDING_MODEL_CHOICE", 
               "-e", "DATABASE_URL", 
               "mcp/mem0"],
      "env": {
        "TRANSPORT": "stdio",
        "LLM_PROVIDER": "openai",
        "LLM_BASE_URL": "https://api.openai.com/v1",
        "LLM_API_KEY": "YOUR-API-KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR-DATABASE-URL"
      }
    }
  }
}
```

## Dual Provider Architecture

### How It Works

The dual provider system operates two separate Mem0 instances in parallel:

1. **Primary Provider**: Your main LLM service (e.g., OpenAI)
2. **Secondary Provider**: Your backup LLM service (e.g., OpenRouter, Ollama)

### Key Features

- **Synchronized Operations**: All memory operations are performed on both providers
- **Same Model Configuration**: Both providers use identical `LLM_CHOICE` and `EMBEDDING_MODEL_CHOICE`
- **Separate Vector Collections**: Each provider stores data in separate database collections to prevent conflicts
- **Automatic Deduplication**: Search and retrieval operations merge and deduplicate results from both providers
- **Health Monitoring**: Real-time status checking ensures both providers are operational
- **Graceful Degradation**: If one provider fails, the system continues with the remaining provider

### Benefits

- **High Availability**: System remains functional even if one provider is down
- **Load Distribution**: Reduces load on individual providers
- **Cost Optimization**: Use different pricing tiers or providers based on your needs
- **Provider Diversity**: Reduce dependency on a single service provider
- **Enhanced Reliability**: Double redundancy for critical memory storage

### Duplicate Prevention System

The system includes intelligent duplicate prevention to avoid storing redundant memories:

#### How It Works
- **Content Extraction**: Automatically extracts searchable content from various message formats
- **Exact Matching**: Performs case-insensitive exact content matching
- **Similarity Analysis**: Uses Jaccard similarity algorithm for fuzzy matching (90% threshold)
- **Cross-Provider Checking**: Searches both primary and secondary providers for duplicates
- **Smart Thresholds**: Only performs expensive similarity checks on longer memories (>20 characters)

#### Benefits
- **Storage Efficiency**: Prevents database bloat from duplicate entries
- **Cost Savings**: Reduces unnecessary API calls and storage costs
- **Data Quality**: Maintains clean, non-redundant memory databases
- **Performance**: Optimized checking algorithms minimize processing overhead
- **Fail-Safe Design**: If duplicate checking fails, memory is still saved to prevent data loss

## Documentation

For detailed documentation, please refer to the `docs/` folder:

- **[Architecture Guide](docs/architecture.md)**: Detailed system architecture and design patterns
- **[API Reference](docs/api-reference.md)**: Complete tool and method documentation
- **[Configuration Guide](docs/configuration.md)**: Comprehensive configuration options
- **[Development Guide](docs/development.md)**: How to extend and customize the system
- **[Troubleshooting](docs/troubleshooting.md)**: Common issues and solutions

## Building Your Own Server

This template provides a foundation for building more complex MCP servers. To build your own:

1. Add your own tools by creating methods with the `@mcp.tool()` decorator
2. Create your own lifespan function to add your own dependencies (clients, database connections, etc.)
3. Modify the `utils.py` file for any helper functions you need for your MCP server
4. Feel free to add prompts and resources as well  with `@mcp.resource()` and `@mcp.prompt()`
