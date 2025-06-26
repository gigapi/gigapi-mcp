"""Main MCP server for GigAPI."""

import logging

from fastmcp import FastMCP

from .client import GigAPIClient
from .config import get_config
from .tools import create_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp-gigapi")

MCP_SERVER_NAME = "mcp-gigapi"

# Create the FastMCP instance
gigapi_config = get_config()
client = GigAPIClient(
    host=gigapi_config.host,
    port=gigapi_config.port,
    username=gigapi_config.username,
    password=gigapi_config.password,
    timeout=gigapi_config.timeout,
    verify_ssl=gigapi_config.verify_ssl,
)
mcp = FastMCP(
    name=MCP_SERVER_NAME,
    dependencies=[
        "requests",
        "python-dotenv",
        "pydantic",
    ],
)

# Register all tools
tools = create_tools(client)
for tool in tools:
    mcp.add_tool(tool)

def run(transport: str = None):
    """Run the MCP server with the specified transport (default from config)."""
    if transport is None:
        transport = gigapi_config.transport
    logger.info(f"Starting MCP server with transport: {transport}")
    mcp.run(transport=transport)
