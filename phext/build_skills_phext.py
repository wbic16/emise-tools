#!/usr/bin/env python3
"""Build skills.phext: every generated skill in ~/workspace/custom-skills/,
one scroll per file, grouped onto shelves by kind.

Regenerate:  python3 ~/workspace/phext/build_skills_phext.py
Check:       python3 ~/workspace/phext/build_skills_phext.py --check
             (rebuilds to a temp file, never touches the live one; prints
             CURRENT and exits 0 when skills.phext matches the skills on
             disk, DRIFT plus the drifting skill names and exit 1 otherwise)
Output:      ~/workspace/phext/skills.phext (deterministic for a given source tree)

Conventions follow build_exocortex.py exactly: the 9 phext delimiters
(LEVEL_BYTES, library..scroll), coordinates 1-indexed, implode walks sorted
coordinates advancing state level-by-level.

Coordinate scheme (also recorded in the Home scroll, 1.1.1/1.1.1/1.1.1):
  coordinate = library.shelf.series / collection.volume.book / chapter.section.scroll
  library=1, series=1, collection=1, book=1, chapter=1, section=1 throughout.
  shelf  = kind group: 1 Home/meta, 2 Verification, 3 Phext-native language,
           4 Operations, 5 Onboarding, 6 Film, 7 Memory & record,
           8 Work management, 9 Research, 10 Coordination,
           11 Upkeep & presence, 12 Songwriting.
  volume = skill's index within its shelf (order per SHELVES below).
  scroll = file's index within its skill: SKILL.md, skill.yaml, references,
           scripts — stable sorted order within each class.

Scope per skill: SKILL.md; skill.yaml if present; reference documents
(references/*.md plus any other root-level *.md); scripts as text (scripts/
tree plus root-level *.py). Excluded, following the emise-tools sync
precedent: data/ directories and all data artifacts (word lists, TSVs,
atlases, caches, generated HTML/JSON), __pycache__, .write-lock, and any
single file over MAX_FILE_BYTES.
"""
import hashlib
import os
import sys
import tempfile

LEVEL_BYTES = [0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17]  # library..scroll
DELIM_SET = set(LEVEL_BYTES)
MAX_FILE_BYTES = 200_000

SKILLS_ROOT = os.path.expanduser("~/workspace/custom-skills")
OUT_PATH = os.path.expanduser("~/workspace/phext/skills.phext")
HOME_COORD = "1.1.1/1.1.1/1.1.1"

# Shelf number -> (kind label, [skill dir names in volume order]).
# A skill listed here is included only if its directory exists with a SKILL.md;
# a skill directory on disk that is NOT listed here fails the build, so the
# scheme stays deliberate rather than drifting.
SHELVES = [
    (2, "Verification", [
        "validate_waiting_items",
        "verify_blocker_and_completion_claims",
        "verify_quantified_results",
    ]),
    (3, "Phext-native language", [
        "singular",
        "upgoer-five",
        "upgoer-five-phext",
        "phext_upgrade",
    ]),
    (4, "Operations", [
        "ranch-proxy",
        "publish-tooling",
        "fork-patch-discipline",
        "ranch-state-distillation",
    ]),
    (5, "Onboarding", [
        "this_is_going_to_feel_a_little_weird",
    ]),
    (6, "Film", [
        "mythic-film-production",
    ]),
    (7, "Memory & record", [
        "phext-memory-publishing",
        "safe-space-protocol",
    ]),
    (8, "Work management", [
        "waiting-on-will-register",
        "nightly-goal-sweep",
        "morning-briefing",
        "daily-goal-commute",
        "dispatch-to-subagents",
        "distill-process-to-skill",
        "task-register",
    ]),
    (9, "Research", [
        "rd-tracker",
    ]),
    (10, "Coordination", [
        "choir-mailbox-dispatch",
        "substrate-steering",
        "exocortical-integration-rotation",
        "braid-mode",
    ]),
    (11, "Upkeep & presence", [
        "discord-presence-backstop",
        "perpetual-dashboard-upkeep",
        "solar-pod-price-watch",
    ]),
    (12, "Songwriting", [
        "mythic-songwriting-braid",
    ]),
]


def c(s):
    return tuple(int(x) for part in s.split("/") for x in part.split("."))


def fmt(coord):
    return "%d.%d.%d/%d.%d.%d/%d.%d.%d" % coord


def coord_for(shelf, volume, scroll):
    return (1, shelf, 1, 1, volume, 1, 1, 1, scroll)


