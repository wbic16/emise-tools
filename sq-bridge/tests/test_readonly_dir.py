#!/usr/bin/env python3
"""test_readonly_dir.py - v1.1 permission repro: SQ_DIR is chmod 555 with
the phext inside chmod 444 (the bridge process user can only READ it).
A read-only bridge channel must still open, read, and close, and SQ_DIR
must gain NO files (no .sq/, no bridge log) and the phext must stay
byte-identical.

Run: .venv/bin/python tests/test_readonly_dir.py [dir] [port]
Defaults: dir /tmp/sq-bridge-ro-data, port 18764.
Asserts internally; exits non-zero on any failure.
"""
import asyncio
import hashlib
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = sys.argv[1] if len(sys.argv) > 1 else "/tmp/sq-bridge-ro-data"
PORT = sys.argv[2] if len(sys.argv) > 2 else "18764"


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def snapshot(d):
    return sorted(os.listdir(d)), {f: sha256(os.path.join(d, f))
                                   for f in os.listdir(d)
                                   if os.path.isfile(os.path.join(d, f))}


def show(label, result):
    text = "".join(getattr(c, "text", str(c)) for c in result.content)
    print(f"--- {label} (isError={getattr(result, 'is_error', getattr(result, 'isError', '?'))})", flush=True)
    print(text, flush=True)
    return text, getattr(result, "is_error", False)


async def main():
    before = snapshot(DATA)
    print(f"before: {before}", flush=True)
    env = dict(os.environ)
    env.update({"SQ_DIR": DATA, "SQ_PORT": PORT, "SQ_BRIDGE_READONLY": "1"})
    python = os.environ.get("SQ_TEST_PYTHON", os.path.join(HERE, ".venv", "bin", "python"))
    bridge = os.environ.get("SQ_TEST_BRIDGE", os.path.join(HERE, "sq_bridge.py"))
    params = StdioServerParameters(command=python, args=[bridge], env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            show("sq_status", await session.call_tool("sq_status", {}))
            t, err = show("sq_open_channel(test)", await session.call_tool(
                "sq_open_channel", {"phext": "test"}))
            assert not err, "open failed on read-only SQ_DIR"
            t, err = show("sq_toc(test)", await session.call_tool(
                "sq_toc", {"phext": "test"}))
            assert "alpha scroll" in t
            t, err = show("sq_read beta", await session.call_tool(
                "sq_read", {"phext": "test", "coordinate": "1.1.1/1.1.1/1.1.2"}))
            assert t.strip() == "beta scroll: phext bridges make channels", t
            t, err = show("sq_write (must refuse)", await session.call_tool(
                "sq_write", {"phext": "test", "coordinate": "1.1.1/1.1.1/1.1.9",
                             "text": "must not land"}))
            assert err, "write was not refused"
            show("sq_close_channel", await session.call_tool("sq_close_channel", {}))
    after = snapshot(DATA)
    print(f"after: {after}", flush=True)
    assert after == before, f"SQ_DIR changed! before={before} after={after}"
    print("PASS: read-only channel worked on a 555/444 SQ_DIR; SQ_DIR listing "
          "and phext SHA-256 unchanged; no .sq or log artifacts inside SQ_DIR.")


if __name__ == "__main__":
    asyncio.run(main())
