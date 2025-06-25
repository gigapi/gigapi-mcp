"""Pytest configuration and fixtures."""

import os
import pytest
from unittest.mock import Mock

from mcp_gigapi.client import GigAPIClient
from mcp_gigapi.tools import GigAPITools


@pytest.fixture(scope="session")
def demo_client():
    """Create a client connected to the public GigAPI demo for integration tests."""
    return GigAPIClient(
        host="gigapi.fly.dev",
        port=443,
        verify_ssl=True,
        timeout=30
    )


@pytest.fixture(scope="session")
def demo_tools(demo_client):
    """Create tools instance with demo client for integration tests."""
    return GigAPITools(demo_client)


@pytest.fixture
def mock_client():
    """Create a mock GigAPI client for unit tests."""
    return Mock(spec=GigAPIClient)


@pytest.fixture
def mock_tools(mock_client):
    """Create tools instance with mock client for unit tests."""
    return GigAPITools(mock_client)


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Set test environment variables
    os.environ["GIGAPI_HOST"] = "test-host"
    os.environ["GIGAPI_PORT"] = "7971"
    os.environ["GIGAPI_TIMEOUT"] = "10"
    os.environ["GIGAPI_VERIFY_SSL"] = "false"
    
    yield
    
    # Clean up environment variables
    for key in ["GIGAPI_HOST", "GIGAPI_PORT", "GIGAPI_TIMEOUT", "GIGAPI_VERIFY_SSL"]:
        if key in os.environ:
            del os.environ[key]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid or "demo" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # Mark unit tests
        elif "test_client" in item.nodeid or "test_tools" in item.nodeid:
            item.add_marker(pytest.mark.unit) 