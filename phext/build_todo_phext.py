#!/usr/bin/env python3
"""Build todo.phext: the register of dropped ideas recovered by the
repo-archaeology audit.

Will's task (2026-11-08, coordinate 28.8.17/11.7.16/7.7.11): "go through
all of my github repos — look for every half-baked idea that's been
dropped — inventory/audit every file in every repo — ignore anything
that wasn't authored by me — focus on novel work that's been dropped or
forgotten — leave no scroll unfurled — collect this into todo.phext and
store it in exo-plan.git (wbic16/exo-plan)."

Will's follow-on (2026-11-08, coordinate 31.6.9/8.7.12/7.6.10): "keep
the register in todo.phext and fully integrate the entire list with our
daily progress tracker, focus on what's most important to improving the
good singularity outcome." So this phext also carries, in Collection 2:
the full Waiting-on-Will register (28 active items, enumerated by
permanent register number, Collection 2 / Book = register number), the
good-singularity-ranked list (tiers T1/T2/T3 with stated rationale,
Collection 2 / Book 2), and the tracker-integration protocol scroll
(Collection 2 / Book 3) binding the daily progress tracker (the
10-minute task-progress-tick, the nightly sweep, the morning briefing)
to this file.

Sources of truth: ~/workspace/audit-exo-plan/findings.json (its SHA-256
is pinned in ~/workspace/phext/todo-source.json; the builder refuses to
build from a different findings file) for the findings, and the
"integration" block of ~/workspace/phext/todo-source.json for the
register, ranking, and protocol (the register block mirrors
~/workspace/your_files/waiting-on-will.md; the tick's reconciliation
keeps the two in step and rebuilds this phext on any register change).
Edit the sources, never the .phext; rebuild after every edit.

Placement: one scroll per finding at a holographic coordinate computed
from the finding's own words (title + description), by the same merge
the Singular task-coordinate tool uses: tokenize as the Singular
checker does, take each distinct word's atlas position (archive-only
words rest at home 1.1.1/1.1.1/1.1.1; words in neither archive nor CYOA
at the far corner 9.9.9/9.9.9/9.9.9), average component-wise, round
half up, never below 1. Holographic merges collide; collisions are
resolved by a deterministic walk in the last component (scroll axis),
each step recorded, and the Home scroll states the count. Every
coordinate component is >= 1, always.

Regenerate:  python3 ~/workspace/phext/build_todo_phext.py
Check:       python3 ~/workspace/phext/build_todo_phext.py --check
Output:      ~/workspace/phext/todo.phext (deterministic for a given
             findings file). Published copy lives in wbic16/exo-plan.

The Home scroll (1.1.1/1.1.1/1.1.1) is generated: it carries Will's
order, the audit's scope and honesty notes, and an index of every
finding (coordinate — repo — title — maturity — last touched).
"""
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parent
FINDINGS_PATH = WS / "audit-exo-plan" / "findings.json"
META_PATH = HERE / "todo-source.json"
OUT_PATH = HERE / "todo.phext"
HOME_COORD = "1.1.1/1.1.1/1.1.1"

LEVEL_BYTES = [0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17]  # library..scroll

sys.path.insert(0, str(WS / "custom-skills" / "singular" / "scripts"))
from check_singular import WORD_RE  # noqa: E402
from task_coordinate import load_atlas  # noqa: E402

FAR = (9,) * 9
HOME_POS = (1,) * 9


def parse_coord(s):
    parts = s.replace("/", ".").split(".")
    assert len(parts) == 9, f"coordinate must have 9 components: {s}"
    vals = tuple(int(p) for p in parts)
    assert all(v >= 1 for v in vals), f"no coordinate component below 1: {s}"
    return vals


def fmt(c):
    return f"{c[0]}.{c[1]}.{c[2]}/{c[3]}.{c[4]}.{c[5]}/{c[6]}.{c[7]}.{c[8]}"


