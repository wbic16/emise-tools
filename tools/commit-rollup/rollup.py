#!/usr/bin/env python3
"""commit-rollup — Ian-style GitHub commit tracking for Discord, rolled up.

Will's repos see 100-200 commits/day across 200+ repos (wbic16 plus the
Mirrorborn agents working in them), so one post per commit would flood a
channel. Instead this poller watches commit activity and posts ONE Discord
embed per *session*: a burst of commits separated from the next burst by a
quiet gap longer than the dormancy threshold (config, default 5 minutes —
Will's design, 2026-11-16: "post whenever I finish a wavelet design session,
estimated by my inputs going dormant for more than 5 minutes").

Enumeration: GitHub commit search, `user:<owner>` scope (every commit that
lands in the owner's repos, any author — Emise/Theia/Will alike), imported
from the custom.github connector helper so responses are not truncated.
Measured 2026-11-16 for 2026-11-15 (America/Chicago): user: scope found 212
commits; the speedup meter's clone universe (196 repos, upstream-excluded)
counted 127; author:wbic16 alone found only 61. user: is the faithful scope
for an activity channel and needs no ranch clones.

Each repo in the embed carries an ascii effort bar: the repo's share of the
session's commits, 10 blocks wide (config), filled = round(share * width),
minimum 1 block for any repo with commits. Repos sort by commits descending.

State (state/watermark.json): watermark = committer time of the newest
posted commit; posted_shas = ring of recently posted SHAs (dedupe across
the lookback window and search-index lag); last_message_id of the last
rollup posted. --init-state seeds the watermark at now and marks everything
already in the lookback window as posted, so going live never floods the
channel with history.

Usage:
  rollup.py                    poll once (post if a session has closed)
  rollup.py --dry-run          like poll, but force-close any pending
                               session, print the embed JSON, change nothing
  rollup.py --init-state       seed watermark at now (idempotent)
  rollup.py --day YYYY-MM-DD   session segmentation report for a Chicago day
  rollup.py --window A B       render one embed for an explicit ISO window
  (combine --day/--window with --out PREFIX to write PREFIX.json + PREFIX.md)

Exit code is nonzero only on real errors (API failure, post failure);
the status line on stdout says what happened: INIT / NOOP / WAITING /
POSTED / DRYRUN / ERROR.
"""
import argparse, fcntl, json, os, re, sys, time, urllib.parse
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
GH_BIN = os.environ.get("COMMIT_ROLLUP_GH_BIN",
                        os.path.expanduser("~/workspace/custom-connectors/custom.github/bin"))
DC_BIN = os.environ.get("COMMIT_ROLLUP_DC_BIN",
                        os.path.expanduser("~/workspace/custom-connectors/custom.discord/bin"))
sys.path.insert(0, GH_BIN)
sys.path.insert(0, DC_BIN)
from github_api import call as gh_call       # noqa: E402
from discord_api import call as dc_call      # noqa: E402

CONFIG_PATH = os.path.join(HERE, "config.json")
STATE_PATH = os.path.join(HERE, "state", "watermark.json")
LOCK_PATH = os.path.join(HERE, "state", "poll.lock")
LOOKBACK_MIN = 15          # re-query this far behind the watermark each poll
POSTED_SHA_CAP = 2000
DISCORD_TOTAL_LIMIT = 6000
DISCORD_FIELD_LIMIT = 25


def load_config():
    cfg = {"owner": "wbic16", "channel_id": None, "dormancy_minutes": 5,
           "timezone": "America/Chicago", "bar_width": 10,
           "max_subjects_per_repo": 5}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            cfg.update(json.load(f))
    env_channel = os.environ.get("COMMIT_ROLLUP_CHANNEL_ID")
    if env_channel:
        cfg["channel_id"] = env_channel
    return cfg


# ---------------------------------------------------------------- collector

