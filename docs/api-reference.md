# API Reference

## Overview

This document provides comprehensive documentation for all MCP tools and methods available in the MCP-Mem0 server.

## MCP Tools

### 1. save_memory

Stores information in long-term memory with dual provider redundancy and duplicate prevention.

**Signature:**
```python
@mcp.tool()
async def save_memory(ctx: Context, text: str) -> str
```

**Parameters:**
- `ctx` (Context): MCP server context containing the dual provider manager
- `text` (str): The content to store in memory, including any relevant details and context

**Returns:**
- `str`: Status message indicating the result of the save operation

**Possible Return Values:**
- `"Memory already exists in database (not duplicated): {text}..."` - When duplicate is detected
- `"Successfully saved memory to both providers: {text}..."` - When saved to both providers
- `"Memory saved to {provider} provider only (sync failed): {text}..."` - When only one provider succeeds
- `"Failed to save memory to both providers: {text}..."` - When both providers fail

**Example Usage:**
```python
# Save a simple memory
result = await save_memory(ctx, "User prefers coffee over tea")

# Save complex information
result = await save_memory(ctx, "User's meeting schedule: Mondays 9am team standup, Wednesdays 2pm client calls")
```

**Duplicate Prevention:**
- Automatically checks for existing similar content
- Uses both exact matching and similarity scoring (90% threshold)
- Prevents redundant storage while maintaining data integrity

---

### 2. get_all_memories

Retrieves all stored memories from both providers with intelligent deduplication.

**Signature:**
```python
@mcp.tool()
async def get_all_memories(ctx: Context) -> str
```

**Parameters:**
- `ctx` (Context): MCP server context containing the dual provider manager

**Returns:**
- `str`: Formatted string containing all unique memories from both providers

**Return Format:**
```
Found {count} memories:

1. {memory_content} [Source: {provider}]
2. {memory_content} [Source: {provider}]
...
```

**Example Usage:**
```python
# Get all stored memories
all_memories = await get_all_memories(ctx)
print(all_memories)
```

**Deduplication Logic:**
- Merges memories from both providers
- Removes exact duplicates based on content
- Preserves source provider information
- Maintains chronological order when possible

---

### 3. search_memories

Finds relevant memories using semantic search across both providers.

**Signature:**
```python
@mcp.tool()
async def search_memories(ctx: Context, query: str, limit: int = 3) -> str
```

**Parameters:**
- `ctx` (Context): MCP server context containing the dual provider manager
- `query` (str): Search query to find relevant memories
- `limit` (int, optional): Maximum number of results to return (default: 3)

**Returns:**
- `str`: Formatted string containing search results with relevance scores

**Return Format:**
```
Found {count} relevant memories:

1. {memory_content} [Source: {provider}]
2. {memory_content} [Source: {provider}]
...
```

**Example Usage:**
```python
# Basic search
results = await search_memories(ctx, "coffee preferences")

# Search with custom limit
results = await search_memories(ctx, "meeting schedule", limit=5)
```

**Search Features:**
- Semantic search using embedding models
- Cross-provider result merging
- Automatic deduplication of results
- Relevance-based ranking

---

### 4. check_provider_health

Monitors the health status of both primary and secondary providers.

**Signature:**
```python
@mcp.tool()
async def check_provider_health(ctx: Context) -> str
```

**Parameters:**
- `ctx` (Context): MCP server context containing the dual provider manager

**Returns:**
- `str`: Detailed health status report for both providers

**Return Format:**
```
Provider Health Status:

Primary Provider: {status}
Secondary Provider: {status}

Overall System Status: {status}
```

**Status Values:**
- `"✅ Healthy"` - Provider is operational
- `"❌ Unhealthy"` - Provider is not responding
- `"⚠️ Degraded"` - Provider has limited functionality

**Example Usage:**
```python
# Check system health
health_status = await check_provider_health(ctx)
print(health_status)
```