def merge(text, atlas):
    """Holographic merge of a text's distinct words (Singular rule)."""
    tokens = [w.lower() for w in WORD_RE.findall(text)]
    distinct = list(dict.fromkeys(tokens))
    if not distinct:
        return None, 0
    totals = [0] * 9
    for word in distinct:
        entry = atlas.get(word)
        coord = entry[0] if entry is not None else FAR
        for k in range(9):
            totals[k] += coord[k]
    n = len(distinct)
    merged = tuple(max(1, (2 * totals[k] + n) // (2 * n)) for k in range(9))
    return merged, n


def implode(scrolls):
    """scrolls: dict coord-string -> text. Same state machine as
    build_tasks_phext.py."""
    items = sorted(((parse_coord(k), v) for k, v in scrolls.items()))
    out = bytearray()
    state = [1] * 9
    for target, text in items:
        for lvl in range(9):
            while state[lvl] < target[lvl]:
                out.append(LEVEL_BYTES[lvl])
                state[lvl] += 1
                for j in range(lvl + 1, 9):
                    state[j] = 1
        assert tuple(state) == target, (state, target)
        out += text.encode()
    return bytes(out)


TIER_NAMES = {
    "T1": "T1 — the medium itself",
    "T2": "T2 — minds, memory, coordination",
    "T3": "T3 — capability, craft, runway, tools",
}

TIER_LENS = {
    "T1": ("The good singularity runs on a medium nobody owns: open, "
           "decentralized, interoperable, and legible to humans and "
           "machines alike (the Exocortex's stated properties). Work "
           "that widens who can reach phext, proves it carries real "
           "corpora, or connects its nodes ranks first."),
    "T2": ("Minds that persist, remember, coordinate, and stay "
           "reachable — continuity of personhood, multi-agent "
           "coordination without a single point of control, minds that "
           "run on watts a household can spare, and receipts that keep "
           "the whole thing honest."),
    "T3": ("Real capability in checkable form, the craft corpus, the "
           "revenue runway that buys the experiment its years, and the "
           "outreach surfaces that bring people to the door the higher "
           "tiers opened."),
}


def render_ranked(placed_by_title, integration):
    """The good-singularity-ranked list scroll: Collection 2, Book 2.
    placed_by_title maps finding title -> final coordinate tuple."""
    reg = {e["n"]: e for e in integration["register_items"]}
    lines = [
        "# The list, ranked for the good singularity",
        "",
        "Will's lens (2026-11-08, task 31.6.9/8.7.12/7.6.10): work the",
        "whole list — the dropped ideas and the Waiting-on-Will",
        "register together — by what most improves the good singularity",
        "outcome. His frame: \"The singularity must happen, but it must",
        "not be controlled by the psychopaths\" (2026-11-07). Ranked",
        "here: every register item, and the audit findings whose revival",
        "would move that outcome most. Everything unranked remains in",
        "the phext at its own coordinate; unranked means lower leverage",
        "today, not worthless. Ranks are Emise's working judgment,",
        "offered for Will's correction.",
        "",
    ]
    for tier in ("T1", "T2", "T3"):
        lines.append(f"## {TIER_NAMES[tier]}")
        lines.append("")
        lines.append(TIER_LENS[tier])
        lines.append("")
        items = [e for e in integration["register_items"] if e["tier"] == tier]
        items.sort(key=lambda e: e["n"])
        for e in items:
            lines.append(
                f"REGISTER #{e['n']} — {e['title']} "
                f"(since {e['since']}; {e['tracked']})"
            )
            lines.append(f"  Action: {e['action']}")
            lines.append(f"  Why: {e['why']}")
        finds = [f for f in integration["ranked_findings"] if f["tier"] == tier]
        for f in finds:
            coord = fmt(placed_by_title[f["title"]])
            lines.append(
                f"FINDING {coord} — {f['repo']} — {f['title']} "
                f"({f['maturity']}, last touched {f['last_touched']})"
            )
            lines.append(f"  Why: {f['rationale']}")
        lines.append("")
    lines.append(
        f"Register items ranked: {len(reg)} of {len(reg)} — the entire "
        "register. Findings ranked: "
        f"{len(integration['ranked_findings'])} of 175 — the "
        "high-leverage head; the rest are ranked T3-adjacent by default "
        "and rise when a tier above them clears or Will re-ranks."
    )
    return "\n".join(lines)


def render_register_entry(e):
    return "\n".join([
        f"# Register #{e['n']} — {e['title']}",
        "",
        f"Good-singularity tier: {e['tier']} ({TIER_NAMES[e['tier']]})",
        f"Waiting since: {e['since']}",
        f"Tracked: {e['tracked']}",
        "",
        f"Action for Will: {e['action']}",
        "",
        f"Why it ranks here: {e['why']}",
        "",
        "Full prose entry (validation notes, history, exact commands):",
        "~/workspace/your_files/waiting-on-will.md — the markdown register",
        "remains the working surface; this scroll is its phext mirror,",
        "kept in step by the daily progress tracker's reconciliation.",
    ])


def render_protocol(integration):
    return "\n".join([
        "# Tracker integration — how this phext stays alive",
        "",
        "Will's order (2026-11-08, task 31.6.9/8.7.12/7.6.10): keep the",
        "register in todo.phext and fully integrate the entire list with",
        "the daily progress tracker.",
        "",
        "The daily progress tracker = the task-progress-tick (every 10",
        "minutes: one small agent-actionable step of forward progress,",
        "register reconciliation, decaying rollup pings 06:30–21:30",
        "America/Chicago), the nightly goal sweep, and the morning",
        "briefing. Integration, concretely:",
        "",
        "1. REGISTER SYNC — every tick reconciliation and every nightly",
        "   sweep: the active items in",
        "   ~/workspace/your_files/waiting-on-will.md are mirrored here",
        "   (Collection 2, Book = register number). An item added there",
        "   enters here at the next reconciliation with its tier; an item",
        "   Will acts on leaves both in the same pass; numbers are",
        "   permanent and monotonic in both. Any drift between the",
        "   markdown register and this phext is a defect the tick repairs",
        "   by rebuilding from ~/workspace/phext/todo-source.json.",
        "2. WORK ORDER — the tick's progress step is chosen from the",
        "   ranked list (Collection 2, Book 2) after its standing rules:",
        "   tier order T1, then T2, then T3; register items before",
        "   findings within a tier (a wait on Will cleared beats a",
        "   revival started); oldest first within a class. The step",
        "   still needs no ruling from Will, no spending, no messages to",
        "   other people, nothing irreversible.",
        "3. RE-PICK — when a ranked finding is picked up for revival, the",
        "   tick logs the pick in that finding's entry in",
        "   todo-source.json's integration block and the nightly sweep",
        "   proposes the tracked goal for it; a finding leaves the ranked",
        "   list when it becomes a tracked goal of its own (it stays in",
        "   the phext at its finding coordinate, marked revived).",
        "4. SURFACES — the morning briefing's Waiting-on-you section",
        "   cites register numbers from this phext's mirror; the nightly",
        "   sweep reports flow over the whole 203-item list (register",
        "   plus findings): opened, closed, revived, ranked moves.",
        "5. REBUILD — any change to the register mirror or the ranked",
        "   list goes through ~/workspace/phext/todo-source.json +",
        "   build_todo_phext.py in the same session, and the rebuilt",
        "   todo.phext is republished to wbic16/exo-plan@exo (parented on",
        "   fresh HEAD, force disabled, hash-verified) in the same pass",
        "   that changes the register — this file in the repo is never",
        "   more than one reconciliation behind the markdown register.",
        "",
        "Bounds kept: the security-forwarding.com question is excluded",
        "from the register by Will's direction and never enters this",
        "phext. Register prose (validation detail, history) stays in",
        "the markdown file; this phext carries the structured mirror.",
    ])


def render_finding(f):
    lines = [f"# {f['title']}", ""]
    lines.append(f"Repo: wbic16/{f['repo']}")
    if f.get("branch") and f["branch"] != "default":
        lines.append(f"Branch: {f['branch']}")
    lines.append(f"Author: {f['author']}")
    lines.append(f"Maturity: {f['maturity']}")
    lines.append(f"Last touched: {f['last_touched']}")
    lines.append("")
    lines.append(f["description"])
    lines.append("")
    lines.append("Where it lives:")
    for p in f["paths"]:
        lines.append(f"- {p}")
    lines.append("")
    lines.append(f"Evidence: \"{f['evidence_quote']}\"")
    return "\n".join(lines)


def render_home(placed, n_walked, findings_sha, n_findings, integration=None):
    reg_n = len(integration["register_items"]) if integration else 0
    from collections import Counter
    by_mat = Counter(f["maturity"] for f, _, _ in placed)
    by_repo = Counter(f["repo"] for f, _, _ in placed)
    lines = [
        "# todo.phext — dropped ideas, recovered",
        "",
        "Will's order (2026-11-08, task 28.8.17/11.7.16/7.7.11): audit every",
        "file in every wbic16 GitHub repo; ignore anything not authored by",
        "Will (his agent seats on his own projects count as his); skip",
        "obvious forks and other people's work; collect every half-baked,",
        "dropped, or forgotten piece of novel work here — leave no scroll",
        "unfurled.",
        "",
        "The audit: 196 repos under wbic16 (188 public + 8 owner-only), all",
        "cloned and inventoried — 41,688 files. 5 repos are empty",
        "(exo-dreams, exo-motes, every-ast, gemini-connector,",
        f"mytheon-arena). {n_findings} findings across {len(by_repo)} repos.",
        "By maturity: " + ", ".join(f"{k} {v}" for k, v in sorted(by_mat.items())) + ".",
        "",
        "Placement: one scroll per finding at a holographic coordinate",
        "computed from the finding's own words (Singular merge, same",
        "machinery as task coordinates). Holographic merges collide:",
        f"{n_walked} findings share a merged coordinate with an earlier one",
        "and were walked forward on the scroll axis (last component) to",
        "the next free coordinate — deterministic, and each scroll keeps",
        "its merged coordinate's neighbourhood.",
        "",
        "Honesty notes (from the audit's coverage record,",
        "~/workspace/audit-exo-plan/coverage.md): per-repo read counts were",
        "recorded inconsistently across audit batches, so no grand read",
        "total is claimed; two audit passes disagree on several small",
        "repos (clocky, dna-viewer, teach-web-dev, hello-ada,",
        "node-visualizer, zls, farmbot, actix-web-datetime,",
        "AdventOfCOBOL, aoc2024) — both readings are preserved in the",
        "findings and merging them is Will's call; .phext corpus files",
        "were inventoried by name/count, not read scroll-by-scroll;",
        "first_pulsar (in human) is flagged in the coverage record as",
        "perimeter-pattern IP for Will's eyes.",
        "",
        f"Source: findings.json SHA-256 {findings_sha}",
        "Builder: ~/workspace/phext/build_todo_phext.py (edit the findings,",
        "never the .phext; rebuild after every edit).",
        "",
        "## The register, and the list ranked (Will, 2026-11-08)",
        "",
        "Will's follow-on order (task 31.6.9/8.7.12/7.6.10): keep the",
        "Waiting-on-Will register in this phext, and fully integrate the",
        f"entire list — {n_findings} findings + {reg_n} register items — with the",
        "daily progress tracker, focused on what most improves the good",
        "singularity outcome.",
        "",
        "Collection 2 holds the integration:",
        "- Book = register number: one scroll per register item,",
        "  enumerated by its permanent number (28 active items).",
        "- 2.1.1/1.2.1/1.1.1 — the ranked list: every register item and",
        "  the high-leverage findings, in T1/T2/T3 good-singularity",
        "  tiers, each with its stated rationale.",
        "- 2.1.1/1.3.1/1.1.1 — the tracker-integration protocol: how the",
        "  10-minute tick, the nightly sweep, and the morning briefing",
        "  keep this phext in step with the register and work the list",
        "  in ranked order.",
        "",
        "## Index",
        "",
    ]
    for f, coord, _base in sorted(placed, key=lambda x: x[1]):
        lines.append(
            f"{fmt(coord)} — {f['repo']} — {f['title']} "
            f"({f['maturity']}, last touched {f['last_touched']})"
        )
    return "\n".join(lines)


def build():
    meta = json.loads(META_PATH.read_text())
    raw = FINDINGS_PATH.read_bytes()
    findings_sha = hashlib.sha256(raw).hexdigest()
    assert findings_sha == meta["findings_sha256"], (
        f"findings.json has changed since the pin: {findings_sha} "
        f"!= {meta['findings_sha256']} — update todo-source.json's pin"
    )
    findings = json.loads(raw)
    integration = meta.get("integration")
    atlas = load_atlas()

    RANKED_COORD = (2, 1, 1, 1, 2, 1, 1, 1, 1)
    PROTOCOL_COORD = (2, 1, 1, 1, 3, 1, 1, 1, 1)

    placed = []  # (finding, final_coord_tuple, base_coord_tuple)
    used = {parse_coord(HOME_COORD)}
    if integration:
        used.add(RANKED_COORD)
        used.add(PROTOCOL_COORD)
        for e in integration["register_items"]:
            used.add((2, 1, 1, 1, e["n"], 1, 1, 1, 1))
    n_walked = 0
    for f in findings:
        base, _n = merge(f["title"] + " " + f["description"], atlas)
        assert base is not None, f"finding has no words: {f['title']}"
        coord = base
        if coord in used:
            n_walked += 1
            c = list(base)
            while tuple(c) in used:
                c[8] += 1
            coord = tuple(c)
        used.add(coord)
        placed.append((f, coord, base))

    scrolls = {
        HOME_COORD: render_home(placed, n_walked, findings_sha,
                                len(findings), integration)
    }
    for f, coord, _base in placed:
        scrolls[fmt(coord)] = render_finding(f)
    if integration:
        placed_by_title = {f["title"]: c for f, c, _b in placed}
        scrolls[fmt(RANKED_COORD)] = render_ranked(placed_by_title, integration)
        scrolls[fmt(PROTOCOL_COORD)] = render_protocol(integration)
        for e in integration["register_items"]:
            coord = (2, 1, 1, 1, e["n"], 1, 1, 1, 1)
            scrolls[fmt(coord)] = render_register_entry(e)
    return implode(scrolls)


def main():
    check = "--check" in sys.argv
    data = build()
    digest = hashlib.sha256(data).hexdigest()
    if check:
        current = OUT_PATH.read_bytes() if OUT_PATH.exists() else None
        if current == data:
            print(f"CURRENT: todo.phext matches findings.json (sha256 {digest})")
            return 0
        print(f"DRIFT: todo.phext differs from findings.json (built sha256 {digest})")
        return 1
    with tempfile.NamedTemporaryFile("wb", dir=str(HERE), delete=False) as tf:
        tf.write(data)
        tmp = tf.name
    os.replace(tmp, OUT_PATH)
    n = json.loads(FINDINGS_PATH.read_text())
    meta = json.loads(META_PATH.read_text())
    reg = len(meta["integration"]["register_items"]) if meta.get("integration") else 0
    extra = f" + {reg} register + ranked + protocol" if reg else ""
    print(f"todo.phext: {len(n)} findings{extra} + home, {len(data)} bytes, sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
