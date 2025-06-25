"""GigAPI HTTP client for MCP server."""

import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GigAPIClientError(Exception):
    """Exception raised for GigAPI client errors."""

    pass


class QueryResponse(BaseModel):
    """Response model for GigAPI query results."""

    results: List[Dict[str, Any]]
    error: Optional[str] = None


class GigAPIClient:
    """HTTP client for GigAPI Timeseries Lake."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 7971,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        """Initialize the GigAPI client.

        Args:
            host: GigAPI server hostname
            port: GigAPI server port
            username: Optional username for authentication
            password: Optional password for authentication
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        # Protocol selection
        if (verify_ssl and port in (443, 8443)) or (port == 443):
            protocol = "https"
        else:
            protocol = "http"
        self.base_url = f"{protocol}://{host}:{port}"
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Setup authentication if provided
        self.auth = None
        if username and password:
            self.auth = (username, password)
        
        # Setup session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "mcp-gigapi/0.1.0"
        })

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request to GigAPI.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            **kwargs: Additional request arguments

        Returns:
            HTTP response

        Raises:
            GigAPIClientError: If request fails
        """
        url = urljoin(self.base_url, endpoint)
        logger.debug(f"Request: {method} {url} params={params} data={data}")
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                auth=self.auth,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs
            )
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            logger.debug(f"Response text: {response.text}")
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise GigAPIClientError(f"Request failed: {e}")

    def health_check(self) -> Dict[str, Any]:
        """Check GigAPI server health.

        Returns:
            Health status response
        """
        response = self._make_request("GET", "/health")
        return response.json()

    def ping(self) -> str:
        """Ping GigAPI server.

        Returns:
            Pong response
        """
        response = self._make_request("GET", "/ping")
        return response.text

    def execute_query(self, query: str, database: str) -> QueryResponse:
        """Execute SQL query on GigAPI.

        Args:
            query: SQL query to execute
            database: Database name

        Returns:
            Query response with results
        """
        data = {"query": query}
        params = {"db": database, "format": "ndjson"}
        
        response = self._make_request("POST", "/query", data=data, params=params)
        try:
            # Handle NDJSON response (one JSON object per line)
            lines = response.text.strip().split('\n')
            results = []
            for line in lines:
                if line.strip():  # Skip empty lines
                    try:
                        result = json.loads(line)
                        results.append(result)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse NDJSON line: {line}, error: {e}")
                        continue
            
            logger.debug(f"/query NDJSON response: {results}")
            return QueryResponse(results=results, error=None)
            
        except Exception as e:
            logger.error(f"Failed to parse /query response: {e}")
            raise GigAPIClientError(f"Failed to parse /query response: {response.text}")

    def write_data(self, database: str, data: str) -> Dict[str, Any]:
        """Write data using InfluxDB Line Protocol.

        Args:
            database: Database name
            data: Data in InfluxDB Line Protocol format

        Returns:
            Write response
        """
        params = {"db": database}
        headers = {"Content-Type": "text/plain"}
        
        response = self._make_request(
            "POST", 
            "/write", 
            data=data, 
            params=params, 
            headers=headers
        )
        return response.json()

    def list_databases(self, database: str = "mydb") -> List[str]:
        """List all databases.

        Returns:
            List of database names
        """
        query = "SHOW DATABASES"
        response = self.execute_query(query, database)
        logger.debug(f"Raw SHOW DATABASES response: {response}")
        if response.error:
            raise GigAPIClientError(f"Failed to list databases: {response.error}")
        
        # Extract database names from NDJSON results
        databases = []
        for result in response.results:
            if "database_name" in result:
                databases.append(result["database_name"])
            elif "name" in result:
                databases.append(result["name"])
            elif "databases" in result:
                databases.extend(result["databases"])
        
        return databases

    def list_tables(self, database: str) -> List[str]:
        """List all tables in a database.

        Args:
            database: Database name

        Returns:
            List of table names
        """
        query = "SHOW TABLES"
        response = self.execute_query(query, database)
        logger.debug(f"Raw SHOW TABLES response: {response}")
        if response.error:
            raise GigAPIClientError(f"Failed to list tables: {response.error}")
        
        # Extract table names from NDJSON results
        tables = []
        for result in response.results:
            if "table_name" in result:
                tables.append(result["table_name"])
            elif "name" in result:
                tables.append(result["name"])
            elif "tables" in result:
                tables.extend(result["tables"])
        
        return tables

    def get_table_schema(self, database: str, table: str) -> List[Dict[str, Any]]:
        """Get table schema information.

        Args:
            database: Database name
            table: Table name

        Returns:
            List of column information
        """
        query = f"DESCRIBE {table}"
        response = self.execute_query(query, database)
        
        if response.error:
            raise GigAPIClientError(f"Failed to get table schema: {response.error}")
        
        return response.results 