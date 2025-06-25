#!/usr/bin/env python3
"""Simple test script to verify GigAPI MCP server with public demo."""

import logging

from mcp_gigapi.client import GigAPIClient
from mcp_gigapi.tools import GigAPITools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_demo_connection():
    """Test connection to the public GigAPI demo."""
    print("🔗 Testing connection to GigAPI demo at https://gigapi.fly.dev")

    # Create client
    client = GigAPIClient(
        host="gigapi.fly.dev",
        port=443,
        verify_ssl=True,
        timeout=30
    )

    tools = GigAPITools(client)

    try:
        # Test 1: Health check
        print("\n1️⃣ Testing health check...")
        health = tools.health_check()
        print(f"✅ Health check: {health['status']}")

        # Test 2: Ping
        print("\n2️⃣ Testing ping...")
        ping = tools.ping()
        print(f"✅ Ping: {ping['status']}")

        # Test 3: List databases
        print("\n3️⃣ Testing database listing...")
        databases = tools.list_databases(database="mydb")
        print(f"Raw list_databases response: {databases}")
        print(f"✅ Found {databases['count']} databases: {databases['databases']}")

        if databases['databases']:
            # Use the first database returned
            database = databases['databases'][0]
            print(f"📊 Using first database: {database}")

            # Test 4: List tables
            print(f"\n4️⃣ Testing table listing for database '{database}'...")
            tables = tools.list_tables(database)
            print(f"✅ Found {tables['count']} tables: {tables['tables']}")

            if tables['tables']:
                # Use the first table found
                table = tables['tables'][0]
                print(f"📋 Using first table: {table}")

                # Test 5: Get table schema
                print(f"\n5️⃣ Testing schema retrieval for table '{table}'...")
                tools.get_table_schema(database, table)
                print("✅ Schema retrieved successfully")

                # Test 6: Count query
                print(f"\n6️⃣ Testing count query on table '{table}'...")
                count_result = tools.run_select_query(f"SELECT count(*) as total FROM {table}", database)
                if count_result['success']:
                    print("✅ Count query successful")
                    for result in count_result['results']:
                        print(f"   {result}")
                else:
                    print(f"❌ Count query failed: {count_result.get('error', 'Unknown error')}")

                # Test 7: Simple query with LIMIT
                print(f"\n7️⃣ Testing simple query on table '{table}'...")
                query_result = tools.run_select_query(f"SELECT * FROM {table} LIMIT 3", database)
                if query_result['success']:
                    print(f"✅ Query successful, got {len(query_result['results'])} result sets")
                    for i, result in enumerate(query_result['results']):
                        print(f"   Result {i+1}: {result}")
                else:
                    print(f"❌ Query failed: {query_result.get('error', 'Unknown error')}")
            else:
                print(f"⚠️  No tables found in database '{database}', skipping table tests")
        else:
            print("⚠️  No databases found, skipping database-specific tests")

        print("\n🎉 All tests completed successfully!")
        assert True
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Test failed")
        raise AssertionError(f"Test failed with error: {e}") from e


def test_mcp_tools_creation():
    """Test MCP tools creation."""
    print("\n🔧 Testing MCP tools creation...")

    client = GigAPIClient()
    from mcp_gigapi.tools import create_tools

    tools = create_tools(client)
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

    print(f"✅ Created {len(tools)} tools:")
    for tool_name in tool_names:
        print(f"   - {tool_name}")

    for expected_tool in expected_tools:
        if expected_tool not in tool_names:
            print(f"❌ Missing expected tool: {expected_tool}")
            raise AssertionError(f"Missing expected tool: {expected_tool}")

    print("✅ All expected tools created successfully!")
    assert True


if __name__ == "__main__":
    print("🚀 GigAPI MCP Server Demo Test")
    print("=" * 50)

    # Test MCP tools creation
    tools_ok = test_mcp_tools_creation()

    # Test demo connection
    demo_ok = test_demo_connection()

    print("\n" + "=" * 50)
    if tools_ok and demo_ok:
        print("🎉 All tests passed! GigAPI MCP server is ready to use.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        exit(1)
