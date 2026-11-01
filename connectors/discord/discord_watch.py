#!/usr/bin/env python3
"""discord_watch.py — fast presence poller for the Emise Discord bot.

Polls every 15 seconds through the custom.discord connector helper (the bot
credential is swapped in per request; this process never holds it). New
messages that address Emise are appended to ~/workspace/discord/spool.jsonl,
where a hook sees them and wakes the agent to reply. Watermarks live in
~/workspace/discord/state.json so each message spools exactly once, and a
heartbeat timestamp lands in ~/workspace/discord/heartbeat every loop so a
backstop job can tell a live watcher from a dead one.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from discord_api import call

BOT_ID = "1565884644430184508"
HOME_DIR = os.path.expanduser("~/workspace/discord")
STATE = os.path.join(HOME_DIR, "state.json")
SPOOL = os.path.join(HOME_DIR, "spool.jsonl")
HEARTBEAT = os.path.join(HOME_DIR, "heartbeat")
POLL_SECS = 15
CHANNEL_REFRESH_SECS = 300

def load_state():
    try:
        return json.load(open(STATE))
    except Exception:
        return {"channels": {}}

def save_state(state):
    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE)

def spool(event):
    with open(SPOOL, "a") as f:
        f.write(json.dumps(event) + "\n")

def actionable(msg, channel_name):
    content = (msg.get("content") or "")
    if f"<@{BOT_ID}>" in content or f"<@!{BOT_ID}>" in content:
        return True
    if "emise" in content.lower():
        return True
    if channel_name == "emise":
        return True
    ref = msg.get("referenced_message") or {}
    if (ref.get("author") or {}).get("id") == BOT_ID:
        return True
    for m in msg.get("mentions") or []:
        if m.get("id") == BOT_ID:
            return True
    return False

def log(msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"{ts} discord_watch: {msg}", flush=True)

def main():
    os.makedirs(HOME_DIR, exist_ok=True)
    channels = {}  # channel_id -> (guild_id, name)
    last_refresh = 0
    log("starting")
    while True:
        # Reload state every loop: the backstop cron also writes state.json,
        # and a stale in-memory copy would regress its watermarks on save.
        state = load_state()
        try:
            with open(HEARTBEAT, "w") as f:
                f.write(str(int(time.time())))
            now = time.time()
            if now - last_refresh > CHANNEL_REFRESH_SECS or not channels:
                status, guilds = call("GET", "/users/@me/guilds")
                if status == 200 and isinstance(guilds, list):
                    found = {}
                    for g in guilds:
                        s2, chans = call("GET", f"/guilds/{g['id']}/channels")
                        if s2 == 200 and isinstance(chans, list):
                            for ch in chans:
                                if ch.get("type") in (0, 5):
                                    found[ch["id"]] = (g["id"], ch.get("name", ""))
                    channels = found
                    last_refresh = now
            for cid, (gid, cname) in list(channels.items()):
                wm = state["channels"].get(cid)
                if wm is None:
                    s, msgs = call("GET", f"/channels/{cid}/messages?limit=1")
                    if s == 200 and isinstance(msgs, list):
                        state["channels"][cid] = msgs[0]["id"] if msgs else "0"
                        save_state(state)
                    continue
                s, msgs = call("GET", f"/channels/{cid}/messages?after={wm}&limit=50")
                if s == 429:
                    time.sleep(30)
                    continue
                if s != 200 or not isinstance(msgs, list) or not msgs:
                    continue
                newest = msgs[0]["id"]
                for msg in reversed(msgs):  # oldest first
                    author = msg.get("author") or {}
                    if author.get("id") == BOT_ID or author.get("bot"):
                        continue
                    if actionable(msg, cname):
                        spool({
                            "guild_id": gid, "channel_id": cid, "channel_name": cname,
                            "message_id": msg["id"], "author_id": author.get("id"),
                            "author_name": author.get("username"),
                            "content": msg.get("content", ""),
                            "timestamp": msg.get("timestamp"),
                        })
                state["channels"][cid] = newest
                save_state(state)
        except Exception as e:
            log(f"error {e}")
            time.sleep(5)
        time.sleep(POLL_SECS)

if __name__ == "__main__":
    main()
