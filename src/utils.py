from mem0 import Memory
import os

# Custom instructions for memory processing (optional – currently unused)
CUSTOM_INSTRUCTIONS = """
Extract the Following Information:  

- Key Information: Identify and save the most important details.
- Context: Capture the surrounding context to understand the memory's relevance.
- Connections: Note any relationships to other topics or memories.
- Importance: Highlight why this information might be valuable in the future.
- Source: Record where this information came from when applicable.
"""

def get_mem0_client():
    # Get LLM provider and configuration from environment variables
    llm_provider = os.getenv('LLM_PROVIDER')
    llm_api_key = os.getenv('LLM_API_KEY')
    llm_model = os.getenv('LLM_CHOICE')
    embedding_model = os.getenv('EMBEDDING_MODEL_CHOICE')
    llm_base_url = os.getenv('LLM_BASE_URL')

    # Initialize config dictionary
    config = {}

    # === LLM CONFIGURATION ===
    if llm_provider in ['openai', 'openrouter']:
        config["llm"] = {
            "provider": llm_provider,
            "config": {
                "model": llm_model,
                "temperature": 0.2,
                "max_tokens": 2000
            }
        }

        # Set base URL if provided (important for openrouter)
        if llm_base_url:
            config["llm"]["config"]["base_url"] = llm_base_url

        # Set API key in environment
        if llm_api_key:
            if llm_provider == "openai":
                os.environ["OPENAI_API_KEY"] = llm_api_key
            elif llm_provider == "openrouter":
                os.environ["OPENROUTER_API_KEY"] = llm_api_key

    elif llm_provider == 'ollama':
        config["llm"] = {
            "provider": "ollama",
            "config": {
                "model": llm_model,
                "temperature": 0.2,
                "max_tokens": 2000
            }
        }

        if llm_base_url:
            config["llm"]["config"]["ollama_base_url"] = llm_base_url

    # === EMBEDDER CONFIGURATION ===
    if llm_provider == 'openai':
        config["embedder"] = {
            "provider": "openai",
            "config": {
                "model": embedding_model or "text-embedding-3-small",
                "embedding_dims": 1536
            }
        }

        if llm_api_key:
            os.environ["OPENAI_API_KEY"] = llm_api_key

    elif llm_provider == 'ollama':
        config["embedder"] = {
            "provider": "ollama",
            "config": {
                "model": embedding_model or "nomic-embed-text",
                "embedding_dims": 768
            }
        }

        if llm_base_url:
            config["embedder"]["config"]["ollama_base_url"] = llm_base_url

    # === VECTOR STORE CONFIGURATION ===
    config["vector_store"] = {
        "provider": "supabase",
        "config": {
            "connection_string": os.environ.get('DATABASE_URL', ''),
            "collection_name": "mem0_memories",
            "embedding_model_dims": 1536 if llm_provider == "openai" else 768
        }
    }

    # (Optional) Add custom prompt for memory extraction
    # config["custom_fact_extraction_prompt"] = CUSTOM_INSTRUCTIONS

    # Create and return the Memory client
    return Memory.from_config(config)