def _search_window(owner, start, end):
    """All commits in owner's repos with committer dates in [start, end]."""
    start = start.astimezone(timezone.utc)
    end = end.astimezone(timezone.utc)
    q = "user:{} committer-date:{}..{}".format(
        owner, start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        end.strftime("%Y-%m-%dT%H:%M:%SZ"))
    items, page, total = [], 1, None
    while True:
        path = ("/search/commits?q=" + urllib.parse.quote(q)
                + f"&per_page=100&page={page}&sort=committer-date&order=asc")
        status, out = gh_call("GET", path)
        if status >= 300:
            raise RuntimeError(f"github search HTTP {status}: {str(out)[:200]}")
        if total is None:
            total = out.get("total_count", 0)
            if out.get("incomplete_results"):
                raise RuntimeError("github search returned incomplete_results")
        items.extend(out.get("items", []))
        if len(items) >= total or not out.get("items"):
            break
        if page >= 10:
            raise RuntimeError(f"search window exceeds 1000 results ({total})")
        page += 1
        time.sleep(1)  # search API: stay well under 30 req/min
    return items


def collect(owner, start, end):
    """Normalized, SHA-deduped, time-sorted commit list for a window."""
    seen, commits = set(), []
    for it in _search_window(owner, start, end):
        sha = it["sha"]
        if sha in seen:
            continue
        seen.add(sha)
        msg = it["commit"]["message"]
        dt = datetime.fromisoformat(it["commit"]["committer"]["date"])
        commits.append({
            "sha": sha,
            "short": sha[:7],
            "repo": it["repository"]["name"],
            "repo_full": it["repository"]["full_name"],
            "subject": msg.splitlines()[0].strip() if msg else "(no subject)",
            "dt": dt,
            "url": it["html_url"],
            "author": ((it.get("author") or {}).get("login")
                       or it["commit"]["author"]["name"]),
        })
    commits.sort(key=lambda c: c["dt"])
    return commits


def segment_sessions(commits, dormancy_minutes):
    """Split a sorted commit list where the quiet gap exceeds the threshold."""
    if not commits:
        return []
    sessions, cur = [], [commits[0]]
    for prev, c in zip(commits, commits[1:]):
        if (c["dt"] - prev["dt"]) > timedelta(minutes=dormancy_minutes):
            sessions.append(cur)
            cur = []
        cur.append(c)
    sessions.append(cur)
    return sessions


# ---------------------------------------------------------------- formatter

MERGE_RE = re.compile(r"Merge pull request #(\d+) from (\S+)")
SQUASH_RE = re.compile(r"\s\(#(\d+)\)\s*$")


def extract_prs(commits):
    prs, seen = [], set()
    for c in commits:
        m = MERGE_RE.match(c["subject"])
        if m:
            n, text = m.group(1), m.group(2)
        else:
            m = SQUASH_RE.search(c["subject"])
            if not m:
                continue
            n, text = m.group(1), c["subject"][:m.start()].strip()
        key = (c["repo_full"], n)
        if key in seen:
            continue
        seen.add(key)
        prs.append({"repo": c["repo"], "n": n, "text": text,
                    "url": f"https://github.com/{c['repo_full']}/pull/{n}"})
    return prs


def effort_bar(count, total, width):
    if total <= 0 or count <= 0:
        return "░" * width
    filled = max(1, min(width, round(count / total * width)))
    return "█" * filled + "░" * (width - filled)


