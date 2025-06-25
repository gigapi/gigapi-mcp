"""Configuration management for GigAPI MCP server."""

import os

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class GigAPIConfig:
    """Configuration for GigAPI MCP server."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # GigAPI connection settings
        self.host = os.getenv("GIGAPI_HOST", "localhost")
        self.port = int(os.getenv("GIGAPI_PORT", "7971"))
        self.username = os.getenv("GIGAPI_USERNAME") or os.getenv("GIGAPI_USER")
        self.password = os.getenv("GIGAPI_PASSWORD") or os.getenv("GIGAPI_PASS")

        # HTTP settings
        self.timeout = int(os.getenv("GIGAPI_TIMEOUT", "30"))
        self.verify_ssl = os.getenv("GIGAPI_VERIFY_SSL", "true").lower() == "true"

        # MCP server settings
        self.transport = os.getenv("GIGAPI_MCP_SERVER_TRANSPORT", "stdio")

        # Default database
        self.default_database = os.getenv("GIGAPI_DEFAULT_DATABASE", "mydb")

        # Enable/disable features
        self.enabled = os.getenv("GIGAPI_ENABLED", "true").lower() == "true"

    @property
    def base_url(self) -> str:
        """Get the base URL for GigAPI."""
        protocol = "https" if self.verify_ssl else "http"
        return f"{protocol}://{self.host}:{self.port}"

    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.enabled:
            raise ValueError("GigAPI is disabled in configuration")

        if not self.host:
            raise ValueError("GIGAPI_HOST is required")

        if self.port <= 0 or self.port > 65535:
            raise ValueError("GIGAPI_PORT must be between 1 and 65535")

        if self.timeout <= 0:
            raise ValueError("GIGAPI_TIMEOUT must be positive")

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": "***" if self.password else None,
            "timeout": self.timeout,
            "verify_ssl": self.verify_ssl,
            "transport": self.transport,
            "default_database": self.default_database,
            "enabled": self.enabled,
            "base_url": self.base_url,
        }


def get_config() -> GigAPIConfig:
    """Get GigAPI configuration instance.

    Returns:
        GigAPI configuration
    """
    return GigAPIConfig()
