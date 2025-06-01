from mem0 import Memory
import os
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import json
import time

# Custom instructions for memory processing
# These aren't being used right now but Mem0 does support adding custom prompting
# for handling memory retrieval and processing.
CUSTOM_INSTRUCTIONS = """
Extract the Following Information:  

- Key Information: Identify and save the most important details.
- Context: Capture the surrounding context to understand the memory's relevance.
- Connections: Note any relationships to other topics or memories.
- Importance: Highlight why this information might be valuable in the future.
- Source: Record where this information came from when applicable.
"""

@dataclass
class ProviderConfig:
    """Configuration for a single provider"""
    provider_name: str
    api_key: str
    base_url: Optional[str]
    model_name: str
    embedding_model: str
    
class DualProviderManager:
    """
    Manages two separate Mem0 providers with perfect synchronization
    """
    
    def __init__(self, primary_config: ProviderConfig, secondary_config: ProviderConfig):
        self.primary_config = primary_config
        self.secondary_config = secondary_config
        self.primary_client = None
        self.secondary_client = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize both clients
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize both primary and secondary Mem0 clients"""
        try:
            self.primary_client = self._create_mem0_client(self.primary_config, "primary")
            self.logger.info("Primary provider initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize primary provider: {e}")
            
        try:
            self.secondary_client = self._create_mem0_client(self.secondary_config, "secondary")
            self.logger.info("Secondary provider initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize secondary provider: {e}")
    
    def _create_mem0_client(self, config: ProviderConfig, provider_type: str) -> Memory:
        """Create a Mem0 client with the given configuration"""
        
        # Configure LLM based on provider
        llm_config = {}
        embedder_config = {}
        
        if config.provider_name in ['openai', 'openrouter']:
            llm_config = {
                "provider": "openai",
                "config": {
                    "model": config.model_name,
                    "temperature": 0.2,
                    "max_tokens": 2000,
                }
            }
            
            embedder_config = {
                "provider": "openai",
                "config": {
                    "model": config.embedding_model,
                    "embedding_dims": 1536
                }
            }
            
            # Set API key in environment
            if config.provider_name == 'openai':
                os.environ[f"OPENAI_API_KEY_{provider_type.upper()}"] = config.api_key
                if not os.environ.get("OPENAI_API_KEY"):
                    os.environ["OPENAI_API_KEY"] = config.api_key
            elif config.provider_name == 'openrouter':
                os.environ[f"OPENROUTER_API_KEY_{provider_type.upper()}"] = config.api_key
                if config.base_url:
                    llm_config["config"]["openai_base_url"] = config.base_url
                    embedder_config["config"]["openai_base_url"] = config.base_url
                    
        elif config.provider_name == 'ollama':
            llm_config = {
                "provider": "ollama",
                "config": {
                    "model": config.model_name,
                    "temperature": 0.2,
                    "max_tokens": 2000,
                }
            }
            
            embedder_config = {
                "provider": "ollama",
                "config": {
                    "model": config.embedding_model,
                    "embedding_dims": 768
                }
            }
            
            if config.base_url:
                llm_config["config"]["ollama_base_url"] = config.base_url
                embedder_config["config"]["ollama_base_url"] = config.base_url
        
        # Configure vector store with provider-specific collection
        vector_store_config = {
            "provider": "supabase",
            "config": {
                "connection_string": os.environ.get('DATABASE_URL', ''),
                "collection_name": f"mem0_memories_{provider_type}",
                "embedding_model_dims": 1536 if config.provider_name in ['openai', 'openrouter'] else 768
            }
        }
          # Create complete configuration
        mem0_config = {
            "llm": llm_config,
            "embedder": embedder_config,
            "vector_store": vector_store_config
        }
        
        return Memory.from_config(mem0_config)
    
    def add(self, messages: Union[str, List[Dict]], user_id: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Add memory to both providers with synchronization and duplicate prevention"""
        results = {"primary": None, "secondary": None, "synchronized": False, "already_exists": False}
        
        # Extract memory content for duplicate checking
        memory_content = self._extract_memory_content(messages)
        
        # Check if memory already exists in either provider
        if self._memory_exists(memory_content, user_id):
            self.logger.info(f"Memory already exists, skipping: {memory_content[:100]}...")
            results["already_exists"] = True
            results["synchronized"] = True  # Consider it synchronized since it already exists
            return results
        
        try:
            # Add to primary provider
            if self.primary_client:
                results["primary"] = self.primary_client.add(messages, user_id=user_id, metadata=metadata)
                self.logger.info("Memory added to primary provider")
        except Exception as e:
            self.logger.error(f"Failed to add memory to primary provider: {e}")
        
        try:
            # Add to secondary provider
            if self.secondary_client:
                results["secondary"] = self.secondary_client.add(messages, user_id=user_id, metadata=metadata)
                self.logger.info("Memory added to secondary provider")
        except Exception as e:
            self.logger.error(f"Failed to add memory to secondary provider: {e}")
        
        # Check synchronization
        results["synchronized"] = bool(results["primary"] and results["secondary"])
        
        if not results["synchronized"]:
            self.logger.warning("Memory not synchronized between providers")
        
        return results
    
    def search(self, query: str, user_id: str, limit: int = 3) -> List[Dict]:
        """Search memories from both providers and merge results"""
        all_results = []
        
        try:
            # Search primary provider
            if self.primary_client:
                primary_results = self.primary_client.search(query, user_id=user_id, limit=limit)
                if isinstance(primary_results, dict) and "results" in primary_results:
                    primary_memories = [{"memory": r["memory"], "source": "primary"} for r in primary_results["results"]]
                else:
                    primary_memories = [{"memory": r, "source": "primary"} for r in primary_results]
                all_results.extend(primary_memories)
        except Exception as e:
            self.logger.error(f"Failed to search primary provider: {e}")
        
        try:
            # Search secondary provider
            if self.secondary_client:
                secondary_results = self.secondary_client.search(query, user_id=user_id, limit=limit)
                if isinstance(secondary_results, dict) and "results" in secondary_results:
                    secondary_memories = [{"memory": r["memory"], "source": "secondary"} for r in secondary_results["results"]]
                else:
                    secondary_memories = [{"memory": r, "source": "secondary"} for r in secondary_results]
                all_results.extend(secondary_memories)
        except Exception as e:
            self.logger.error(f"Failed to search secondary provider: {e}")
        
        # Deduplicate and merge results
        unique_results = self._deduplicate_memories(all_results)
        
        # Return top results based on limit
        return unique_results[:limit]
    
    def get_all(self, user_id: str) -> List[Dict]:
        """Get all memories from both providers"""
        all_memories = []
        
        try:
            if self.primary_client:
                primary_memories = self.primary_client.get_all(user_id=user_id)
                if isinstance(primary_memories, dict) and "results" in primary_memories:
                    primary_data = [{"memory": r["memory"], "source": "primary"} for r in primary_memories["results"]]
                else:
                    primary_data = [{"memory": r, "source": "primary"} for r in primary_memories]
                all_memories.extend(primary_data)
        except Exception as e:
            self.logger.error(f"Failed to get memories from primary provider: {e}")
        
        try:
            if self.secondary_client:
                secondary_memories = self.secondary_client.get_all(user_id=user_id)
                if isinstance(secondary_memories, dict) and "results" in secondary_memories:
                    secondary_data = [{"memory": r["memory"], "source": "secondary"} for r in secondary_memories["results"]]
                else:
                    secondary_data = [{"memory": r, "source": "secondary"} for r in secondary_memories]
                all_memories.extend(secondary_data)
        except Exception as e:
            self.logger.error(f"Failed to get memories from secondary provider: {e}")
        
        return self._deduplicate_memories(all_memories)
    
    def _deduplicate_memories(self, memories: List[Dict]) -> List[Dict]:
        """Remove duplicate memories based on content similarity"""
        unique_memories = []
        seen_contents = set()
        
        for memory_item in memories:
            memory_text = memory_item["memory"]
            # Simple deduplication based on exact content match
            # In a more sophisticated implementation, you could use embedding similarity
            if memory_text not in seen_contents:
                seen_contents.add(memory_text)
                unique_memories.append(memory_item)
        
        return unique_memories
    
    def _extract_memory_content(self, messages) -> str:
        """Extract memory content from messages for duplicate checking"""
        if isinstance(messages, str):
            return messages.strip()
        elif isinstance(messages, list):
            # For list of messages, extract text content
            content_parts = []
            for msg in messages:
                if isinstance(msg, dict):
                    # Handle message objects with role/content structure
                    if "content" in msg:
                        content_parts.append(str(msg["content"]).strip())
                    elif "text" in msg:
                        content_parts.append(str(msg["text"]).strip())
                    else:
                        # Fallback: convert entire dict to string
                        content_parts.append(str(msg).strip())
                else:
                    content_parts.append(str(msg).strip())
            return " ".join(content_parts)
        else:
            # Fallback for other types
            return str(messages).strip()
    
    def _memory_exists(self, memory_content: str, user_id: str) -> bool:
        """Check if a memory with similar content already exists in either provider"""
        try:
            # Get existing memories from both providers
            existing_memories = self.get_all(user_id)
            
            # Normalize the input memory content for comparison
            normalized_input = memory_content.lower().strip()
            
            # Check for exact or very similar matches
            for memory_item in existing_memories:
                existing_content = memory_item["memory"].lower().strip()
                
                # Exact match
                if existing_content == normalized_input:
                    self.logger.info(f"Found exact memory match in {memory_item['source']} provider")
                    return True
                
                # Check for substantial similarity (90% overlap)
                if len(normalized_input) > 20:  # Only for longer memories
                    similarity = self._calculate_similarity(normalized_input, existing_content)
                    if similarity > 0.9:
                        self.logger.info(f"Found similar memory (similarity: {similarity:.2f}) in {memory_item['source']} provider")
                        return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error checking memory existence: {e}")
            # In case of error, allow the memory to be saved (fail safe)
            return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings using Jaccard similarity"""
        try:
            # Simple token-based Jaccard similarity
            words1 = set(text1.split())
            words2 = set(text2.split())
            
            if not words1 and not words2:
                return 1.0
            if not words1 or not words2:
                return 0.0
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def health_check(self) -> Dict[str, bool]:
        """Check health status of both providers"""
        health = {"primary": False, "secondary": False}
        
        try:
            if self.primary_client:
                # Simple health check by attempting to get memories
                self.primary_client.get_all(user_id="health_check", limit=1)
                health["primary"] = True
        except Exception as e:
            self.logger.error(f"Primary provider health check failed: {e}")
        
        try:
            if self.secondary_client:
                self.secondary_client.get_all(user_id="health_check", limit=1)
                health["secondary"] = True
        except Exception as e:
            self.logger.error(f"Secondary provider health check failed: {e}")
        
        return health

def get_dual_provider_manager() -> DualProviderManager:
    """Create and configure dual provider manager"""
    
    # Check if dual provider configuration exists
    has_dual_config = (
        os.getenv('PRIMARY_LLM_PROVIDER') and 
        os.getenv('SECONDARY_LLM_PROVIDER') and
        os.getenv('PRIMARY_LLM_API_KEY') and 
        os.getenv('SECONDARY_LLM_API_KEY')
    )
    
    if has_dual_config:
        # Use new dual provider configuration
        primary_config = ProviderConfig(
            provider_name=os.getenv('PRIMARY_LLM_PROVIDER', 'openai'),
            api_key=os.getenv('PRIMARY_LLM_API_KEY', ''),
            base_url=os.getenv('PRIMARY_LLM_BASE_URL'),
            model_name=os.getenv('LLM_CHOICE', 'gpt-4o-mini'),
            embedding_model=os.getenv('EMBEDDING_MODEL_CHOICE', 'text-embedding-3-small')
        )
        
        secondary_config = ProviderConfig(
            provider_name=os.getenv('SECONDARY_LLM_PROVIDER', 'openai'),
            api_key=os.getenv('SECONDARY_LLM_API_KEY', ''),
            base_url=os.getenv('SECONDARY_LLM_BASE_URL'),
            model_name=os.getenv('LLM_CHOICE', 'gpt-4o-mini'),  # Same model choice
            embedding_model=os.getenv('EMBEDDING_MODEL_CHOICE', 'text-embedding-3-small')  # Same embedding model
        )
    else:
        # Fallback to legacy configuration (duplicate the same provider for both primary and secondary)
        legacy_provider = os.getenv('LLM_PROVIDER', 'openai')
        legacy_api_key = os.getenv('LLM_API_KEY', '')
        legacy_base_url = os.getenv('LLM_BASE_URL')
        
        primary_config = ProviderConfig(
            provider_name=legacy_provider,
            api_key=legacy_api_key,
            base_url=legacy_base_url,
            model_name=os.getenv('LLM_CHOICE', 'gpt-4o-mini'),
            embedding_model=os.getenv('EMBEDDING_MODEL_CHOICE', 'text-embedding-3-small')
        )
        
        # For legacy mode, use the same configuration for both providers
        secondary_config = ProviderConfig(
            provider_name=legacy_provider,
            api_key=legacy_api_key,
            base_url=legacy_base_url,
            model_name=os.getenv('LLM_CHOICE', 'gpt-4o-mini'),
            embedding_model=os.getenv('EMBEDDING_MODEL_CHOICE', 'text-embedding-3-small')
        )
    
    return DualProviderManager(primary_config, secondary_config)

def get_mem0_client():
    """Legacy function - returns primary client from dual provider for backward compatibility"""
    dual_manager = get_dual_provider_manager()
    return dual_manager.primary_client if dual_manager.primary_client else dual_manager.secondary_client