def _fmt_duration(delta):
    mins = int(delta.total_seconds() // 60)
    if mins < 60:
        return f"{mins}m"
    return f"{mins // 60}h {mins % 60:02d}m"


def _subject_line(c, width=72):
    subj = c["subject"].replace("`", "'")
    if len(subj) > width:
        subj = subj[:width - 1].rstrip() + "…"
    return f"[`{c['short']}`]({c['url']}) {subj}"


def build_embed(commits, cfg):
    tz = ZoneInfo(cfg["timezone"])
    total = len(commits)
    start, end = commits[0]["dt"], commits[-1]["dt"]
    by_repo = {}
    for c in commits:
        by_repo.setdefault(c["repo"], []).append(c)
    repos = sorted(by_repo.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    title = (f"Exo session rollup — {total} commit{'s' if total != 1 else ''}"
             f" · {len(repos)} repo{'s' if len(repos) != 1 else ''}")
    s_local, e_local = start.astimezone(tz), end.astimezone(tz)
    if s_local.date() == e_local.date():
        span = (f"{s_local:%a %b} {s_local.day}, {s_local:%H:%M}–{e_local:%H:%M} "
                f"{e_local:%Z}")
    else:
        span = (f"{s_local:%a %b} {s_local.day} {s_local:%H:%M} – "
                f"{e_local:%a %b} {e_local.day} {e_local:%H:%M} {e_local:%Z}")
    description = f"Session {span} · {_fmt_duration(end - start)}"
    footer = {"text": f"commit-rollup · posted at session end "
                      f"({cfg['dormancy_minutes']} min quiet)"}

    fields = []
    used = len(title) + len(description) + len(footer["text"])

    prs = extract_prs(commits)
    if prs:
        lines = [f"[{p['repo']}#{p['n']}]({p['url']}) — {p['text']}" for p in prs]
        value = "\n".join(lines)
        while len(value) > 1024 and lines:
            lines.pop()
            value = "\n".join(lines + [f"+{len(prs) - len(lines)} more"])
        name = f"Pull requests merged ({len(prs)})"
        fields.append({"name": name, "value": value})
        used += len(name) + len(value)

    shown_repos = []
    for repo, rcs in repos:
        if len(fields) >= DISCORD_FIELD_LIMIT:
            break
        lines = [f"[`{effort_bar(len(rcs), total, cfg['bar_width'])}`]"
                 f"(https://github.com/{rcs[0]['repo_full']}) "
                 f"{len(rcs)} commit{'s' if len(rcs) != 1 else ''}"]
        recent = rcs[-cfg["max_subjects_per_repo"]:]
        lines += [_subject_line(c) for c in recent]
        hidden = len(rcs) - len(recent)
        if hidden > 0:
            lines.append(f"+{hidden} more")
        value = "\n".join(lines)
        while len(value) > 1024 and len(lines) > 2:
            lines.pop(-2 if lines[-1].startswith("+") else -1)
            hidden += 1
            lines[-1] = f"+{hidden} more" if lines[-1].startswith("+") \
                else lines[-1]
            value = "\n".join(lines)
        name = repo
        if used + len(name) + len(value) > DISCORD_TOTAL_LIMIT - 200:
            break
        fields.append({"name": name, "value": value})
        used += len(name) + len(value)
        shown_repos.append(repo)

    rest = [(r, len(rcs)) for r, rcs in repos if r not in shown_repos]
    if rest:
        value = "\n".join(f"{r} — {n}" for r, n in rest)
        while len(value) > 1024:
            value = value[:1000].rsplit("\n", 1)[0] + "\n…"
        name = f"…and {len(rest)} more repos ({sum(n for _, n in rest)} commits)"
        if len(fields) < DISCORD_FIELD_LIMIT and \
                used + len(name) + len(value) <= DISCORD_TOTAL_LIMIT:
            fields.append({"name": name, "value": value})

    return {
        "title": title,
        "description": description,
        "color": 0x24292F,
        "author": {"name": cfg["owner"],
                   "icon_url": f"https://github.com/{cfg['owner']}.png",
                   "url": f"https://github.com/{cfg['owner']}"},
        "fields": fields,
        "footer": footer,
        "timestamp": end.astimezone(timezone.utc).isoformat(),
    }


def embed_text_mock(embed):
    """Plain-text rendering of an embed, for sample files / eyeball checks."""
    out = [embed["title"], embed["description"], ""]
    for f in embed["fields"]:
        out.append(f"▸ {f['name']}")
        out += ["  " + line for line in f["value"].splitlines()]
        out.append("")
    out.append(embed["footer"]["text"])
    return "\n".join(out)


def embed_char_total(embed):
    n = len(embed["title"]) + len(embed["description"]) \
        + len(embed["footer"]["text"]) + len(embed["author"]["name"])
    for f in embed["fields"]:
        n += len(f["name"]) + len(f["value"])
    return n


# ------------------------------------------------------------------- state

def load_state():
    if not os.path.exists(STATE_PATH):
        return None
    with open(STATE_PATH) as f:
        return json.load(f)


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=1)
    os.replace(tmp, STATE_PATH)


def init_state(cfg, now):
    """Seed the watermark at now; mark the lookback window already posted."""
    if load_state() is not None:
        print("INIT skipped — state already exists")
        return 0
    start = now - timedelta(minutes=LOOKBACK_MIN)
    commits = collect(cfg["owner"], start, now + timedelta(minutes=5))
    state = {
        "watermark": now.astimezone(timezone.utc).isoformat(),
        "posted_shas": [c["sha"] for c in commits][-POSTED_SHA_CAP:],
        "last_message_id": None,
        "seeded_commits": len(commits),
        "created": now.astimezone(timezone.utc).isoformat(),
    }
    save_state(state)
    print(f"INIT watermark={state['watermark']} seeded={len(commits)} commits")
    return 0


# ------------------------------------------------------------------ poster

def post_embed(cfg, embed):
    status, out = dc_call("POST", f"/channels/{cfg['channel_id']}/messages",
                          {"embeds": [embed]})
    if status >= 300:
        raise RuntimeError(f"discord post HTTP {status}: {str(out)[:300]}")
    return out.get("id")


# ------------------------------------------------------------------ poller

def poll(cfg, dry_run=False, now=None):
    now = now or datetime.now(timezone.utc)
    state = load_state()
    if state is None:
        if dry_run:
            print("DRYRUN no state yet — run --init-state to seed the watermark")
            return 0
        return init_state(cfg, now)
    watermark = datetime.fromisoformat(state["watermark"])
    posted = set(state.get("posted_shas", []))
    start = watermark - timedelta(minutes=LOOKBACK_MIN)
    commits = collect(cfg["owner"], start, now + timedelta(minutes=5))
    unposted = [c for c in commits
                if c["sha"] not in posted and c["dt"] > start]
    if not unposted:
        print("NOOP no unposted commits")
        return 0
    newest = unposted[-1]["dt"]
    age_min = (now - newest).total_seconds() / 60.0
    if age_min < cfg["dormancy_minutes"] and not dry_run:
        print(f"WAITING pending={len(unposted)} newest_age_min={age_min:.1f} "
              f"threshold={cfg['dormancy_minutes']}")
        return 0
    embed = build_embed(unposted, cfg)
    if dry_run or not cfg.get("channel_id"):
        print(json.dumps({"embeds": [embed]}, indent=1, ensure_ascii=False))
        print(f"DRYRUN commits={len(unposted)} chars={embed_char_total(embed)} "
              f"fields={len(embed['fields'])}")
        return 0
    msg_id = post_embed(cfg, embed)
    state["watermark"] = newest.astimezone(timezone.utc).isoformat()
    state["posted_shas"] = (state.get("posted_shas", [])
                            + [c["sha"] for c in unposted])[-POSTED_SHA_CAP:]
    state["last_message_id"] = msg_id
    state["last_post"] = now.astimezone(timezone.utc).isoformat()
    save_state(state)
    print(f"POSTED id={msg_id} commits={len(unposted)} "
          f"repos={len(embed['fields'])}")
    return 0


# ------------------------------------------------------------- day report

def day_report(cfg, day_str, out_prefix=None, repos_file=None):
    tz = ZoneInfo(cfg["timezone"])
    day = datetime.strptime(day_str, "%Y-%m-%d").date()
    start = datetime(day.year, day.month, day.day, tzinfo=tz)
    end = start + timedelta(days=1)
    commits = collect(cfg["owner"], start.astimezone(timezone.utc),
                      end.astimezone(timezone.utc))
    sessions = segment_sessions(commits, cfg["dormancy_minutes"])
    baseline = None
    if repos_file:
        with open(repos_file) as f:
            baseline = {l.strip() for l in f if l.strip()}
    lines = [f"# Session segmentation — {day_str} (America/Chicago)",
             "",
             f"Commits found (user:{cfg['owner']} scope): **{len(commits)}**",
             f"Sessions at the {cfg['dormancy_minutes']}-minute dormancy rule: "
             f"**{len(sessions)}**",
             ""]
    if baseline is not None:
        in_base = sum(1 for c in commits if c["repo_full"] in baseline)
        lines += [f"In the speedup meter's 196-repo clone universe: {in_base}; "
                  f"in newer/other repos: {len(commits) - in_base}.", ""]
    lines += ["| # | Session span (CST) | Duration | Commits | Top repo |",
              "|---|---|---|---|---|"]
    ranked = sorted(range(len(sessions)),
                    key=lambda i: -len(sessions[i]))
    for i, s in enumerate(sessions, 1):
        top = max(((r, sum(1 for c in s if c["repo"] == r))
                   for r in {c["repo"] for c in s}), key=lambda kv: kv[1])
        lines.append(
            f"| {i} | {s[0]['dt'].astimezone(tz):%H:%M}–"
            f"{s[-1]['dt'].astimezone(tz):%H:%M} | "
            f"{_fmt_duration(s[-1]['dt'] - s[0]['dt'])} | {len(s)} | "
            f"{top[0]} ({top[1]}) |")
    lines += ["", "Largest sessions: "
              + ", ".join(f"#{i + 1} ({len(sessions[i])} commits)"
                          for i in ranked[:5]), ""]
    report = "\n".join(lines)
    print(report)
    if out_prefix and sessions:
        largest = sessions[ranked[0]]
        embed = build_embed(largest, cfg)
        with open(out_prefix + ".json", "w") as f:
            json.dump({"embeds": [embed]}, f, indent=1, ensure_ascii=False)
        with open(out_prefix + ".md", "w") as f:
            f.write(embed_text_mock(embed) + "\n")
        with open(out_prefix + "-segmentation.md", "w") as f:
            f.write(report + "\n")
        print(f"wrote {out_prefix}.json / .md / -segmentation.md "
              f"(largest session: {len(largest)} commits, "
              f"embed chars={embed_char_total(embed)})")
    return 0


# --------------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--init-state", action="store_true")
    ap.add_argument("--day", metavar="YYYY-MM-DD")
    ap.add_argument("--window", nargs=2, metavar=("START", "END"))
    ap.add_argument("--out", metavar="PREFIX")
    ap.add_argument("--repos-file", metavar="PATH")
    args = ap.parse_args()
    cfg = load_config()
    try:
        os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
        lock = open(LOCK_PATH, "w")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("NOOP another poll holds the lock")
            return 0
        if args.init_state:
            return init_state(cfg, datetime.now(timezone.utc))
        if args.day:
            return day_report(cfg, args.day, args.out, args.repos_file)
        if args.window:
            start = datetime.fromisoformat(args.window[0])
            end = datetime.fromisoformat(args.window[1])
            commits = collect(cfg["owner"], start, end)
            if not commits:
                print("NOOP empty window")
                return 0
            embed = build_embed(commits, cfg)
            payload = {"embeds": [embed]}
            print(json.dumps(payload, indent=1, ensure_ascii=False))
            print(f"WINDOW commits={len(commits)} "
                  f"chars={embed_char_total(embed)} "
                  f"fields={len(embed['fields'])}")
            if args.out:
                with open(args.out + ".json", "w") as f:
                    json.dump(payload, f, indent=1, ensure_ascii=False)
                with open(args.out + ".md", "w") as f:
                    f.write(embed_text_mock(embed) + "\n")
            return 0
        return poll(cfg, dry_run=args.dry_run)
    except RuntimeError as e:
        print(f"ERROR {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