**Health Check Logic:**
- Tests connection to each provider
- Verifies API functionality
- Reports overall system status
- Provides actionable error information

---

### 5. sync_providers

Manually triggers synchronization between providers.

**Signature:**
```python
@mcp.tool()
async def sync_providers(ctx: Context) -> str
```

**Parameters:**
- `ctx` (Context): MCP server context containing the dual provider manager

**Returns:**
- `str`: Status report of the synchronization operation

**Return Format:**
```
Synchronization Status:

Primary → Secondary: {status}
Secondary → Primary: {status}

Sync Summary: {summary}
```

**Example Usage:**
```python
# Trigger manual sync
sync_result = await sync_providers(ctx)
print(sync_result)
```

**Synchronization Process:**
- Compares memories between providers
- Identifies missing or inconsistent data
- Attempts to reconcile differences
- Reports sync status and any conflicts

## DualProviderManager Methods

### Core Methods

#### `__init__(primary_config: ProviderConfig, secondary_config: ProviderConfig)`

Initializes the dual provider manager with the specified configurations.

**Parameters:**
- `primary_config` (ProviderConfig): Configuration for the primary provider
- `secondary_config` (ProviderConfig): Configuration for the secondary provider

#### `add(messages: Union[str, List[Dict]], user_id: str, metadata: Optional[Dict] = None) -> Dict[str, Any]`

Adds memory to both providers with synchronization and duplicate prevention.

**Parameters:**
- `messages`: Content to store (string or list of message objects)
- `user_id`: User identifier for memory association
- `metadata`: Optional metadata to associate with the memory

**Returns:**
```python
{
    "primary": Optional[Any],      # Result from primary provider
    "secondary": Optional[Any],    # Result from secondary provider  
    "synchronized": bool,          # Whether both providers succeeded
    "already_exists": bool         # Whether memory was a duplicate
}
```

#### `search(query: str, user_id: str, limit: int = 3) -> List[Dict]`

Searches memories from both providers and merges results.

**Parameters:**
- `query`: Search query string
- `user_id`: User identifier for scoped search
- `limit`: Maximum number of results

**Returns:**
```python
[
    {
        "memory": str,    # Memory content
        "source": str     # Provider source ("primary" or "secondary")
    },
    ...
]
```

#### `get_all(user_id: str) -> List[Dict]`

Retrieves all memories from both providers.

**Parameters:**
- `user_id`: User identifier for scoped retrieval

**Returns:**
```python
[
    {
        "memory": str,    # Memory content
        "source": str     # Provider source ("primary" or "secondary")
    },
    ...
]
```

#### `health_check() -> Dict[str, Any]`

Performs health checks on both providers.

**Returns:**
```python
{
    "primary": {
        "status": str,      # "healthy", "unhealthy", "degraded"
        "details": str      # Additional status information
    },
    "secondary": {
        "status": str,      # "healthy", "unhealthy", "degraded"
        "details": str      # Additional status information
    },
    "overall": str          # Overall system status
}
```

### Helper Methods

#### `_extract_memory_content(messages) -> str`

Extracts searchable content from various message formats.

**Parameters:**
- `messages`: Input in various formats (string, list, dict)

**Returns:**
- `str`: Normalized content string for duplicate checking

**Supported Formats:**
- Simple strings
- Message objects with `content` or `text` fields
- Lists of messages
- Complex nested structures

#### `_memory_exists(memory_content: str, user_id: str) -> bool`

Checks if a memory with similar content already exists.

**Parameters:**
- `memory_content`: Normalized content to check
- `user_id`: User identifier for scoped checking

**Returns:**
- `bool`: True if duplicate found, False otherwise

**Detection Logic:**
- Exact content matching (case-insensitive)
- Similarity analysis using Jaccard algorithm
- 90% similarity threshold for fuzzy matches
- Only checks longer content (>20 characters) for similarity

