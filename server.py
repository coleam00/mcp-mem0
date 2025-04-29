import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import uvicorn

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get configuration from environment variables
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8080'))
    transport = os.getenv('TRANSPORT', 'sse')

    # Create FastMCP app
    app = FastMCP()

    # Run the server
    print(f"Starting MCP server on {host}:{port} using {transport} transport")
    uvicorn.run(app, host=host, port=port)

if __name__ == '__main__':
    main()