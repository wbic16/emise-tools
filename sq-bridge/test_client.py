#!/usr/bin/env python3
"""test_client.py - end-to-end test of sq_bridge.py over real MCP stdio.

Phase A: bridge in default READ-ONLY mode. Lists tools, opens a channel on
the scratch test.phext, reads, queries, and attempts a write (must refuse).
Phase B: bridge with SQ_BRIDGE_READONLY=0. Writes a scroll to the scratch
copy, reads it back, closes the channel.

Run: .venv/bin/python test_client.py   (env SQ_TEST_PORT optional, 18763)
"""
import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = os.environ.get("SQ_TEST_PORT", "18763")


def server(readonly):
    env = dict(os.environ)
    env.update({
        "SQ_DIR": os.path.join(HERE, "test-data"),
        "SQ_PORT": PORT,
        "SQ_BRIDGE_READONLY": readonly,
    })
    return StdioServerParameters(
        command=os.path.join(HERE, ".venv", "bin", "python"),
        args=[os.path.join(HERE, "sq_bridge.py")],
        env=env,
    )


def show(label, result):
    text = "".join(getattr(c, "text", str(c)) for c in result.content)
    is_err = getattr(result, "is_error", getattr(result, "isError", "?"))
    print(f"--- {label} (isError={is_err})", flush=True)
    print(text, flush=True)


async def phase(readonly, fn):
    async with stdio_client(server(readonly)) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await fn(session)


async def phase_a(session):
    tools = await session.list_tools()
    print("--- tools:", ", ".join(t.name for t in tools.tools))
    show("A sq_status", await session.call_tool("sq_status", {}))
    show("A sq_open_channel(test)", await session.call_tool("sq_open_channel", {"phext": "test"}))
    show("A sq_toc(test)", await session.call_tool("sq_toc", {"phext": "test.phext"}))
    show("A sq_read alpha", await session.call_tool(
        "sq_read", {"phext": "test", "coordinate": "1.1.1/1.1.1/1.1.1"}))
    show("A sq_query range", await session.call_tool(
        "sq_query", {"phext": "test", "from_coordinate": "1.1.1/1.1.1/1.1.1",
                     "to_coordinate": "1.1.1/1.1.1/1.1.2"}))
    show("A sq_write (must refuse)", await session.call_tool(
        "sq_write", {"phext": "test", "coordinate": "1.1.1/1.1.1/1.1.3",
                     "text": "delta scroll: must not land"}))
    show("A sq_read missing phext (must refuse)", await session.call_tool(
        "sq_read", {"phext": "ghost", "coordinate": "1.1.1/1.1.1/1.1.1"}))
    show("A sq_close_channel", await session.call_tool("sq_close_channel", {}))


async def phase_b(session):
    show("B sq_open_channel(test)", await session.call_tool("sq_open_channel", {"phext": "test"}))
    show("B sq_write delta", await session.call_tool(
        "sq_write", {"phext": "test", "coordinate": "1.1.1/1.1.1/1.1.3",
                     "text": "delta scroll: written through the bridge"}))
    show("B sq_read delta back", await session.call_tool(
        "sq_read", {"phext": "test", "coordinate": "1.1.1/1.1.1/1.1.3"}))
    show("B sq_write bad coord (must refuse)", await session.call_tool(
        "sq_write", {"phext": "test", "coordinate": "0.0.0/1.1.1/1.1.1", "text": "nope"}))
    show("B sq_close_channel", await session.call_tool("sq_close_channel", {}))
    show("B sq_status after close", await session.call_tool("sq_status", {}))


async def main():
    print("=== Phase A: SQ_BRIDGE_READONLY=1 (default) ===")
    await phase("1", phase_a)
    print("=== Phase B: SQ_BRIDGE_READONLY=0 ===")
    await phase("0", phase_b)


if __name__ == "__main__":
    asyncio.run(main())
