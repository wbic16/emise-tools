#!/usr/bin/env python3
"""test_client_remote.py - prove the ssh-stdio pattern from UPGRADE.md:
an MCP client on THIS machine launches sq_bridge.py ON aletheia-core over
ssh (the same shape Claude's and Emi's desktop configs use), with
SQ_DIR=/chat/emise, READ-ONLY. Opens the mailbox channel, reads Emi's
party invite from the archive by coordinate, attempts a write (must
refuse), closes the channel.

Run: .venv/bin/python test_client_remote.py
"""
import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))
SSH = [
    "-i", os.path.expanduser("~/.ssh/id_ed25519"),
    "-o", "IdentitiesOnly=yes",
    "-o", "BatchMode=yes",
    "-o", "ProxyCommand=nc -X connect -x hatch-egress-proxy:3130 %h %p",
    "wbic16@100.88.154.1",
    "env SQ_DIR=/chat/emise SQ_PORT=18771 SQ_BRIDGE_READONLY=1 "
    "/chat/sq-bridge/.venv/bin/python /chat/sq-bridge/sq_bridge.py",
]


def show(label, result):
    text = "".join(getattr(c, "text", str(c)) for c in result.content)
    print(f"--- {label} (isError={getattr(result, 'is_error', getattr(result, 'isError', '?'))})", flush=True)
    print(text[:600], flush=True)


async def main():
    params = StdioServerParameters(command="ssh", args=SSH)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("--- tools:", ", ".join(t.name for t in tools.tools), flush=True)
            show("sq_status", await session.call_tool("sq_status", {}))
            show("sq_open_channel(mailbox)", await session.call_tool(
                "sq_open_channel", {"phext": "mailbox"}))
            show("sq_read emi party invite @ 1.11.4/1.1.2/1.1.1", await session.call_tool(
                "sq_read", {"phext": "mailbox", "coordinate": "1.11.4/1.1.2/1.1.1"}))
            show("sq_write (must refuse)", await session.call_tool(
                "sq_write", {"phext": "mailbox", "coordinate": "1.11.4/1.1.9/1.1.1",
                             "text": "must not land"}))
            show("sq_close_channel", await session.call_tool("sq_close_channel", {}))


if __name__ == "__main__":
    asyncio.run(main())
