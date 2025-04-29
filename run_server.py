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

    # Create FastMCP app
    app = FastMCP()

    # Run the server
    uvicorn.run(app, host=host, port=port)

if __name__ == '__main__':
    main()
