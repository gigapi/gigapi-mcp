# <img src="https://github.com/user-attachments/assets/5b0a4a37-ecab-4ca6-b955-1a2bbccad0b4" />

# GigAPI MCP Server
[![PyPI - Version](https://img.shields.io/pypi/v/mcp-gigapi)](https://pypi.org/project/mcp-gigapi)
[![CodeQL](https://github.com/gigapi/gigapi-mcp/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/gigapi/gigapi-mcp/actions/workflows/github-code-scanning/codeql)

An MCP server for GigAPI Timeseries Lake that provides seamless integration with Claude Desktop and other MCP-compatible clients.

## Features

### GigAPI Tools

* `run_select_query`  
   * Execute SQL queries on your GigAPI cluster.  
   * Input: `sql` (string): The SQL query to execute, `database` (string): The database to execute against.
   * All queries are executed safely through GigAPI's HTTP API with NDJSON format.
* `list_databases`  
   * List all databases on your GigAPI cluster.
   * Input: `database` (string): The database to use for the SHOW DATABASES query (defaults to "mydb").
* `list_tables`  
   * List all tables in a database.  
   * Input: `database` (string): The name of the database.
* `get_table_schema`  
   * Get schema information for a specific table.
   * Input: `database` (string): The name of the database, `table` (string): The name of the table.
* `write_data`  
   * Write data using InfluxDB Line Protocol format.
   * Input: `database` (string): The database to write to, `data` (string): Data in InfluxDB Line Protocol format.
* `health_check`  
   * Check the health status of the GigAPI server.
* `ping`  
   * Ping the GigAPI server to check connectivity.

## Quick Start

### 1. Install the MCP Server

#### Option A: From PyPI (Recommended)
```bash
# The package will be available on PyPI after the first release
# Users can install it directly with uv
uv run --with mcp-gigapi --python 3.11 mcp-gigapi --help
```

#### Option B: From Source
```bash
# Clone the repository
git clone https://github.com/gigapi/mcp-gigapi.git
cd mcp-gigapi

# Install dependencies
uv sync
```

### 2. Configure Claude Desktop

1. Open the Claude Desktop configuration file located at:  
   * On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`  
   * On Windows: `%APPDATA%/Claude/claude_desktop_config.json`
2. Add the following configuration:

#### For the Public Demo (Recommended for Testing)

```json
{
  "mcpServers": {
    "mcp-gigapi": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp-gigapi",
        "--python",
        "3.13",
        "mcp-gigapi"
      ],
      "env": {
        "GIGAPI_HOST": "gigapi.fly.dev",
        "GIGAPI_PORT": "443",
        "GIGAPI_TIMEOUT": "30",
        "GIGAPI_VERIFY_SSL": "true",
        "GIGAPI_DEFAULT_DATABASE": "mydb"
      }
    }
  }
}
```

#### For Local Development

```json
{
  "mcpServers": {
    "mcp-gigapi": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp-gigapi",
        "--python",
        "3.13",
        "mcp-gigapi"
      ],
      "env": {
        "GIGAPI_HOST": "localhost",
        "GIGAPI_PORT": "7971",
        "GIGAPI_TIMEOUT": "30",
        "GIGAPI_VERIFY_SSL": "false",
        "GIGAPI_DEFAULT_DATABASE": "mydb"
      }
    }
  }
}
```

#### With Authentication

```json
{
  "mcpServers": {
    "mcp-gigapi": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp-gigapi",
        "--python",
        "3.13",
        "mcp-gigapi"
      ],
      "env": {
        "GIGAPI_HOST": "your-gigapi-server",
        "GIGAPI_PORT": "7971",
        "GIGAPI_USERNAME": "your_username",
        "GIGAPI_PASSWORD": "your_password",
        "GIGAPI_TIMEOUT": "30",
        "GIGAPI_VERIFY_SSL": "true",
        "GIGAPI_DEFAULT_DATABASE": "your_database"
      }
    }
  }
}
```

3. **Important**: Replace the `uv` command with the absolute path to your `uv` executable:
   ```bash
   which uv  # Find the path
   ```
4. Restart Claude Desktop to apply the changes.

## API Compatibility

This MCP server is designed to work with GigAPI's HTTP API endpoints:

### Query Endpoints
- `POST /query?db={database}&format=ndjson` - Execute SQL queries with NDJSON response format
- All queries return NDJSON (Newline Delimited JSON) format for efficient streaming

### Write Endpoints
- `POST /write?db={database}` - Write data using InfluxDB Line Protocol

### Administrative Endpoints
- `GET /health` - Health check
- `GET /ping` - Simple ping

## Example Usage

### Writing Data
Use InfluxDB Line Protocol format:

```bash
curl -X POST "http://localhost:7971/write?db=mydb" --data-binary @/dev/stdin << EOF
weather,location=us-midwest,season=summer temperature=82
weather,location=us-east,season=summer temperature=80
weather,location=us-west,season=summer temperature=99
EOF
```

### Reading Data
Execute SQL queries via JSON POST with NDJSON format:

```bash
curl -X POST "http://localhost:7971/query?db=mydb&format=ndjson" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT time, temperature FROM weather WHERE time >= epoch_ns('\''2025-04-24T00:00:00'\''::TIMESTAMP)"}'
```

### Show Databases/Tables
```bash
# Show databases
curl -X POST "http://localhost:7971/query?db=mydb&format=ndjson" \
  -H "Content-Type: application/json" \
  -d '{"query": "SHOW DATABASES"}'

