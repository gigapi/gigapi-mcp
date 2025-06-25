"""Tests for GigAPI client."""

import pytest
from unittest.mock import Mock, patch

from mcp_gigapi.client import GigAPIClient, GigAPIClientError, QueryResponse


class TestGigAPIClient:
    """Test cases for GigAPIClient."""

    def test_init_defaults(self):
        """Test client initialization with defaults."""
        client = GigAPIClient()
        assert client.base_url == "http://localhost:7971"
        assert client.timeout == 30
        assert client.verify_ssl is True
        assert client.auth is None

    def test_init_with_auth(self):
        """Test client initialization with authentication."""
        client = GigAPIClient(
            host="test.com",
            port=8080,
            username="user",
            password="pass"
        )
        assert client.base_url == "http://test.com:8080"
        assert client.auth == ("user", "pass")

    def test_init_with_ssl(self):
        """Test client initialization with SSL settings."""
        client = GigAPIClient(
            host="test.com",
            port=8443,
            verify_ssl=False
        )
        assert client.base_url == "http://test.com:8443"
        assert client.verify_ssl is False

    @patch('requests.Session.request')
    def test_health_check(self, mock_request):
        """Test health check method."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_request.return_value = mock_response

        client = GigAPIClient()
        result = client.health_check()

        assert result == {"status": "healthy"}
        mock_request.assert_called_once_with(
            method="GET",
            url="http://localhost:7971/health",
            json=None,
            params=None,
            auth=None,
            timeout=30,
            verify=True
        )

    @patch('requests.Session.request')
    def test_ping(self, mock_request):
        """Test ping method."""
        mock_response = Mock()
        mock_response.text = "pong"
        mock_request.return_value = mock_response

        client = GigAPIClient()
        result = client.ping()

        assert result == "pong"
        mock_request.assert_called_once_with(
            method="GET",
            url="http://localhost:7971/ping",
            json=None,
            params=None,
            auth=None,
            timeout=30,
            verify=True
        )

    @patch('requests.Session.request')
    def test_execute_query(self, mock_request):
        """Test execute query method."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"name": "test"}],
            "error": None
        }
        mock_request.return_value = mock_response

        client = GigAPIClient()
        result = client.execute_query("SELECT * FROM test", "mydb")

        assert isinstance(result, QueryResponse)
        assert result.results == [{"name": "test"}]
        assert result.error is None

        mock_request.assert_called_once_with(
            method="POST",
            url="http://localhost:7971/query",
            json={"query": "SELECT * FROM test"},
            params={"db": "mydb"},
            auth=None,
            timeout=30,
            verify=True
        )

    @patch('requests.Session.request')
    def test_write_data(self, mock_request):
        """Test write data method."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        mock_request.return_value = mock_response

        client = GigAPIClient()
        data = "weather,location=us-midwest temperature=82"
        result = client.write_data("mydb", data)

        assert result == {"status": "success"}

        mock_request.assert_called_once_with(
            method="POST",
            url="http://localhost:7971/write",
            data=data,
            params={"db": "mydb"},
            auth=None,
            timeout=30,
            verify=True,
            headers={"Content-Type": "text/plain"}
        )

    @patch('requests.Session.request')
    def test_request_error(self, mock_request):
        """Test request error handling."""
        mock_request.side_effect = Exception("Connection failed")

        client = GigAPIClient()
        
        with pytest.raises(GigAPIClientError, match="Request failed: Connection failed"):
            client.ping()


class TestQueryResponse:
    """Test cases for QueryResponse model."""

    def test_query_response_creation(self):
        """Test QueryResponse model creation."""
        response = QueryResponse(
            results=[{"name": "test"}],
            error=None
        )
        assert response.results == [{"name": "test"}]
        assert response.error is None

    def test_query_response_with_error(self):
        """Test QueryResponse model with error."""
        response = QueryResponse(
            results=[],
            error="Query failed"
        )
        assert response.results == []
        assert response.error == "Query failed" 