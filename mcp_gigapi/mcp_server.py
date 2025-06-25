"""Main MCP server for GigAPI."""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp import ServerSession, StdioServerParameters

from .client import GigAPIClient
from .config import get_config
from .tools import create_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GigAPIMCPServer:
    """GigAPI MCP Server."""

    def __init__(self):
        """Initialize the MCP server."""
        self.config = get_config()
        self.client: Optional[GigAPIClient] = None
        self.server: Optional[ServerSession] = None

    async def initialize(self) -> None:
        """Initialize the MCP server and GigAPI client."""
        try:
            # Validate configuration
            self.config.validate()
            
            # Initialize GigAPI client
            self.client = GigAPIClient(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                timeout=self.config.timeout,
                verify_ssl=self.config.verify_ssl,
            )
            
            # Test connection
            await self._test_connection()
            
            # Create MCP server
            self.server = ServerSession("gigapi")
            
            # Register tools
            tools = create_tools(self.client)
            for tool in tools:
                self.server.tool(tool)
            
            logger.info("GigAPI MCP server initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GigAPI MCP server: {e}")
            raise

    async def _test_connection(self) -> None:
        """Test connection to GigAPI server."""
        try:
            # Try to ping the server
            response = self.client.ping()
            logger.info(f"Successfully connected to GigAPI at {self.config.base_url}")
            logger.info(f"Ping response: {response}")
            
        except Exception as e:
            logger.error(f"Failed to connect to GigAPI: {e}")
            raise

    async def run(self) -> None:
        """Run the MCP server."""
        if not self.server:
            raise RuntimeError("Server not initialized")
        
        # Create server parameters based on transport
        if self.config.transport == "stdio":
            params = StdioServerParameters()
        else:
            raise ValueError(f"Unsupported transport: {self.config.transport}")
        
        # Run the server
        async with self.server.run_stdio(params) as stream:
            logger.info("GigAPI MCP server started")
            await stream.wait_closed()


async def main() -> None:
    """Main entry point."""
    try:
        server = GigAPIMCPServer()
        await server.initialize()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1) 