#!/usr/bin/env python3
"""GitHub API helper for the custom.github connector.

The fine-grained token lives in the registered connection `custom.github`;
this helper never sees or stores it. Each request carries a surrogate via
dynamic_credentials, which Muse swaps for the real credential only on an
approved request to api.github.com.

Usage:
  github_api.py get  <api-path>                 # GET, prints JSON
  github_api.py call <METHOD> <api-path> <json> # arbitrary call, prints JSON
"""
import json, sys, urllib.request, urllib.error
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

HOST = "api.github.com"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")

def call(method, path, body=None):
    url = f"https://{HOST}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(req, "custom.github", allowed_hosts=[HOST])
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