# Show tables  
curl -X POST "http://localhost:7971/query?db=mydb&format=ndjson" \
  -H "Content-Type: application/json" \
  -d '{"query": "SHOW TABLES"}'

# Count records
curl -X POST "http://localhost:7971/query?db=mydb&format=ndjson" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT count(*), avg(temperature) FROM weather"}'
```

## Environment Variables

### Required Variables

* `GIGAPI_HOST`: The hostname of your GigAPI server
* `GIGAPI_PORT`: The port number of your GigAPI server (default: 7971)

### Optional Variables

* `GIGAPI_USERNAME` or `GIGAPI_USER`: The username for authentication (if required)
* `GIGAPI_PASSWORD` or `GIGAPI_PASS`: The password for authentication (if required)
* `GIGAPI_TIMEOUT`: Request timeout in seconds (default: 30)
* `GIGAPI_VERIFY_SSL`: Enable/disable SSL certificate verification (default: true)
* `GIGAPI_DEFAULT_DATABASE`: Default database to use for queries (default: mydb)
* `GIGAPI_MCP_SERVER_TRANSPORT`: Sets the transport method for the MCP server (default: stdio)
* `GIGAPI_ENABLED`: Enable/disable GigAPI functionality (default: true)

### Example Configurations

#### For Local Development
```bash
# Required variables
GIGAPI_HOST=localhost
GIGAPI_PORT=7971

# Optional: Override defaults for local development
GIGAPI_VERIFY_SSL=false
GIGAPI_TIMEOUT=60
GIGAPI_DEFAULT_DATABASE=mydb
```

#### For Production with Authentication
```bash
# Required variables
GIGAPI_HOST=your-gigapi-server
GIGAPI_PORT=7971
GIGAPI_USERNAME=your_username
GIGAPI_PASSWORD=your_password

# Optional: Production settings
GIGAPI_VERIFY_SSL=true
GIGAPI_TIMEOUT=30
GIGAPI_DEFAULT_DATABASE=your_database
```

#### For Public Demo
```bash
GIGAPI_HOST=gigapi.fly.dev
GIGAPI_PORT=443
GIGAPI_VERIFY_SSL=true
GIGAPI_DEFAULT_DATABASE=mydb
```

## Data Format

GigAPI uses Hive partitioning with the structure:
```
/data
  /mydb
    /weather
      /date=2025-04-10
        /hour=14
          *.parquet
          metadata.json
```

## Development

### Setup Development Environment

1. Install dependencies:
   ```bash
   uv sync --all-extras --dev
   source .venv/bin/activate
   ```

2. Create a `.env` file in the root of the repository:
   ```bash
   GIGAPI_HOST=localhost
   GIGAPI_PORT=7971
   GIGAPI_USERNAME=your_username
   GIGAPI_PASSWORD=your_password
   GIGAPI_TIMEOUT=30
   GIGAPI_VERIFY_SSL=false
   GIGAPI_DEFAULT_DATABASE=mydb
   ```

3. For testing with the MCP Inspector:
   ```bash
   fastmcp dev mcp_gigapi/mcp_server.py
   ```

### Running Tests

```bash
# Run all tests
uv run pytest -v

# Run only unit tests
uv run pytest -v -m "not integration"

# Run only integration tests
uv run pytest -v -m "integration"

# Run linting
uv run ruff check .

# Test with public demo
python test_demo.py
```

### Testing with Public Demo

The repository includes a test script that validates the MCP server against the public GigAPI demo:

```bash
python test_demo.py
```

This will test:
- ✅ Health check and connectivity
- ✅ Database listing (SHOW DATABASES)
- ✅ Table listing (SHOW TABLES)
- ✅ Data queries (SELECT count(*) FROM table)
- ✅ Sample data retrieval

## PyPI Publishing

This package is automatically published to PyPI on each GitHub release. The publishing process is handled by GitHub Actions workflows:

- **CI Workflow** (`.github/workflows/ci.yml`): Runs tests on pull requests and pushes to main
- **Publish Workflow** (`.github/workflows/publish.yml`): Publishes to PyPI when a release is created

### For Users

Once published, users can install the package directly from PyPI:

```bash
# Install and run the MCP server
uv run --with mcp-gigapi --python 3.11 mcp-gigapi
```

### For Maintainers

To publish a new version:

1. Update the version in `pyproject.toml`
2. Create a GitHub release
3. The workflow will automatically publish to PyPI

See [RELEASING.md](RELEASING.md) for detailed release instructions.

## Troubleshooting

### Common Issues

1. **Connection refused**: Check that GigAPI is running and the host/port are correct
2. **Authentication failed**: Verify username/password are correct
3. **SSL certificate errors**: Set `GIGAPI_VERIFY_SSL=false` for self-signed certificates
4. **No databases found**: Ensure you're using the correct default database (usually "mydb")

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

Apache-2.0 license

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- Issues: [GitHub Issues](https://github.com/gigapi/mcp-gigapi/issues)
- Documentation: [GigAPI Documentation](https://gigapi.com/docs)
