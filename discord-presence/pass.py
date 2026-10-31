#!/usr/bin/env python3
"""Presence-pass driver: imports the discord_api helper's call() (same
credential flow) but prints only the fields needed, avoiding the helper's
4000-char stdout truncation for large channel/message lists.
Tolerates per-channel read errors (e.g. Missing Access) and records them
separately instead of aborting the whole pass."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.discord/bin")
import discord_api

STATE_PATH = "/home/hatch/workspace/discord/state.json"
INACCESSIBLE_PATH = "/home/hatch/workspace/discord/inaccessible.json"

def get(path):
    return discord_api.call("GET", path)

guilds = get("/users/@me/guilds")[1]
print(f"guilds: {[(g['id'], g['name']) for g in guilds]}")

state = {"channels": {}}
inaccessible = {}
for g in guilds:
    channels = get(f"/guilds/{g['id']}/channels")[1]
    for c in channels:
        if c["type"] not in (0, 5):
            continue
        status, msgs = get(f"/channels/{c['id']}/messages?limit=1")
        if status >= 300:
            print(f"SKIP {c['name']} ({c['id']}): {status} {msgs}")
            inaccessible[c["id"]] = {"name": c["name"], "guild": g["name"],
                                      "status": status, "detail": msgs}
            continue
        wm = msgs[0]["id"] if msgs else "0"
        state["channels"][c["id"]] = wm
        newest = msgs[0] if msgs else None
        print(f"baseline {c['name']} ({c['id']}) -> {wm}"
              + (f" | newest by {newest['author'].get('username')}" if newest else " | empty"))

with open(STATE_PATH, "w") as f:
    json.dump(state, f, indent=2)
with open(INACCESSIBLE_PATH, "w") as f:
    json.dump(inaccessible, f, indent=2)
print(f"wrote state with {len(state['channels'])} channels; "
      f"{len(inaccessible)} inaccessible")