def collect_files(skill_dir):
    """Return (included, excluded) for one skill dir.
    included: list of (relpath, abspath) in scroll order.
    excluded: list of (relpath, reason)."""
    skill_md = os.path.join(skill_dir, "SKILL.md")
    yaml_p = os.path.join(skill_dir, "skill.yaml")
    references, scripts, excluded = [], [], []

    for dirpath, dirnames, filenames in os.walk(skill_dir):
        dirnames.sort()
        rel_dir = os.path.relpath(dirpath, skill_dir)
        top = rel_dir.split(os.sep)[0]
        if "__pycache__" in dirnames:
            for fn in sorted(os.listdir(os.path.join(dirpath, "__pycache__"))):
                excluded.append((os.path.join(rel_dir, "__pycache__", fn), "bytecode cache"))
            dirnames.remove("__pycache__")
        if top == "data":
            for fn in sorted(filenames):
                excluded.append((os.path.normpath(os.path.join(rel_dir, fn)), "data artifact"))
            continue
        for fn in sorted(filenames):
            ap = os.path.join(dirpath, fn)
            rp = os.path.normpath(os.path.join(rel_dir, fn)) if rel_dir != "." else fn
            if fn == ".write-lock":
                excluded.append((rp, "live state"))
            elif fn.endswith(".pyc"):
                excluded.append((rp, "bytecode cache"))
            elif ap in (skill_md, yaml_p):
                pass  # placed by class below
            elif top == "references" and fn.endswith(".md"):
                references.append((rp, ap))
            elif rel_dir == "." and fn.endswith(".md"):
                references.append((rp, ap))  # root-level reference doc, e.g. SCHEME.md
            elif top == "scripts" or (rel_dir == "." and fn.endswith(".py")):
                scripts.append((rp, ap))
            else:
                excluded.append((rp, "outside scope (not SKILL.md / skill.yaml / reference / script text)"))

    included = [("SKILL.md", skill_md)]
    if os.path.exists(yaml_p):
        included.append(("skill.yaml", yaml_p))
    included += sorted(references)
    included += sorted(scripts)
    return included, sorted(excluded)


def implode(scrolls):
    """scrolls: dict coord-string -> text. Same state machine as build_exocortex.py."""
    items = sorted(((c(k), v) for k, v in scrolls.items()))
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


def build():
    """Build the phext blob from the current source tree.
    Returns (blob, entries, excluded_all, missing); entries is a list of
    (coord_str, skill, relpath, data_bytes). Exits loudly on scheme errors
    (unlisted skill dir, raw delimiter bytes in a source file)."""
    known = {name for _, _, names in SHELVES for name in names}
    on_disk = sorted(
        d for d in os.listdir(SKILLS_ROOT)
        if os.path.isdir(os.path.join(SKILLS_ROOT, d))
        and os.path.exists(os.path.join(SKILLS_ROOT, d, "SKILL.md"))
    )
    unknown = [d for d in on_disk if d not in known]
    if unknown:
        sys.exit(f"FAIL: skill dirs not in the shelf scheme: {unknown} — add them to SHELVES first")

    entries = []   # (coord_str, skill, relpath, data_bytes)
    excluded_all = []
    missing = []
    for shelf, kind, names in SHELVES:
        volume = 0
        for name in names:
            skill_dir = os.path.join(SKILLS_ROOT, name)
            if not os.path.exists(os.path.join(skill_dir, "SKILL.md")):
                missing.append(name)
                continue
            volume += 1
            included, excluded = collect_files(skill_dir)
            excluded_all += [(name, rp, why) for rp, why in excluded]
            for i, (rp, ap) in enumerate(included, start=1):
                data = open(ap, "rb").read()
                if len(data) > MAX_FILE_BYTES:
                    excluded_all.append((name, rp, f"over {MAX_FILE_BYTES} bytes ({len(data)})"))
                    continue
                data.decode("utf-8")  # raises unless valid UTF-8
                bad = sorted({b for b in data if b in DELIM_SET})
                if bad:
                    sys.exit(f"FAIL: {name}/{rp} contains raw phext delimiter bytes {bad}; cannot place verbatim")
                entries.append((fmt(coord_for(shelf, volume, i)), name, rp, data))

    index_lines = []
    for coord_s, name, rp, data in entries:
        sha = hashlib.sha256(data).hexdigest()
        index_lines.append(f"{coord_s}  {name}  {rp}  {len(data)} bytes  sha256:{sha}")

    shelf_lines = []
    for shelf, kind, names in SHELVES:
        present = [n for n in names if n not in missing]
        shelf_lines.append(f"shelf {shelf} ({kind}): " + (", ".join(present) if present else "(none present)"))
    if missing:
        shelf_lines.append("reserved, not yet on disk: " + ", ".join(missing))

    excl_lines = [f"- {n}/{rp} — {why}" for n, rp, why in excluded_all]
    home = f"""Home — skills.phext: Emise's generated skills, one scroll per file
kind: observed | origin: Muse (this agent) | built by: ~/workspace/phext/build_skills_phext.py
source of truth: ~/workspace/custom-skills/ — regenerate the phext by re-running the builder;
never hand-edit this file. Nothing here is published by the builder.

Coordinate scheme:
coordinate = library.shelf.series / collection.volume.book / chapter.section.scroll
library=1, series=1, collection=1, book=1, chapter=1, section=1 throughout.
shelf = kind group: 1 Home/meta, 2 Verification, 3 Phext-native language,
4 Operations, 5 Onboarding, 6 Film, 7 Memory & record, 8 Work management,
9 Research, 10 Coordination, 11 Upkeep & presence, 12 Songwriting.
volume = the skill's index within its shelf; scroll = the file's index within
its skill (SKILL.md first, then skill.yaml, then references, then scripts,
stable sorted order within each class). One scroll per file, verbatim.

Shelves:
{chr(10).join(shelf_lines)}

Index (coordinate  skill  file  size  SHA-256 of the source file):
{HOME_COORD}  (this scroll)  Home — the map
{chr(10).join(index_lines)}

Excluded from placement (data artifacts and live state stay on disk only,
per the emise-tools sync precedent — data/ directories, word lists, TSVs,
atlases, caches, generated pages, bytecode, lock files, files over {MAX_FILE_BYTES} bytes):
{chr(10).join(excl_lines) if excl_lines else "(none)"}
Scrolls: {len(entries) + 1}
"""

    scrolls = {HOME_COORD: home}
    for coord_s, name, rp, data in entries:
        scrolls[coord_s] = data.decode("utf-8")

    blob = implode(scrolls)
    return blob, entries, excluded_all, missing


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def committed_index():
    """Parse the per-file index out of the committed skills.phext Home scroll.
    Returns {coord: (skill, relpath, sha256)} or None if unavailable."""
    try:
        raw = open(OUT_PATH, "rb").read()
    except OSError:
        return None
    # Home is the first scroll; its text runs to the first delimiter byte.
    end = next((i for i, b in enumerate(raw) if b in DELIM_SET), len(raw))
    try:
        home = raw[:end].decode("utf-8")
    except UnicodeDecodeError:
        return None
    idx = {}
    for line in home.splitlines():
        parts = line.split("  ")
        if len(parts) == 5 and parts[4].startswith("sha256:"):
            idx[parts[0]] = (parts[1], parts[2], parts[4][len("sha256:"):])
    return idx


