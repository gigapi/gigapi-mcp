"""MCP tools for GigAPI operations."""

import json
import logging
from typing import Any, Dict, List, Optional

from mcp import Tool
from pydantic import BaseModel, Field

from .client import GigAPIClient, GigAPIClientError

logger = logging.getLogger(__name__)


class QueryInput(BaseModel):
    """Input model for SQL query execution."""

    sql: str = Field(..., description="The SQL query to execute")
    database: str = Field(..., description="The database to execute the query against")


class DatabaseInput(BaseModel):
    """Input model for database operations."""

    database: str = Field(..., description="The name of the database")


class WriteDataInput(BaseModel):
    """Input model for data writing operations."""

    database: str = Field(..., description="The database to write to")
    data: str = Field(..., description="Data in InfluxDB Line Protocol format")


class GigAPITools:
    """GigAPI MCP tools."""

    def __init__(self, client: GigAPIClient):
        """Initialize GigAPI tools.

        Args:
            client: GigAPI client instance
        """
        self.client = client

    def run_select_query(self, sql: str, database: str) -> Dict[str, Any]:
        """Execute SQL query on GigAPI.

        Args:
            sql: The SQL query to execute
            database: The database to execute the query against

        Returns:
            Query results
        """
        try:
            response = self.client.execute_query(sql, database)
            
            if response.error:
                return {
                    "error": response.error,
                    "success": False
                }
            
            return {
                "results": response.results,
                "success": True,
                "query": sql,
                "database": database
            }
        except GigAPIClientError as e:
            logger.error(f"Query execution failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "query": sql,
                "database": database
            }

    def list_databases(self, database: str = "mydb") -> Dict[str, Any]:
        """List all databases on GigAPI.

        Returns:
            List of databases
        """
        try:
            databases = self.client.list_databases(database)
            return {
                "databases": databases,
                "success": True,
                "count": len(databases)
            }
        except GigAPIClientError as e:
            logger.error(f"Failed to list databases: {e}")
            return {
                "error": str(e),
                "success": False,
                "databases": []
            }

    def list_tables(self, database: str) -> Dict[str, Any]:
        """List all tables in a database.

        Args:
            database: The name of the database

        Returns:
            List of tables
        """
        try:
            tables = self.client.list_tables(database)
            return {
                "tables": tables,
                "success": True,
                "database": database,
                "count": len(tables)
            }
        except GigAPIClientError as e:
            logger.error(f"Failed to list tables: {e}")
            return {
                "error": str(e),
                "success": False,
                "database": database,
                "tables": []
            }

    def get_table_schema(self, database: str, table: str) -> Dict[str, Any]:
        """Get table schema information.

        Args:
            database: The name of the database
            table: The name of the table

        Returns:
            Table schema information
        """
        try:
            schema = self.client.get_table_schema(database, table)
            return {
                "schema": schema,
                "success": True,
                "database": database,
                "table": table
            }
        except GigAPIClientError as e:
            logger.error(f"Failed to get table schema: {e}")
            return {
                "error": str(e),
                "success": False,
                "database": database,
                "table": table
            }

    def write_data(self, database: str, data: str) -> Dict[str, Any]:
        """Write data using InfluxDB Line Protocol.

        Args:
            database: The database to write to
            data: Data in InfluxDB Line Protocol format

        Returns:
            Write operation result
        """
        try:
            result = self.client.write_data(database, data)
            return {
                "result": result,
                "success": True,
                "database": database,
                "data_lines": len(data.strip().split('\n'))
            }
        except GigAPIClientError as e:
            logger.error(f"Failed to write data: {e}")
            return {
                "error": str(e),
                "success": False,
                "database": database
            }

    def health_check(self) -> Dict[str, Any]:
        """Check GigAPI server health.

        Returns:
            Health status
        """
        try:
            health = self.client.health_check()
            return {
                "health": health,
                "success": True,
                "status": "healthy"
            }
        except GigAPIClientError as e:
            logger.error(f"Health check failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "status": "unhealthy"
            }

    def ping(self) -> Dict[str, Any]:
        """Ping GigAPI server.

        Returns:
            Ping response
        """
        try:
            response = self.client.ping()
            return {
                "response": response,
                "success": True,
                "status": "connected"
            }
        except GigAPIClientError as e:
            logger.error(f"Ping failed: {e}")
            return {
                "error": str(e),
                "success": False,
                "status": "disconnected"
            }


def create_tools(client: GigAPIClient) -> List[Tool]:
    """Create MCP tools for GigAPI.

    Args:
        client: GigAPI client instance

    Returns:
        List of MCP tools
    """
    tools_instance = GigAPITools(client)
    
    return [
        Tool(
            name="run_select_query",
            description="Execute SQL queries on your GigAPI cluster. All queries are executed safely.",
            inputSchema=QueryInput.model_json_schema(),
            handler=tools_instance.run_select_query,
        ),
        Tool(
            name="list_databases",
            description="List all databases on your GigAPI cluster.",
            inputSchema=DatabaseInput.model_json_schema(),
            handler=lambda input_data: tools_instance.list_databases(input_data.get("database", "mydb")),
        ),
        Tool(
            name="list_tables",
            description="List all tables in a database.",
            inputSchema=DatabaseInput.model_json_schema(),
            handler=tools_instance.list_tables,
        ),
        Tool(
            name="get_table_schema",
            description="Get schema information for a specific table.",
            inputSchema=DatabaseInput.model_json_schema(),
            handler=lambda input_data: tools_instance.get_table_schema(
                input_data["database"], input_data.get("table", "")
            ),
        ),
        Tool(
            name="write_data",
            description="Write data using InfluxDB Line Protocol format.",
            inputSchema=WriteDataInput.model_json_schema(),
            handler=tools_instance.write_data,
        ),
        Tool(
            name="health_check",
            description="Check the health status of the GigAPI server.",
            inputSchema={},
            handler=lambda _: tools_instance.health_check(),
        ),
        Tool(
            name="ping",
            description="Ping the GigAPI server to check connectivity.",
            inputSchema={},
            handler=lambda _: tools_instance.ping(),
        ),
    ] 