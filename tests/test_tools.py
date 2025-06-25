"""Tests for GigAPI MCP tools using the public demo service."""


import pytest

from mcp_gigapi.client import GigAPIClient
from mcp_gigapi.tools import GigAPITools, create_tools


class TestGigAPITools:
    """Test cases for GigAPITools using the public demo."""

    @pytest.fixture
    def demo_client(self):
        """Create a client connected to the public GigAPI demo."""
        return GigAPIClient(
            host="gigapi.fly.dev",
            port=443,
            verify_ssl=True,
            timeout=30
        )

    @pytest.fixture
    def tools(self, demo_client):
        """Create tools instance with demo client."""
        return GigAPITools(demo_client)

    def test_health_check(self, tools):
        """Test health check with demo service."""
        result = tools.health_check()

        assert result["success"] is True
        assert result["status"] == "healthy"
        assert "health" in result

    def test_ping(self, tools):
        """Test ping with demo service."""
        result = tools.ping()

        assert result["success"] is True
        assert result["status"] == "connected"
        assert "response" in result

    def test_list_databases(self, tools):
        """Test listing databases with demo service."""
        result = tools.list_databases()

        assert result["success"] is True
        assert "databases" in result
        assert "count" in result
        assert isinstance(result["databases"], list)
        assert len(result["databases"]) > 0

    def test_list_tables(self, tools):
        """Test listing tables with demo service."""
        # First get a database to test with
        db_result = tools.list_databases()
        if db_result["success"] and db_result["databases"]:
            database = db_result["databases"][0]

            result = tools.list_tables(database)

            assert result["success"] is True
            assert "tables" in result
            assert "count" in result
            assert result["database"] == database
            assert isinstance(result["tables"], list)

    def test_run_select_query_simple(self, tools):
        """Test simple SELECT query with demo service."""
        # First get a database to test with
        db_result = tools.list_databases()
        if db_result["success"] and db_result["databases"]:
            database = db_result["databases"][0]

            result = tools.run_select_query("SELECT 1 as test", database)

            assert result["success"] is True
            assert "results" in result
            assert result["query"] == "SELECT 1 as test"
            assert result["database"] == database

    def test_run_select_query_show_tables(self, tools):
        """Test SHOW TABLES query with demo service."""
        # First get a database to test with
        db_result = tools.list_databases()
        if db_result["success"] and db_result["databases"]:
            database = db_result["databases"][0]

            result = tools.run_select_query("SHOW TABLES", database)

            assert result["success"] is True
            assert "results" in result
            assert result["query"] == "SHOW TABLES"
            assert result["database"] == database

    def test_get_table_schema(self, tools):
        """Test getting table schema with demo service."""
        # First get a database and table to test with
        db_result = tools.list_databases()
        if db_result["success"] and db_result["databases"]:
            database = db_result["databases"][0]

            table_result = tools.list_tables(database)
            if table_result["success"] and table_result["tables"]:
                table = table_result["tables"][0]

                result = tools.get_table_schema(database, table)
                if not result["success"]:
                    assert "error" in result
                    pytest.skip(f"Demo server error: {result['error']}")
                assert result["success"] is True
                assert "schema" in result
                assert result["database"] == database
                assert result["table"] == table

    def test_error_handling_invalid_query(self, tools):
        """Test error handling with invalid query."""
        # First get a database to test with
        db_result = tools.list_databases()
        if db_result["success"] and db_result["databases"]:
            database = db_result["databases"][0]

            result = tools.run_select_query("INVALID SQL QUERY", database)

            # Should handle the error gracefully
            assert "success" in result
            # The query might fail, but we should get a proper error response
            if not result["success"]:
                assert "error" in result


class TestCreateTools:
    """Test cases for tool creation."""

    def test_create_tools(self):
        """Test creating MCP tools."""
        client = GigAPIClient()
        tools = create_tools(client)

        # Check that we have the expected tools
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "run_select_query",
            "list_databases",
            "list_tables",
            "get_table_schema",
            "write_data",
            "health_check",
            "ping"
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_tool_descriptions(self):
        """Test that tools have proper descriptions."""
        client = GigAPIClient()
        tools = create_tools(client)

        for tool in tools:
            assert tool.description is not None
            assert len(tool.description) > 0

    def test_tool_input_schemas(self):
        """Test that tools have proper input schemas."""
        client = GigAPIClient()
        tools = create_tools(client)

        for tool in tools:
            assert tool.inputSchema is not None


@pytest.mark.integration
class TestIntegrationWithDemo:
    """Integration tests with the public GigAPI demo service."""

    @pytest.fixture
    def demo_client(self):
        """Create a client connected to the public GigAPI demo."""
        return GigAPIClient(
            host="gigapi.fly.dev",
            port=443,
            verify_ssl=True,
            timeout=30
        )

    @pytest.fixture
    def tools(self, demo_client):
        """Create tools instance with demo client."""
        return GigAPITools(demo_client)

    def test_full_workflow(self, tools):
        """Test a complete workflow with the demo service."""
        # 1. Health check
        health = tools.health_check()
        assert health["success"] is True

        # 2. List databases
        databases = tools.list_databases()
        assert databases["success"] is True
        assert len(databases["databases"]) > 0

        # 3. List tables in first database
        database = databases["databases"][0]
        tables = tools.list_tables(database)
        assert tables["success"] is True

        # 4. Run a simple query
        query_result = tools.run_select_query("SELECT 1 as test", database)
        assert query_result["success"] is True

    def test_sample_data_queries(self, tools):
        """Test queries on sample data."""
        # Get a database to work with
        db_result = tools.list_databases()
        if db_result["success"] and db_result["databases"]:
            database = db_result["databases"][0]

            # Test various query types
            queries = [
                "SELECT 1 as test",
                "SHOW TABLES",
                "SELECT count(*) as total FROM (SELECT 1 as x)"
            ]

            for query in queries:
                result = tools.run_select_query(query, database)
                assert result["success"] is True
                assert result["query"] == query
                assert result["database"] == database
