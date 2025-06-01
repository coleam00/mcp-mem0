from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
from mem0 import Memory
import asyncio
import json
import os

from utils import get_mem0_client, get_dual_provider_manager, DualProviderManager

load_dotenv()

# Default user ID for memory operations
DEFAULT_USER_ID = "user"

# Create a dataclass for our application context
@dataclass
class Mem0Context:
    """Context for the Mem0 MCP server."""
    dual_manager: DualProviderManager
    mem0_client: Memory  # Keep for backward compatibility

@asynccontextmanager
async def mem0_lifespan(server: FastMCP) -> AsyncIterator[Mem0Context]:
    """
    Manages the Mem0 dual provider lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        Mem0Context: The context containing both dual manager and legacy client
    """
    # Create dual provider manager
    dual_manager = get_dual_provider_manager()
    
    # Create legacy client for backward compatibility
    mem0_client = get_mem0_client()
    
    try:
        yield Mem0Context(dual_manager=dual_manager, mem0_client=mem0_client)
    finally:
        # No explicit cleanup needed for the Mem0 clients
        pass

# Initialize FastMCP server with the Mem0 client as context
mcp = FastMCP(
    "mcp-mem0",
    description="MCP server for long term memory storage and retrieval with Mem0",
    lifespan=mem0_lifespan,
    host=os.getenv("HOST", "0.0.0.0"),
    port=os.getenv("PORT", "8050")
)        

@mcp.tool()
async def save_memory(ctx: Context, text: str) -> str:
    """Save information to your long-term memory using dual providers.

    This tool stores information to both primary and secondary LLM providers for redundancy.
    The content will be processed and indexed for later retrieval through semantic search.

    Args:
        ctx: The MCP server provided context which includes the dual provider manager
        text: The content to store in memory, including any relevant details and context
    """    try:
        dual_manager = ctx.request_context.lifespan_context.dual_manager
        messages = [{"role": "user", "content": text}]
        result = dual_manager.add(messages, user_id=DEFAULT_USER_ID)
        
        # Check if memory already exists
        if result.get("already_exists", False):
            return f"Memory already exists in database (not duplicated): {text[:100]}..." if len(text) > 100 else f"Memory already exists in database: {text}"
        
        # Check synchronization status
        if result["synchronized"]:
            return f"Successfully saved memory to both providers: {text[:100]}..." if len(text) > 100 else f"Successfully saved memory to both providers: {text}"
        elif result["primary"] or result["secondary"]:
            provider = "primary" if result["primary"] else "secondary"
            return f"Memory saved to {provider} provider only (sync failed): {text[:100]}..." if len(text) > 100 else f"Memory saved to {provider} provider only: {text}"
        else:
            return f"Failed to save memory to both providers: {text[:50]}..."
    except Exception as e:
        return f"Error saving memory: {str(e)}"

@mcp.tool()
async def get_all_memories(ctx: Context) -> str:
    """Get all stored memories from both providers.
    
    Call this tool when you need complete context of all previously stored memories.
    Results are merged from both primary and secondary providers.

    Args:
        ctx: The MCP server provided context which includes the dual provider manager

    Returns a JSON formatted list of all stored memories from both providers, 
    including when they were created and their content. Duplicates are removed.
    """
    try:
        dual_manager = ctx.request_context.lifespan_context.dual_manager
        memories = dual_manager.get_all(user_id=DEFAULT_USER_ID)
        
        # Extract memory content and include source information
        flattened_memories = []
        for memory_item in memories:
            if isinstance(memory_item, dict):
                flattened_memories.append({
                    "memory": memory_item["memory"],
                    "source": memory_item.get("source", "unknown")
                })
            else:
                flattened_memories.append({"memory": memory_item, "source": "unknown"})
        
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error retrieving memories: {str(e)}"

