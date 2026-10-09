import os
import requests

CLIENT_ID = os.environ["COGNITO_CLIENT_ID"]
CLIENT_SECRET = os.environ["COGNITO_CLIENT_SECRET"]
TOKEN_URL = os.environ["COGNITO_TOKEN_URL"]
SCOPE = os.environ["COGNITO_SCOPE"]
GATEWAY_URL = os.environ["AGENTCORE_GATEWAY_URL"]
MCP_VERSION = "2026-07-28"


def fetch_access_token():
    response = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials", "scope": SCOPE},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def mcp_meta():
    return {
        "io.modelcontextprotocol/protocolVersion": MCP_VERSION,
        "io.modelcontextprotocol/clientInfo": {
            "name": "vacation-planner-gateway-test",
            "version": "1.0.0",
        },
        "io.modelcontextprotocol/clientCapabilities": {},
    }


def list_tools(access_token):
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "MCP-Protocol-Version": MCP_VERSION,
        "Mcp-Method": "tools/list",
    }
    payload = {
        "jsonrpc": "2.0",
        "id": "list-tools-request",
        "method": "tools/list",
        "params": {"_meta": mcp_meta()},
    }
    response = requests.post(GATEWAY_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def search_tools(access_token, query):
    search_name = "x_amz_bedrock_agentcore_search"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {access_token}",
        "MCP-Protocol-Version": MCP_VERSION,
        "Mcp-Method": "tools/call",
        "Mcp-Name": search_name,
    }
    payload = {
        "jsonrpc": "2.0",
        "id": "search-tools-request",
        "method": "tools/call",
        "params": {
            "name": search_name,
            "arguments": {"query": query},
            "_meta": mcp_meta(),
        },
    }
    response = requests.post(GATEWAY_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def call_tool(access_token, tool_name, arguments):
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "MCP-Protocol-Version": MCP_VERSION,
        "Mcp-Method": "tools/call",
        "Mcp-Name": tool_name,
    }
    payload = {
        "jsonrpc": "2.0",
        "id": "call-tool-request",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments,
            "_meta": mcp_meta(),
        },
    }
    response = requests.post(GATEWAY_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    token = fetch_access_token()
    listed = list_tools(token)
    tool_names = [
        tool["name"]
        for tool in listed.get("result", {}).get("tools", [])
        if tool.get("name", "").endswith("___get_travel_packages")
    ]
    if len(tool_names) != 1:
        raise RuntimeError("Expected exactly one travel-package tool")
    result = call_tool(token, tool_names[0], {"city": "Mumbai"})
    print("Travel-package invocation completed")
    print(result)
