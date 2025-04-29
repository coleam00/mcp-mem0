import os
from dotenv import load_dotenv
import uvicorn
from mcp.server.fastmcp import FastMCP

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get configuration from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '9000'))  # Default to 9000 to match main config
    transport = os.getenv('TRANSPORT', 'sse')
    protocol = os.getenv('PROTOCOL', 'sse')

    mcp_instance = FastMCP(transport=transport, protocol=protocol)

    # Use the sse_app attribute as the ASGI app
    app = mcp_instance.sse_app

    print(f"Starting MCP server on {host}:{port} using {transport} transport and {protocol} protocol")
    uvicorn.run(app, host=host, port=port)

if __name__ == '__main__':
    main()