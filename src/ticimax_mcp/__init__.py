from .server import mcp
import os

def main():
    # MCP_TRANSPORT=http olursa Railway/uzak mod, yoksa yerel (stdio) mod
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "http":
        port = int(os.getenv("PORT", 8000))
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        mcp.run()