#### `_calculate_similarity(text1: str, text2: str) -> float`

Calculates similarity between two text strings using Jaccard similarity.

**Parameters:**
- `text1`: First text string
- `text2`: Second text string

**Returns:**
- `float`: Similarity score from 0.0 (no similarity) to 1.0 (identical)

**Algorithm:**
- Token-based Jaccard similarity
- Word-level comparison
- Handles edge cases (empty strings, etc.)

#### `_deduplicate_memories(memories: List[Dict]) -> List[Dict]`

Removes duplicate memories based on content similarity.

**Parameters:**
- `memories`: List of memory objects with content and source

**Returns:**
- `List[Dict]`: Deduplicated list of unique memories

**Deduplication Logic:**
- Content-based deduplication
- Preserves first occurrence
- Maintains source information
- Simple exact matching for performance

## Configuration Classes

### ProviderConfig

Data class for provider configuration.

```python
@dataclass
class ProviderConfig:
    provider_name: str              # Provider type: 'openai', 'openrouter', 'ollama'
    api_key: str                   # API key for authentication
    base_url: Optional[str]        # Custom base URL (optional)
    model_name: str               # LLM model name
    embedding_model: str          # Embedding model name
```

**Example:**
```python
config = ProviderConfig(
    provider_name="openai",
    api_key="sk-...",
    base_url="https://api.openai.com/v1",
    model_name="gpt-4o-mini",
    embedding_model="text-embedding-3-small"
)
```

## Utility Functions

### `get_dual_provider_manager() -> DualProviderManager`

Factory function that creates and configures a DualProviderManager instance.

**Returns:**
- `DualProviderManager`: Configured manager instance

**Configuration Logic:**
1. Checks for dual provider environment variables
2. Falls back to legacy single provider configuration
3. Creates appropriate ProviderConfig objects
4. Initializes and returns DualProviderManager

### `get_mem0_client() -> Optional[Memory]`

Legacy compatibility function that returns a single Mem0 client.

**Returns:**
- `Optional[Memory]`: Primary client from dual provider manager, or None

**Usage:**
- Maintains backward compatibility with existing code
- Returns primary client if available, otherwise secondary
- Should be replaced with `get_dual_provider_manager()` for new code

## Error Handling

### Common Error Patterns

#### Provider Initialization Errors
```python
try:
    manager = get_dual_provider_manager()
except Exception as e:
    logger.error(f"Failed to initialize providers: {e}")
    # Handle gracefully
```

#### Memory Operation Errors
```python
try:
    result = manager.add(messages, user_id)
    if not result["synchronized"]:
        logger.warning("Memory not synchronized between providers")
except Exception as e:
    logger.error(f"Failed to save memory: {e}")
    # Provide user feedback
```

#### Search Errors
```python
try:
    results = manager.search(query, user_id)
except Exception as e:
    logger.error(f"Search failed: {e}")
    return "Search temporarily unavailable"
```

### Error Recovery Strategies

1. **Graceful Degradation**: Continue with available providers
2. **Retry Logic**: Attempt operations multiple times with backoff
3. **Fail-Safe Defaults**: Return safe default values on errors
4. **User Communication**: Provide clear error messages to users
5. **Logging**: Comprehensive error logging for debugging

## Performance Guidelines

### Best Practices

1. **Batch Operations**: Group multiple memory operations when possible
2. **Appropriate Limits**: Use reasonable limits for search operations
3. **Content Size**: Consider memory content size for performance
4. **Error Handling**: Implement proper error handling to prevent cascading failures
5. **Health Monitoring**: Regular health checks to ensure system stability

### Performance Metrics

- **Memory Save Time**: Typically 100-500ms per operation
- **Search Response Time**: Usually 50-200ms for semantic search
- **Health Check Duration**: Generally <100ms per provider
- **Duplicate Detection**: Adds 10-50ms overhead per save operation
