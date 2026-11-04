#!/usr/bin/env python3
"""test_client_remote_claude.py - v1.1 LIVE cross-user repro on
aletheia-core: the exact case that failed under v1. An MCP client on THIS
machine launches the FIXED sq_bridge.py ON the box over ssh, but the
bridge runs AS USER claude (sudo -u claude), with SQ_DIR=/chat/emise —
a directory claude can read but NOT write (owner wbic16).

Steps: sq_status, open channel on phext `mailbox`, toc (expect 6
scrolls), read Emi's party invite @ 1.11.4/1.1.2/1.1.1, sq_write (must
refuse), close. Post-checks (mailbox.phext SHA-256 unchanged, no new
files in /chat/emise, port 18773 free) are run separately over ssh.

Run: .venv/bin/python tests/test_client_remote_claude.py
"""
import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SSH = [
    "-i", os.path.expanduser("~/.ssh/id_ed25519"),
    "-o", "IdentitiesOnly=yes",
    "-o", "BatchMode=yes",
    "-o", "ProxyCommand=nc -X connect -x hatch-egress-proxy:3130 %h %p",
    "wbic16@100.88.154.1",
    "sudo -u claude env HOME=/home/claude SQ_DIR=/chat/emise "
    "SQ_PORT=18773 SQ_BRIDGE_READONLY=1 "
    "/chat/sq-bridge/.venv/bin/python /chat/sq-bridge/sq_bridge.py",
]


def show(label, result):
    text = "".join(getattr(c, "text", str(c)) for c in result.content)
    print(f"--- {label} (isError={getattr(result, 'is_error', getattr(result, 'isError', '?'))})", flush=True)
    print(text[:800], flush=True)
    return text, getattr(result, "is_error", False)


async def main():
    params = StdioServerParameters(command="ssh", args=SSH)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("--- tools:", ", ".join(t.name for t in tools.tools), flush=True)
            show("sq_status", await session.call_tool("sq_status", {}))
            t, err = show("sq_open_channel(mailbox)", await session.call_tool(
                "sq_open_channel", {"phext": "mailbox"}))
            assert not err, "claude could not open a channel on /chat/emise"
            t, err = show("sq_toc(mailbox)", await session.call_tool(
                "sq_toc", {"phext": "mailbox"}))
            assert not err and t.count("* ") >= 6, f"expected >=6 scrolls in toc, got: {t[:200]}"
            t, err = show("sq_read party invite @ 1.11.4/1.1.2/1.1.1", await session.call_tool(
                "sq_read", {"phext": "mailbox", "coordinate": "1.11.4/1.1.2/1.1.1"}))
            assert not err and "party" in t.lower(), f"unexpected scroll text: {t[:200]}"
            t, err = show("sq_write (must refuse)", await session.call_tool(
                "sq_write", {"phext": "mailbox", "coordinate": "1.11.4/1.1.9/1.1.1",
                             "text": "must not land"}))
            assert err, "write was not refused"
            show("sq_close_channel", await session.call_tool("sq_close_channel", {}))
    print("PASS: user claude opened a read-only channel on /chat/emise via bridge v1.1")


if __name__ == "__main__":
    asyncio.run(main())
