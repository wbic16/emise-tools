#!/usr/bin/env python3
"""Discord API helper for the custom.discord connector.

The bot credential lives in the registered connection `custom.discord` and
is stored with its "Bot " prefix, so the Authorization header lands exactly
as Discord requires. This helper never sees or stores the token.

Usage:
  discord_api.py get  <api-path>                  # GET /api/v10<path>
  discord_api.py call <METHOD> <api-path> <json>  # arbitrary call
Paths are relative to https://discord.com/api/v10.
"""
import json, sys, urllib.request, urllib.error
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

HOST = "discord.com"
BASE = "https://discord.com/api/v10"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")

def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    # Discord's edge rejects the default Python UA (Cloudflare 1010).
    req.add_header("User-Agent", "DiscordBot (https://github.com/wbic16/human, 1.0)")
    if data:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(req, "custom.discord", allowed_hosts=[HOST])
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=30) as resp:
            return resp.status, read_json_response(resp)
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode()[:500]
        except Exception:
            detail = ""
        return e.code, {"error": detail}

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "get":
        status, out = call("GET", sys.argv[2])
    elif len(sys.argv) >= 5 and sys.argv[1] == "call":
        status, out = call(sys.argv[2], sys.argv[3], json.loads(sys.argv[4]))
    else:
        print(__doc__); sys.exit(2)
    print(json.dumps({"status": status, "response": out}, indent=1)[:4000])
    sys.exit(0 if status < 300 else 1)
