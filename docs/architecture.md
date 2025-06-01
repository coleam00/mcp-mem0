# Architecture Guide

## Overview

MCP-Mem0 implements a sophisticated dual-provider architecture that provides high availability, redundancy, and intelligent memory management for AI agents. This document provides a deep dive into the system's architectural components and design decisions.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client (Claude, Windsurf, etc.)      │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP Protocol
┌─────────────────────▼───────────────────────────────────────┐
│                    MCP Server                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              DualProviderManager                        ││
│  │  ┌─────────────────┐    ┌─────────────────────────────┐ ││
│  │  │ Primary Provider│    │   Secondary Provider        │ ││
│  │  │                 │    │                             │ ││
│  │  │ ┌─────────────┐ │    │ ┌─────────────────────────┐ │ ││
│  │  │ │   Mem0      │ │    │ │        Mem0             │ │ ││
│  │  │ │   Client    │ │    │ │        Client           │ │ ││
│  │  │ └─────────────┘ │    │ └─────────────────────────┘ │ ││
│  │  └─────────────────┘    └─────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Database Layer                               │
│  ┌───────────────────────┐  ┌──────────────────────────────┐│
│  │ mem0_memories_primary │  │  mem0_memories_secondary     ││
│  │     Collection        │  │      Collection              ││
│  └───────────────────────┘  └──────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. DualProviderManager

The `DualProviderManager` is the heart of the system, managing two separate Mem0 instances and coordinating all operations between them.

#### Key Responsibilities:
- **Provider Initialization**: Sets up both primary and secondary Mem0 clients
- **Memory Operations**: Coordinates add, search, and retrieval operations
- **Health Monitoring**: Tracks the status of both providers
- **Duplicate Prevention**: Implements intelligent duplicate detection
- **Result Deduplication**: Merges and deduplicates results from both providers

#### Class Structure:
```python
@dataclass
class ProviderConfig:
    provider_name: str      # 'openai', 'openrouter', 'ollama'
    api_key: str           # API key for the provider
    base_url: Optional[str] # Custom base URL (optional)
    model_name: str        # LLM model name
    embedding_model: str   # Embedding model name

class DualProviderManager:
    primary_client: Optional[Memory]
    secondary_client: Optional[Memory]
    logger: logging.Logger
```

### 2. Memory Operations Flow

#### Adding Memories
```
User Input → Content Extraction → Duplicate Check → Save to Both Providers → Return Status
     ↓              ↓                   ↓                     ↓                ↓
   Text/Msgs   Extract Content    Check Existing     Primary + Secondary   Sync Status
```

#### Searching Memories
```
Search Query → Search Both Providers → Merge Results → Deduplicate → Return Sorted
     ↓               ↓                     ↓             ↓              ↓
   Keywords      Primary + Secondary    Combine Lists   Remove Dupes   Best Matches
```

#### Retrieving All Memories
```
Get Request → Fetch from Both → Merge Collections → Deduplicate → Return All
     ↓             ↓                  ↓               ↓             ↓
   User ID     Primary + Secondary   Combine Data   Remove Dupes   Full List
```

### 3. Duplicate Prevention System

The duplicate prevention system uses a multi-layer approach:

#### Layer 1: Content Extraction
- Handles multiple input formats (strings, message objects, lists)
- Normalizes content for consistent comparison
- Extracts meaningful text from complex structures

#### Layer 2: Exact Matching
- Case-insensitive exact content matching
- Fast O(1) lookups using normalized content
- Immediate duplicate detection for identical content

#### Layer 3: Similarity Analysis
- Jaccard similarity algorithm for fuzzy matching
- 90% threshold for substantial similarity detection
- Token-based comparison for semantic similarity

#### Layer 4: Cross-Provider Checking
- Searches existing memories in both providers
- Prevents duplicates across the entire system
- Maintains consistency across provider boundaries

### 4. Database Architecture

#### Separate Collections
Each provider uses its own vector collection in the database:
- `mem0_memories_primary`: Primary provider memories
- `mem0_memories_secondary`: Secondary provider memories

#### Benefits:
- **Conflict Prevention**: No data conflicts between providers
- **Independent Scaling**: Each collection can be optimized separately
- **Provider Isolation**: Issues with one provider don't affect the other
- **Easy Maintenance**: Clear separation for debugging and maintenance

### 5. Configuration System

#### Dual Provider Configuration
The system supports two configuration modes:

**Mode 1: Dual Provider (Recommended)**
```env
PRIMARY_LLM_PROVIDER=openai
PRIMARY_LLM_API_KEY=sk-...
SECONDARY_LLM_PROVIDER=openrouter
SECONDARY_LLM_API_KEY=sk-...
LLM_CHOICE=gpt-4o-mini              # Same for both
EMBEDDING_MODEL_CHOICE=text-embedding-3-small  # Same for both
```

**Mode 2: Legacy Single Provider**
```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_CHOICE=gpt-4o-mini
EMBEDDING_MODEL_CHOICE=text-embedding-3-small
```

#### Configuration Logic:
1. Check for dual provider variables (`PRIMARY_*`, `SECONDARY_*`)
2. If found, use dual provider mode
3. If not found, fallback to legacy mode (duplicate same provider)
4. Ensure both providers use identical model configurations

## Design Patterns

### 1. Strategy Pattern
The system uses the Strategy pattern for provider management:
- Each provider implements the same interface
- Providers can be swapped without changing the core logic
- Easy to add new provider types

### 2. Template Method Pattern
Memory operations follow a template method pattern:
- Common operation structure for all memory functions
- Specific implementation details handled by individual providers
- Consistent error handling and logging

### 3. Observer Pattern
Health monitoring uses an observer-like pattern:
- Providers report their status
- Manager aggregates and reports overall health
- Enables proactive monitoring and alerting

### 4. Fail-Safe Pattern
All operations implement fail-safe mechanisms:
- If one provider fails, continue with the other
- If duplicate checking fails, still save the memory
- Graceful degradation maintains system availability

## Performance Considerations

### 1. Duplicate Detection Optimization
- Only performs expensive similarity checks on longer content (>20 chars)
- Uses efficient token-based algorithms
- Caches frequently accessed data

### 2. Parallel Operations
- Memory operations are performed in parallel where possible
- Independent error handling prevents cascading failures
- Async-ready architecture for future enhancements

### 3. Memory Efficiency
- Smart deduplication reduces memory usage
- Efficient data structures for similarity calculations
- Minimal overhead for health monitoring

## Security Considerations

### 1. API Key Management
- Separate API keys for each provider
- Environment variable isolation
- No hardcoded credentials

### 2. Data Isolation
- Separate database collections per provider
- Independent access controls
- Provider-specific configurations

### 3. Error Information
- Sanitized error messages
- No sensitive data in logs
- Graceful error handling

## Scalability

### 1. Horizontal Scaling
- Each provider can scale independently
- Database collections can be partitioned
- Load balancing between providers

### 2. Vertical Scaling
- Efficient algorithms scale with data size
- Memory-efficient operations
- Optimized database queries

### 3. Future Enhancements
- Support for additional providers
- Advanced similarity algorithms
- Distributed caching systems

## Monitoring and Observability

### 1. Health Checks
- Real-time provider status monitoring
- Connection health verification
- Performance metrics tracking

### 2. Logging
- Structured logging with appropriate levels
- Operation tracing and debugging
- Error correlation and analysis

### 3. Metrics
- Success/failure rates for operations
- Response times and latency
- Provider availability statistics
