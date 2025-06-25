#!/usr/bin/env python3
"""Entry point for mcp-gigapi package."""

import asyncio
import sys

from .mcp_server import main as async_main


def main():
    """Synchronous entry point."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
