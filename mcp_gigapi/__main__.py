#!/usr/bin/env python3
"""Entry point for mcp-gigapi package."""

from .config import get_config
from .mcp_server import run


def main():
    config = get_config()
    transport = config.transport
    run(transport=transport)

if __name__ == "__main__":
    main()