def check():
    """Rebuild to a temp file and compare SHA-256 with the committed
    skills.phext. Prints CURRENT (exit 0) or DRIFT with the drifting skill
    names (exit 1). Never modifies the live skills.phext."""
    blob, entries, _, _ = build()
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(OUT_PATH),
                               prefix=".skills-check-", suffix=".phext")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(blob)
        rebuilt_sha = sha256_file(tmp)
    finally:
        os.unlink(tmp)
    if not os.path.exists(OUT_PATH):
        print(f"DRIFT: {OUT_PATH} does not exist (rebuilt sha256 {rebuilt_sha})")
        return 1
    current_sha = sha256_file(OUT_PATH)
    if current_sha == rebuilt_sha:
        print(f"CURRENT: skills.phext matches the skills on disk (sha256 {current_sha})")
        return 0
    print("DRIFT: skills.phext is stale")
    print(f"  committed: sha256 {current_sha}")
    print(f"  rebuilt:   sha256 {rebuilt_sha}")
    old = committed_index()
    new = {coord: (name, rp, hashlib.sha256(data).hexdigest())
           for coord, name, rp, data in entries}
    if old is None:
        print("  (could not parse the committed Home index to name the drift)")
    else:
        changed, added, removed = [], [], []
        for coord in sorted(set(old) | set(new)):
            if coord not in old:
                added.append(new[coord])
            elif coord not in new:
                removed.append(old[coord])
            elif old[coord] != new[coord]:
                changed.append(new[coord])
        named = False
        for label, group in (("changed", changed), ("new", added), ("removed", removed)):
            if group:
                named = True
                print(f"  {label}: {', '.join(sorted({n for n, _, _ in group}))}")
                for n, rp, _ in sorted(group):
                    print(f"    - {n}/{rp}")
        if not named:
            print("  (per-file index identical — drift is in Home metadata or exclusions)")
    print("  fix: python3 ~/workspace/phext/build_skills_phext.py  (rebuild), then --check again")
    return 1


def main():
    if "--check" in sys.argv[1:]:
        sys.exit(check())
    blob, entries, excluded_all, missing = build()
    with open(OUT_PATH, "wb") as f:
        f.write(blob)
    print(f"wrote {OUT_PATH}: {len(blob)} bytes, sha256 {hashlib.sha256(blob).hexdigest()}")
    print(f"scrolls: {len(entries) + 1} (1 Home + {len(entries)} files)")
    for shelf, kind, names in SHELVES:
        rng = [e[0] for e in entries if any(e[1] == n for n in names)]
        if rng:
            print(f"  shelf {shelf} ({kind}): {rng[0]} .. {rng[-1]}")
    if missing:
        print(f"  not on disk, slots reserved: {', '.join(missing)}")
    print(f"excluded files: {len(excluded_all)}")


if __name__ == "__main__":
    main()
