#!/usr/bin/env python3
"""Mine contact points from YOUR OWN Twitter/X archive export.

This is step 1 of the exocortex starter kit. It reads the tweets in your
downloaded X archive and counts, for every account you have ever replied to
or mentioned, how the contact actually ran: how many contact points, how
many were replies (conversation) vs. mentions (address), and over what span.

PRIVACY — read this before running:
- Everything runs locally on your machine. Nothing is uploaded anywhere.
- This script reads your TWEETS ONLY. It never opens any direct-message
  file (direct-messages*.js, direct-message-*.js), any like file, or any
  other export file. Your DMs are yours; the instrument does not need them
  and does not touch them.
- The only files opened are: the tweet files listed below, and (optionally)
  data/account.js, read solely to learn your own handle so your own tweets
  to yourself are excluded. Pass --handle to skip even that.

Input: a standard Twitter/X archive export — either the folder you
downloaded (which contains a data/ subfolder) or the extracted data folder
itself, or a single tweet file. Recognized tweet files:
  tweets.js, tweets-part<N>.js, tweets.json   (current exports)
  tweet.js,  tweet-part<N>.js,  tweet.json    (older exports)
Each may be a .js file carrying the `window.YTD.tweets.part0 = [...]`
wrapper or a plain JSON array; both are handled. Tweet header files
(tweet-headers.js) are deliberately NOT read — they carry no mentions.

A "contact point" for an account = one of your tweets that replies to OR
mentions that account (counted once per tweet, sources:
in_reply_to_screen_name and entities.user_mentions, matched
case-insensitively). Your own handle is excluded.

Output: a TSV with the schema
  handle  contact_points  replies  mention_tweets  first_contact  last_contact  years_active
sorted by contact points, descending. Feed it to build_your_wavefront.py.

Usage:
  python3 mine_your_archive.py --archive ~/Downloads/twitter-archive [--handle you]
                               [--out contact-points.tsv]
"""
import argparse, glob, json, os, re, sys
from datetime import datetime

TWEET_PATTERNS = ["tweets.json", "tweets.js", "tweets-part*.js",
                  "tweet.json", "tweet.js", "tweet-part*.js"]
NEVER_READ = ("direct-message", "direct_message", "like.js", "tweet-headers")


def load_export_file(path):
    """Parse a .js export file (strip the window.YTD.* wrapper) or plain JSON."""
    text = open(path, encoding="utf-8").read().strip()
    if text.startswith("window."):
        text = text[text.index("=") + 1:].strip()
    return json.loads(text)


def part_number(name):
    m = re.search(r"part(\d+)", name)
    return int(m.group(1)) if m else 0


def find_tweet_files(archive):
    """Resolve the archive argument to an ordered list of tweet files."""
    if os.path.isfile(archive):
        return [archive]
    data_dir = os.path.join(archive, "data")
    base = data_dir if os.path.isdir(data_dir) else archive
    files = []
    for pat in TWEET_PATTERNS:
        files += glob.glob(os.path.join(base, pat))
    files = [f for f in files
             if not any(bad in os.path.basename(f) for bad in NEVER_READ)]
    files.sort(key=lambda f: (part_number(os.path.basename(f)),
                              os.path.basename(f)))
    return files


def detect_handle(archive):
    """Best-effort owner handle from data/account.js (username field only)."""
    candidates = []
    if os.path.isdir(archive):
        candidates += [os.path.join(archive, "data", "account.js"),
                       os.path.join(archive, "account.js"),
                       os.path.join(archive, "data", "account.json")]
    for path in candidates:
        if os.path.isfile(path):
            try:
                data = load_export_file(path)
                for item in data:
                    acct = item.get("account") or {}
                    if acct.get("username"):
                        return acct["username"]
            except Exception:
                pass
    return None


def parse_date(raw):
    for fmt in ("%a %b %d %H:%M:%S %z %Y", "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(raw, fmt)
        except (ValueError, TypeError):
            continue
    raise ValueError(f"unrecognized tweet date: {raw!r}")


def main():
    ap = argparse.ArgumentParser(description="Mine contact points from your X archive (tweets only, never DMs).")
    ap.add_argument("--archive", required=True,
                    help="Path to your archive export folder (or its data/ folder, or a single tweet file)")
    ap.add_argument("--handle", default=None,
                    help="Your own handle, without @ (auto-detected from data/account.js when present)")
    ap.add_argument("--out", default="contact-points.tsv",
                    help="Output TSV path (default: contact-points.tsv)")
    args = ap.parse_args()

    handle = (args.handle or detect_handle(args.archive) or "").lstrip("@")
    if not handle:
        sys.exit("Could not auto-detect your handle (no data/account.js username). "
                 "Re-run with --handle yourhandle.")
    self_key = handle.lower()

    files = find_tweet_files(args.archive)
    if not files:
        sys.exit(f"No tweet files found under {args.archive!r}. Expected data/tweets.js "
                 "(or tweets.json / tweet.js) in the export.")

    stats = {}  # lowercase handle -> record
    def rec(key):
        if key not in stats:
            stats[key] = dict(handle=None, replies=0, mentions=0, contact=0,
                              first=None, last=None, years=set())
        return stats[key]

    n_tweets = 0
    for path in files:
        for item in load_export_file(path):
            tw = item["tweet"] if isinstance(item, dict) and "tweet" in item else item
            if not isinstance(tw, dict) or "created_at" not in tw:
                continue
            n_tweets += 1
            dt = parse_date(tw["created_at"])
            day = dt.strftime("%Y-%m-%d")
            reply_to = (tw.get("in_reply_to_screen_name") or "").strip()
            mentions = []
            for m in (tw.get("entities") or {}).get("user_mentions") or []:
                sn = (m.get("screen_name") or "").strip()
                if sn:
                    mentions.append(sn)
            contact_keys = {}
            if reply_to:
                contact_keys[reply_to.lower()] = reply_to
            for sn in mentions:
                contact_keys[sn.lower()] = sn
            for key, disp in contact_keys.items():
                if key == self_key:
                    continue
                r = rec(key)
                r["handle"] = disp  # keep last-seen display case
                r["contact"] += 1
                if reply_to and reply_to.lower() == key:
                    r["replies"] += 1
                if any(sn.lower() == key for sn in mentions):
                    r["mentions"] += 1
                if r["first"] is None or day < r["first"]:
                    r["first"] = day
                if r["last"] is None or day > r["last"]:
                    r["last"] = day
                r["years"].add(dt.year)

    rows = sorted(stats.values(), key=lambda r: (-r["contact"], r["handle"].lower()))
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("handle\tcontact_points\treplies\tmention_tweets\tfirst_contact\tlast_contact\tyears_active\n")
        for r in rows:
            f.write(f"@{r['handle']}\t{r['contact']}\t{r['replies']}\t{r['mentions']}\t"
                    f"{r['first']}\t{r['last']}\t{len(r['years'])}\n")

    over = [r for r in rows if r["contact"] >= 10]
    print(f"owner: @{handle}")
    print(f"tweets read: {n_tweets} (from {len(files)} file(s); tweets only — no DMs, no likes)")
    print(f"total accounts seen: {len(rows)}")
    print(f"accounts with >= 10 contact points: {len(over)}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