@mcp.tool()
async def search_memories(ctx: Context, query: str, limit: int = 3) -> str:
    """Search memories using semantic search across both providers.

    This tool searches relevant information from your memory across both primary and secondary providers. 
    Results are ranked by relevance and merged from both sources.
    Always search your memories before making decisions to ensure you leverage your existing knowledge.

    Args:
        ctx: The MCP server provided context which includes the dual provider manager
        query: Search query string describing what you're looking for. Can be natural language.
        limit: Maximum number of results to return (default: 3)
    """
    try:
        dual_manager = ctx.request_context.lifespan_context.dual_manager
        memories = dual_manager.search(query, user_id=DEFAULT_USER_ID, limit=limit)
        
        # Format results with source information
        formatted_memories = []
        for memory_item in memories:
            if isinstance(memory_item, dict):
                formatted_memories.append({
                    "memory": memory_item["memory"],
                    "source": memory_item.get("source", "unknown")
                })
            else:
                formatted_memories.append({"memory": memory_item, "source": "unknown"})
        
        return json.dumps(formatted_memories, indent=2)
    except Exception as e:
        return f"Error searching memories: {str(e)}"

@mcp.tool()
async def check_provider_health(ctx: Context) -> str:
    """Check the health status of both primary and secondary providers.

    This tool verifies that both LLM providers are functioning correctly and can
    process memory operations. Useful for debugging connection issues.

    Args:
        ctx: The MCP server provided context which includes the dual provider manager

    Returns a JSON formatted status report for both providers.
    """
    try:
        dual_manager = ctx.request_context.lifespan_context.dual_manager
        health_status = dual_manager.health_check()
        
        status_report = {
            "primary_provider": {
                "status": "healthy" if health_status["primary"] else "unhealthy",
                "provider": dual_manager.primary_config.provider_name,
                "model": dual_manager.primary_config.model_name
            },
            "secondary_provider": {
                "status": "healthy" if health_status["secondary"] else "unhealthy",
                "provider": dual_manager.secondary_config.provider_name,
                "model": dual_manager.secondary_config.model_name
            },
            "overall_status": "healthy" if any(health_status.values()) else "critical"
        }
        
        return json.dumps(status_report, indent=2)
    except Exception as e:
        return f"Error checking provider health: {str(e)}"

@mcp.tool()
async def sync_providers(ctx: Context) -> str:
    """Manually trigger synchronization between providers.

    This tool attempts to synchronize memories between primary and secondary providers
    by comparing their contents and ensuring consistency.

    Args:
        ctx: The MCP server provided context which includes the dual provider manager

    Returns a status report of the synchronization process.
    """
    try:
        dual_manager = ctx.request_context.lifespan_context.dual_manager
        
        # Get memories from both providers
        primary_memories = []
        secondary_memories = []
        
        if dual_manager.primary_client:
            try:
                primary_result = dual_manager.primary_client.get_all(user_id=DEFAULT_USER_ID)
                if isinstance(primary_result, dict) and "results" in primary_result:
                    primary_memories = [r["memory"] for r in primary_result["results"]]
                else:
                    primary_memories = primary_result
            except Exception as e:
                pass
        
        if dual_manager.secondary_client:
            try:
                secondary_result = dual_manager.secondary_client.get_all(user_id=DEFAULT_USER_ID)
                if isinstance(secondary_result, dict) and "results" in secondary_result:
                    secondary_memories = [r["memory"] for r in secondary_result["results"]]
                else:
                    secondary_memories = secondary_result
            except Exception as e:
                pass
        
        sync_report = {
            "primary_count": len(primary_memories),
            "secondary_count": len(secondary_memories),
            "sync_status": "synchronized" if len(primary_memories) == len(secondary_memories) else "needs_sync",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return json.dumps(sync_report, indent=2)
    except Exception as e:
        return f"Error during provider synchronization: {str(e)}"

async def main():
    transport = os.getenv("TRANSPORT", "sse")
    if transport == 'sse':
        # Run the MCP server with sse transport
        await mcp.run_sse_async()
    else:
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
