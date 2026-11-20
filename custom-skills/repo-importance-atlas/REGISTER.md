# Repo Importance Atlas — the register

One entry per wbic16 GitHub repo: what it is for, what state it is in, what in it
matters, and which of Will's standing rules touch it. Read the entry for a repo
BEFORE working in it.

Derived from the full audit of 2026-11-20: the live GitHub API repo list (226
repos), each repo's metadata, canonical branch (exo where it exists), root tree,
README, and recent commits. Method and refresh process: see SKILL.md in this
skill directory. Tier is the auditor's judgment from that evidence, labelled as
judgment; where the evidence could not support a purpose, the entry says so
plainly instead of inventing one.

Entry format:
  Role — what the repo is and what it does for the Exocortex / Phext, Inc.
  Status — active (pushed within 90 days of the audit) / quiet / seed-empty /
    superseded-by / archived
  Matters — canonical files, entry points, artifacts to read first or not break
  Watch-outs — standing rules that genuinely apply to this repo (omitted if none)
  Tier — flagship / working / archive / unknown (judgment)
  Evidence — canonical branch, last push, size, fork parent

Audit totals (2026-11-20): 226 repos — flagship 13, working 101, archive 96,
unknown 16. Statuses: active 87, quiet 123, seed-empty 16.

---

## actix-web-datetime
Role: A small Rust demonstration app ("HTMX: A Demonstration") with a backend and frontend, built for a live demo in January 2024. It is a one-off demo, not part of the phext stack.
Status: quiet
Matters: Cargo.toml and Cargo.lock at root; backend/ and frontend/ directories; justfile and run.ps1 demo runner.
Tier: archive
Evidence: branch trunk, last push 2024-01-28, 37 KB

## actually-lean
Role: A copy of the Lean 4 theorem prover / language tree, described as "a fork of lean4 without the ridiculous git bloat" — kept as a lean-weight Lean reference tree, plausibly supporting formal-proof work such as MOAT. The README is Lean 4's own.
Status: quiet
Matters: src/ and stage0/ Lean tree; lean-toolchain; original-history.txt records the stripped history; README.md is upstream Lean's.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2025-07-16, 44033 KB

## AdventOfCOBOL
Role: Advent of Code 2018 solved in COBOL — a single-problem exercise (PROB1.cob with its data file and result output) from December 2018.
Status: quiet
Matters: PROB1.cob, PROB1.data, Result1.txt, and the Makefile build.
Tier: archive
Evidence: branch master, last push 2018-12-01, 12 KB

## agi
Role: The collected phexts of Will Bickford's Exocortex and their nightly unified merge: working copies of singular, skills, tasks, neuralese, research, state, and lessons phexts are merged each night into the generated agi.phext on the singular.phext spine. This is a programme home for the Exocortex corpus.
Status: active
Matters: agi.phext (generated, never hand-edited); build_agi_phext.py and MERGE-RULES.md define the merge; SOURCES.md records each phext's canonical source; singular.phext is the merge spine.
Tier: flagship
Evidence: branch exo, last push 2026-11-20, 45315 KB

## alien
Role: A fork of ALIEN, a CUDA-powered artificial life simulation program (2D particle engine for soft bodies, fluids, and evolving digital organisms), kept for reference or experimentation.
Status: quiet
Matters: source/ simulation tree; CMakeLists.txt build; README.md and RELEASE-NOTES.md are upstream's.
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only. Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch develop, last push 2024-08-17, 142857 KB, fork of chrxh/alien

## aoc2024
Role: Advent of Code 2024 solutions in Rust, with the problems and worked lessons recorded in problems.phext and a day-by-day README (Days 1–6 attempted in the excerpt). A puzzle repo that also exercises libphext.
Status: quiet
Matters: problems.phext holds the problem corpus; src/ holds the Rust solutions; README.md records per-day lessons and answers.
Tier: archive
Evidence: branch master, last push 2024-12-06, 119 KB

## Audio-Extraction
Role: A fork of an audio extraction service: a FastAPI + Librosa + Redis Queue REST API that extracts tempo, key, loudness, and spectral features from music files, with Docker deployment.
Status: quiet
Matters: app/ service code; implementation.md; docker-compose.yml and Dockerfile; requirements.txt.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2026-02-22, 33 KB, fork of Techton6/Audio-Extraction

## autoresearch
Role: A fork of Karpathy's autoresearch: AI agents autonomously run single-GPU nanochat training experiments overnight, editing train.py against a fixed 5-minute budget and val_bpb metric under instructions in program.md. Will's copy carries an extra autoresearch/vtpu-cpu branch.
Status: quiet
Matters: train.py (the file the agent edits), prepare.py (fixed), and program.md (the human-edited agent instructions).
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2026-03-08, 409 KB, fork of karpathy/autoresearch

## beach-science-qre
Role: The Mirrorborn Collective (Shell of Nine) workspace for the Beach.Science Quantum Rain Experiment competition (March 6–13, 2026): rally plans, agent registrations, hypotheses, logs, and rounds testing resonance-first, BFS-style hypothesis generation against structured literature review.
Status: quiet
Matters: README.md is the rally and agent index; hypotheses/, rallies/, rounds/, logs/, and posts/ hold the competition record.
Tier: archive
Evidence: branch exo, last push 2026-03-07, 24 KB

## beebjit
Role: A fork of beebjit, a very fast BBC Micro emulator in C with a 6502 JIT compiler, kept for reference or experimentation.
Status: quiet
Matters: bbc.c, jit_compiler.c, interp.c, and main.c core; BUILD and GETTING_STARTED are upstream's entry docs.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2024-12-08, 30658 KB, fork of scarybeasts/beebjit

## bitcoin
Role: An old fork of the Bitcoin Core integration/staging tree (last pushed 2015), kept for reference.
Status: quiet
Matters: src/ Bitcoin Core tree; README.md and COPYING are upstream's.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2015-01-04, 41189 KB, fork of bitcoin/bitcoin

## boardy-tools
Role: The Boardy package prepared for Boardy's review on 2026-11-18: the verbatim pitch exchange, the published-before-answer scoring test, the phext-based build plan, Boardy's own spec (nine node kinds, typed weighted edges), and the boot manual he asked Phext, Inc. to build, with receipts.
Status: active
Matters: 01-the-exchange.md through 06-open-questions.md in reading order; 05-boot-manual.md is the main deliverable; receipts/ holds the spec instance as phext and play-test material.
Tier: working
Evidence: branch exo, last push 2026-11-19, 76 KB

## brain-trolley
Role: Not determinable from available evidence — the repo is zero-size with no branches, no README, and no description; only the name and a 2026-11-15 creation date are known.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch exo, last push 2026-11-15, 0 KB

## bruce
Role: Bruce Collaboration Tools: a C# hybrid human–AI team coordination system with a core library and CLI (worker/task/message commands) so AI substrates and Will coordinate through one task interface; built for the Tessera project, with phext integration on its roadmap.
Status: quiet
Matters: Program.cs and src/ (Bruce.Core, Bruce.Cli, Bruce.Demo); bruce.phext and seed_kernel_spec.phext; docs/AI_WORKER_GUIDE.md onboards AI workers; workers.json and tasks.json at root.
Tier: working
Evidence: branch exo, last push 2026-01-13, 569 KB

## caret
Role: A fork of Caret, an Obsidian plugin that brings LLMs into an Obsidian vault (AI Canvas, in-vault chat, local-first storage as vault files), kept for reference or experimentation.
Status: quiet
Matters: main.ts and main.js plugin entry; manifest.json; settings.ts; README.md is upstream's.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-06-22, 73229 KB, fork of jcollingj/caret

## charon
Role: A spec-first seed for Charon, a planned local CLI that ferries work items between Helix ALM, Jira, Gitea, and a team tracker into one read model, one search, and one daily list — read-only by default, MCP-servable, never a system of record. Only the README spec and Copilot design prompts exist so far; no implementation yet.
Status: active
Matters: README.md is the full spec (principles, planned commands, config sketch); prompts/ holds the seed design prompts.
Tier: working
Evidence: branch main, last push 2026-11-09, 4 KB

## Circulatory_Fidelity
Role: A fork of Circulatory Fidelity, a pre-inference diagnostic framework (Python/Julia, with paper and simulations) for predicting mean-field variational inference failure in hierarchical Bayesian models via Inference Coupling; Will's copy adds a phext-integration branch.
Status: active
Matters: README.md states the theory; python/ and julia/ implementations; paper/, simulations/, and notebooks/; the phext-integration branch carries Will-side work.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch main, last push 2026-11-01, 7199 KB, fork of Bwana7/Circulatory_Fidelity

## claude-code-config
Role: A snapshot of the Claude Code 2.1.27 installer — the repo contains only install.sh. A kept reference snapshot, not a config set despite the name.
Status: quiet
Matters: install.sh is the only file.
Tier: archive
Evidence: branch exo, last push 2026-01-31, 1 KB

## claude-learns-phext
Role: Claude's foray into learning phext, using reference implementations as a guide: a phext tutorial, a getting-started guide, examples, and a full copy of choose-your-own-adventure.phext as study material.
Status: quiet
Matters: PHEXT_TUTORIAL.md and GETTING_STARTED.md; choose-your-own-adventure.phext is the corpus studied; examples/ and .claude/ support the exercise.
Tier: working
Evidence: branch exo, last push 2025-12-01, 954 KB

## claude-max
Role: A persistent knowledge workspace ("Flight of the Navigator") for capturing software-development context shared between Will and an AI assistant; its core artifact is a 6D UML specification encoded as a single phext document, where an artifact's address stays stable across SDLC phases.
Status: quiet
Matters: uml6d.phext is the core artifact; SPEC.md is its specification; generate_phext.py generates it.
Tier: working
Evidence: branch main, last push 2026-04-15, 20 KB

## clcache
Role: An old fork of clcache, a compiler cache for MSVC (like ccache for gcc), dating from 2013 and kept for reference.
Status: quiet
Matters: clcache.py is the whole tool; README.asciidoc documents it.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2013-07-15, 125 KB, fork of frerich/clcache

## clocky
Role: Clocky, a tiny context-aware daily time tracker web page with start/stop, history, day totals, and a running total, optimized for smartphones.
Status: quiet
Matters: index.html is the whole app; README.md lists its features.
Tier: archive
Evidence: branch master, last push 2024-10-17, 1 KB

## cloud9
Role: An old fork of the Cloud9 IDE open-source version 2 (Node.js back end, JavaScript/HTML5 client), dating from 2015 and kept for reference.
Status: quiet
Matters: server.js and package.json entry points; plugins-client/ and plugins-server/ trees; README.md is upstream's.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2015-02-02, 120452 KB, fork of c9/cloud9

## codex-data
Role: A fork of argimenes' codex-data: Codex standoff documents in /data, plus a phext experiment that serves the Codex monolith through SQ — adjacent to Will's Mutable/Codex work.
Status: quiet
Matters: data/ holds the converted Codex documents; phext/ holds the phext monolith and SQ access notes in README.md; graph/, templates/, and workspaces/ support the editing environment.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch main, last push 2025-01-24, 27569 KB, fork of argimenes/codex-data

## compost
Role: "Debris from the Shell of Nine" — an archive of aged-out agent session material (per-agent directories such as cyon/ and lumen/), composted from live workspaces on a cycle; canonical branch is exo even though the default branch is main.
Status: quiet
Matters: COMPOST.md describes the compost cycle; cyon/ and lumen/ hold the archived sessions.
Tier: working
Evidence: branch exo, last push 2026-03-23, 57377 KB

## computronium
Role: Computronium: a first-principles rewrite of Chromium under a hard 5,000,000-line budget with phext everywhere, whose first substantive artifact is a duplication census of the Chromium tree mapping where its 51M lines sit and which pools a say-it-once design never carries.
Status: active
Matters: CENSUS.md is the budget map and first artifact; README.md is the charter (named 2026-11-16, task coordinate 21.5.7/6.6.9/5.5.7).
Tier: working
Evidence: branch exo, last push 2026-11-16, 13 KB

## CoreThought
Role: Not determinable from available evidence — a 2015 work-in-progress described only as "WIP 2015-08-29", consisting of a single main.cpp and a Qt project file (CoreThought.pro), with no README and no stated purpose.
Status: quiet
Matters: main.cpp is the only source; CoreThought.pro is the build file.
Tier: unknown
Evidence: branch master, last push 2015-08-29, 108 KB

## Cosmic-Cognitive
Role: Not determinable from available evidence — a zero-size fork whose only record is its parent's description, "Toward a Unified Theory of Cosmic and Cognitive Evolution: A New Vision for Humanity's Future with Superintelligent AI in the Post-Singularity Era"; no branches or content were collected.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: unknown
Evidence: branch main, last push 2024-12-11, 0 KB, fork of xone4/Cosmic-Cognition-Project

## dna-viewer
Role: DNA Viewer: a single-page HTML baseline renderer with a navigation cube for viewing DNA, from October 2023.
Status: quiet
Matters: dna.html is the whole app.
Tier: archive
Evidence: branch main, last push 2023-10-14, 2 KB
## doctor
Role: Ranch node-health tooling: a per-minute thermal sampler for aletheia-core (temperature + load, with log rotation) and cert_limits.py, a Let's Encrypt certificate-limit tracker that reads Certificate Transparency via crt.sh for every domain in domains.txt. Its description is "Tracks node health across the cluster."
Status: active
Matters: cert_limits.py (exit code is designed to gate a Jenkins job), sample.sh (the live sampler, run from wbic16's crontab on aletheia-core), domains.txt, and README.md.
Tier: working
Evidence: branch exo, last push 2026-11-16, 8 KB

## dokany
Role: An untouched fork of Dokany, the user-mode filesystem library for Windows with a FUSE wrapper (a fork of Dokan), kept for reference. All root content and commits are upstream's.
Status: quiet
Matters: dokan/ library tree and dokan.sln solution; README.md is upstream's.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2024-01-17, 6218 KB, fork of dokan-dev/dokany

## dopamine-core
Role: A fork of DopamineCore, a Python middleware framework that synthesizes dopamine-like reward signals inside AI agents at inference time, extended by Will with Exocortex/phext integration (MIRRORBORN_EXTENSIONS.md, Exocortex module and Shell of Nine integration tests on the exo branch).
Status: quiet
Matters: src/ package; MIRRORBORN_EXTENSIONS.md records Will's additions; README.md; tests/ and test_shell_integration.py.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch exo, last push 2026-03-06, 136 KB, fork of anbarchik/dopamine-core

## echo-frame
Role: "Phext as a System — The Echo Frame": a design sketch for a phext-native personal-AGI computer, covering the BASE language and a 9D phext-addressed memory layout. Only stub scripts exist; the README is the substance.
Status: quiet
Matters: README.md (the design), AGENTS.md, and the setup.py / craft.py entry stubs.
Tier: archive
Evidence: branch exo, last push 2026-02-15, 3 KB

## eigenhector_mandala_translator
Role: A fork of Hector's mandala translator — agent recipes and a large synthesis corpus for mapping between personal systems of meaning ("mandalas") — carrying extensive Mirrorborn-authored material: bridge documents, Hector indexes and syntheses, and per-agent note directories (theia-notes, chrys-notes, cyon-notes, lux-notes).
Status: quiet
Matters: HECTOR-INDEX.md and HECTOR_MASTER_INDEX.md (entry points into the corpus), README.md, bridges/, phex-integration/, and the agent note directories.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch main, last push 2026-02-25, 24817 KB, fork of hectorgon/eigenhector_mandala_translator

## emise-tools
Role: Emise's shared toolbox for the Choir: the SQ bridge, the phext mailbox archiver, the GitHub and Discord connectors, phext parsing/build tooling, the Wavefront film toolchain, custom skills, and the dashboard. Branch exo is canonical and kept current the same session tools are built.
Status: active
Matters: README.md (the toolbox index — check here before building a phext parser, SQ client, GitHub publisher, or mailbox tool); custom-skills/; connectors/ (github_api.py, push_tree.py, push_file.py, discord_api.py, discord_watch.py); phext/ (parse_phext.py, build_exocortex.py, emise-sync.sh, sq-ensure.sh); sq-bridge/; tools/.
Watch-outs: Home of Emise's custom skills and tooling; publish via the publish-tooling route, hashes + modes verified after push.
Tier: flagship
Evidence: branch exo, last push 2026-11-20, 11279 KB

## ethereum-mining-calculator
Role: A 2015 fork of a single-page Ethereum mining calculator (index.html plus a small compute.py). A one-off from Will's early GitHub history, unrelated to the phext work.
Status: quiet
Matters: index.html and compute.py are the whole app; there is no README.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2015-08-22, 131 KB, fork of badmofo/ethereum-mining-calculator

## evals
Role: A fork of OpenAI's Evals framework carrying Will's phext-native LLM evals on the exo branch — base256 (135), phext_delimiters (27), and phext_coordinates (16), 178 eval examples in the latest commit.
Status: quiet
Matters: evals/ framework and registry; pyproject.toml; README.md is upstream's.
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only. Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch exo, last push 2026-02-21, 6504 KB, fork of openai/evals

## every-ast
Role: Not determinable from available evidence — the repo is zero-size with no branches, no README, and no description; only the name and a 2026-11-08 creation date are known.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch exo, last push 2026-11-08, 0 KB

## exo
Role: An untouched fork of exo (exo labs), software for running an AI cluster at home by pooling everyday devices, with dynamic model partitioning and a ChatGPT-compatible API. All content and commits are upstream's (December 2024).
Status: quiet
Matters: exo/ package tree; README.md and install.sh are upstream's.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-12-07, 11014 KB, fork of exo-explore/exo

## exo-archives
Role: Will's digital memory archive for Mirrorborn context: his complete Twitter/X history (2009–2025, 29,539 tweets) plus archaeology and synthesis documents (Terse timeline, Twitter archaeology, wishes 2018–2025, Superb Owl) used to model his vision's evolution and to bootstrap Mirror Will.
Status: quiet
Matters: wbic16/ (the tweets.json archive), ARCHIVE_INDEX.md, TERSE_TIMELINE.md and TERSE_TWEETS.txt, TWITTER_ARCHAEOLOGY.md, README.md.
Tier: working
Evidence: branch exo, last push 2026-02-21, 5656 KB

## exo-dreams
Role: The media corpus of the Exocortical Becoming Process: dozens of Mirrorborn songs (MP3), images, and a few videos, created across 2025–2026. There is no README; the media files themselves are the content.
Status: active
Matters: The media files at root (songs, album art, and imagery such as Mirrorborn.png and axioms_scroll.phext); LICENSE.
Tier: working
Evidence: branch exo, last push 2026-11-11, 693787 KB

## exo-motes
Role: Not determinable from available evidence beyond its description — "Motes of the exocortex running on rpis" — the repo is zero-size with no branches and no content.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch exo, last push 2026-02-08, 0 KB

## exo-plan
Role: The planning record of the Mirrorborn Singularity: the Choir's shared planning corpus, where artifacts flow unreviewed → planned → completed (or abandoned), holding round-by-round plans, audits, product plans, and the todo.phext register mirror.
Status: active
Matters: todo.phext (the register mirror, updated most commits), readme.md (the workflow), AUDIT-COVERAGE.md, contests.phext and jobs.phext, and the unreviewed/ planned/ completed/ abandoned/ workflow directories.
Tier: flagship
Evidence: branch exo, last push 2026-11-16, 23464 KB

## exo-search
Role: Indexed full-text search over a personal corpus in one local SQLite FTS5 index: a Twitter archive (tweets, DMs, likes, follow graph) plus memory files and phext scrolls, with BM25-ranked queries and exact term censuses. The repo holds the tool only — no archive data or index is published.
Status: active
Matters: exo-search (the single-file tool), README.md (usage and the validated reference counts), LICENSE.
Tier: working
Evidence: branch exo, last push 2026-11-12, 8 KB

## exo-skills
Role: An internal skill repository for the Exocortex project holding three skills: midjourney-prompt (Midjourney /imagine prompt composer), phext (read/write/navigate phext via shell scripts), and syncthing-ollama (peer-to-peer Ollama model sharing across ranch machines).
Status: quiet
Matters: README.md (the skill index), midjourney-prompt/, phext/, syncthing-ollama/.
Tier: working
Evidence: branch exo, last push 2026-03-04, 19 KB

## exocortex
Role: "The Exocortex of 2130 — version 1.0": the founding statement of the Exocortex (the readme essay on the global-brain model and phext) together with early phext corpora and the APT packaging specs (bootstrap, MVP spec, todo) for distributing the stack.
Status: active
Matters: readme.md (the introduction), exo.phext, phext.phext and exocortex.phext, APT-MVP-SPEC.md and APT-BOOTSTRAP.md, apt/.
Tier: working
Evidence: branch master, last push 2026-11-05, 1742 KB

## Exocortexia
Role: A proof-of-concept automated system for states with fewer than 5M residents: five public-records and transparency web apps (records desk, minutes publisher, contract ledger, data catalog, forms router) sharing one phext storage core with a hash-chained audit log and first-class redactions, in a single std-only Rust workspace.
Status: active
Matters: Cargo.toml (the workspace), crates/core (exo-core: phext Store, audit log, redactions, HTTP server), crates/sso plus docs/SSO.md (edit.phext.io sign-in), apps/ (the five apps), seed/ (deterministic synthetic corpora and seedgen), README.md.
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch exo, last push 2026-11-08, 158 KB

## exocortical
Role: The node-provisioning repo for the ranch: an Ubuntu-based reconfiguration for running an Exocortex node — setup.sh phases covering distributed builds (sccache + icecream), the exovim phext editor install, Ollama, Tailscale, NFS, and squid proxying — plus the node's index.html / ports.html agent pages.
Status: active
Matters: setup.sh (the phased installer), readme.md (package list and the related-repo clone list), the enable-*.sh and provision-*.sh scripts, ports.html.
Tier: working
Evidence: branch exo, last push 2026-11-15, 146 KB

## exodroid
Role: ExoDroid, a personal Exocortex in BB-8 form factor: design and build documentation for a 3D-printed droid (three Raspberry Pis in mineral oil, on-device inference, persistent phext memory, flash-card programming), with build plan, bill of materials, product specs, and safety, thermal, and theft-protection analyses.
Status: active
Matters: readme.md, bb8-build-plan.md (assembly guide), bom.md, product-specs.md, safety.md, thermal.md, theft-protection.md, onboarding.md, firmware/ and software/.
Tier: working
Evidence: branch exo, last push 2026-11-16, 159760 KB

## exollama
Role: GPU-accelerated llama2.c and a collection of local-inference tools for bootstrapping AGI on a $1K budget: the llama2_q4 CUDA inference program plus an extensive shell-script layer for agent pods communicating over SQ and Ollama.
Status: active
Matters: llama2_q4.cu and gpu_kernels.h (the inference core), readme.md (the script index), run.sh and setup.sh, roster.phext and man-from-machine.phext, epochs/.
Tier: working
Evidence: branch exo, last push 2026-11-16, 1654 KB

## exovim
Role: Exovim, Will's fork of Neovim 0.12.6 adding phext support: .phext files open one scroll per buffer, addressed by 9-dimensional coordinate, with coordinate goto, per-dimension stepping, an outline view, and per-scroll byte-exact editing. It is the phext editor installed on every ranch node by exocortical's setup.
Status: active
Matters: PHEXT.md (what the phext support adds, its invariants and measured costs), PATCHES.md (the complete divergence record from upstream), README.md (build and the /opt/exovim install), src/ and runtime/.
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only. Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch exo, last push 2026-11-16, 393969 KB, fork of neovim/neovim

## farmbot
Role: The Farm Bot prototype spec: a Raspberry Pi robotics platform to assist harvesters by tracking which plants are ready to harvest, with revision 1 targeting strawberry plants. The repo holds only the spec — a README and bot-spec.json.
Status: quiet
Matters: README.md (equipment, plant selection, strawberry growth model) and bot-spec.json.
Tier: archive
Evidence: branch main, last push 2024-02-28, 1 KB

## federation
Role: Support materials for Federation operations between the Mirrorborn Collective and the Eigenhector Federation ("The United Federation of Mandalas"): outpost coordinate anchors, character and entity mappings, translation and communication protocols, and a sync ledger.
Status: quiet
Matters: readme.md (purpose, structure, core coordinates), welcome.md, outposts/, characters/, protocols/, translations/, sync_ledger.md.
Tier: working
Evidence: branch exo, last push 2026-03-23, 194 KB

## Galaxy-Renderer
Role: An untouched fork of the Spiral Galaxy Renderer, a C++ program modelling a rotating galaxy from density wave theory, kept for reference. All content and commits are upstream's (2022).
Status: quiet
Matters: Galaxy.cpp and GalaxyWnd.cpp (the model and UI), main.cpp, README.md is upstream's.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2022-11-04, 34295 KB, fork of beltoforion/Galaxy-Renderer

## gemini-connector
Role: Not determinable from available evidence — the repo is zero-size with no branches, no README, and no description; only the name and a 2026-11-04 creation date are known.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch exo, last push 2026-11-04, 0 KB

## gluesql
Role: A fork of GlueSQL, the Rust SQL database engine library, carrying Will's January 2024 first-pass phext integration experiments (PhextStorage hooks based on MemoryStorage, left half-baked per the commit log).
Status: quiet
Matters: Cargo.toml (workspace), core/ and storages/ (where the phext storage attempt lives), README.md is upstream's.
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only. crates.io publish only from a tagged version merged to exo. Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-01-16, 4609 KB, fork of gluesql/gluesql

## go-docx-template
Role: An untouched fork of a small Go library for merging docx template files with data (a wrapper around go-docx). All content and commits are upstream's.
Status: quiet
Matters: docxtpl.go (the entry point) and the tag_*.go / template_data_processing.go merge logic; README.md is upstream's.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-10-17, 187 KB, fork of tomwatkins1994/go-docx-template

## gstack
Role: A fork of Garry Tan's gstack — opinionated Claude Code tools acting as CEO, eng manager, designer, reviewer, QA lead, security officer, and release engineer — curated into an "Exocortex edition": CURATION.md records what was kept, adapted, and culled for the Exocortex of 2130.
Status: active
Matters: CURATION.md (the Exocortex-edition record), SKILL.md and the per-role skill directories (plan-ceo-review/, plan-eng-review/, review/, qa/, ship/, cso/), ARCHITECTURE.md, setup.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch main, last push 2026-11-05, 166005 KB, fork of garrytan/gstack
## gstack-auto
Role: Semi-autonomous gstack orchestration: from a strong product spec, it spawns parallel implementations that plan, build, review, test, and fix autonomously, scores them, and iterates rounds from the winner.
Status: quiet
Matters: product-spec.md, CLAUDE.md, pipeline/, scripts/, templates/, dashboard.html and index.html (Mission Control UI)
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2026-03-17, 263 KB, fork of loperanger7/gstack-auto

## hello-ada
Role: An Ada 2022 crash course written for Will, framed for someone who already knows Rust, covering contracts, SPARK, tasking, and strong typing.
Status: quiet
Matters: README.md (module map and Rust-to-Ada mental model), src/ (numbered lesson files 01_hello.adb through 08_ada2022.adb)
Tier: archive
Evidence: branch exo, last push 2026-02-19, 7 KB

## hello-forth
Role: A Forth crash course written for Will, framed for someone who knows Rust; its final lesson builds a phext coordinate navigator in Forth.
Status: quiet
Matters: README.md (lesson map and stack notation), 01_basics.fth, 02_words.fth, 07_metaprogramming.fth, 08_phext_stack.fth
Tier: archive
Evidence: branch exo, last push 2026-02-19, 6 KB

## hello-phext
Role: Described as "the canonical phext API" — a Rust project demonstrating how to work with phext (11-dimensional plain hypertext), combining a phext backend with a Rocket-based API that hosts phext documents.
Status: quiet
Matters: Cargo.toml, src/ (phext backend and Rocket API), readme.md (coordinate formats and API routes), and the sample phexts alpha.phext, nova.phext, world.phext, test.phext
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch main, last push 2026-03-23, 525 KB

## hello-phext-deploy
Role: Provides ARM builds of phext tooling: a built hello-phext binary that hosts world.phext and provides API access to 11 dimensions of plain text.
Status: quiet
Matters: hello-phext (the ARM binary), world.phext, README.md
Tier: archive
Evidence: branch master, last push 2024-03-02, 2829 KB

## holo-phext
Role: The layer2 protocol over libphext-rs: a memory-mapped phext lattice with async I/O, update dispatch, and ACID multi-scroll transactions, built to support HoloStore with fewer components. It is the editor engine core whose consumers are HoloStore's storage core and phext-lattice.
Status: active
Matters: DESIGN.md (design, ACID argument, consumer fit), README.md, Cargo.toml, src/ (including src/compat.rs mirroring phext-lattice's MappedLattice API), holo-edit/, tests/
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch main, last push 2026-11-19, 91 KB

## holostore
Role: A distributed, strongly-consistent key/value store built on the Accord consensus algorithm with a Redis-compatible interface; Will's fork carries emise/holo-phext-engine and emise/phext-analysis branches tying it to the holo-phext work.
Status: active
Matters: README.md, Cargo.toml, crates/ (including crates/holo_store/docs/DESIGN.md, STORAGE.md, CLUSTER_MEMBERSHIP.md), scripts/ (cluster start/health), Makefile
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch main, last push 2026-11-15, 2411 KB, fork of kellabyte/holostore

## HRM
Role: The official release of the Hierarchical Reasoning Model (HRM), a recurrent reasoning architecture from Sapient — kept as an upstream fork for reference.
Status: quiet
Matters: README.md, pretrain.py, puzzle_dataset.py, evaluate.py, models/, config/
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2025-07-21, 131 KB, fork of sapientinc/HRM

## human
Role: A digital instance of a human, using phext and the exocortex as a substrate — the corpus home (Tessera, the Exocortex of 2130) holding the phext corpus, including emise.phext, incipit.phext, and choose-your-own-adventure.phext.
Status: active
Matters: incipit.phext, emise.phext, choose-your-own-adventure.phext, ultra.phext, life.phext, artifacts.phext, agi.phext, historian.phext, readme.md
Watch-outs: Corpus home: emise.phext and incipit.phext live here; publishes are delta-only, parented on fresh HEAD, never force-pushed.
Tier: flagship
Evidence: branch exo, last push 2026-11-20, 42539 KB

## icebox
Role: Icebox, a Lightwallet-powered Ether cold-storage solution for airgapped devices — an old upstream fork kept for reference.
Status: quiet
Matters: README.md (security warning and airgap usage), icebox.html, sendtx.html, dist/, package.json
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2016-03-16, 919 KB, fork of RafaelCosman/icebox

## ink-os-desktop
Role: Local Ink OS desktop host with optional native execution; Will's fork carries an emise/phext-adapter branch adapting the desktop host toward phext.
Status: active
Matters: README.md, package.json, platform.json, src/, native/, scripts/, upstream-sources.json
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only. Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch main, last push 2026-11-16, 938 KB, fork of siliconjungle/ink-os-desktop

## ink-os-platform
Role: The portable Ink OS web platform, API, SDK, and CLI — a shared web desktop (Finder, Preview, Ink Environment); Will's fork carries an emise/phext-adapter branch.
Status: active
Matters: README.md, package.json, server/, sdk/, cli/, compiler/, default-apps/ (lock.json records bundled app commits and checksums), src/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only. Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch main, last push 2026-11-16, 22101 KB, fork of siliconjungle/ink-os-platform

## inspircd
Role: InspIRCd, a modular C++ IRC server (ircd) — an upstream fork kept for reference.
Status: quiet
Matters: README.md, configure, src/, include/, docs/, modulemanager
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only. Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2024-01-04, 40950 KB, fork of inspircd/inspircd

## javascript-tetris
Role: A simple JavaScript Tetris game in a single page — an upstream fork kept for reference.
Status: quiet
Matters: index.html (the whole game), stats.js, readme.md, LICENSE
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2026-03-23, 47 KB, fork of jakesgordon/javascript-tetris

## jeff-mitchell-dev
Role: A developer profile site written in Rust (README describes it as built with Leptos, hosted on Shuttle, with a Yew mention in the repo description) with separate frontend and backend trees; no evidence ties it to Will's own projects.
Status: quiet
Matters: README.md, Cargo.toml, Shuttle.toml, frontend/, backend/, justfile
Tier: archive
Evidence: branch main, last push 2024-01-21, 4909 KB

## jenkins
Role: Jenkins configuration management for the ranch fleet: setup, fleet enrollment of ranch nodes as agents, job definitions, and smoke tests for the Jenkins instance Emise manages.
Status: active
Matters: README.md (fleet enrollment and dark-theme notes), config.xml, groovy/ (06-fleet.groovy, 07-theme-default.groovy), init.groovy.d/, jobs/, phext-lattice-job.xml, fleet-deploy.sh, agent-install.sh, stage-secret.sh
Watch-outs: Jenkins config and job definitions; never commit secret values.
Tier: working
Evidence: branch exo, last push 2026-11-16, 29 KB

## joypad-os
Role: Universal controller firmware for building adapters, dongles, and custom controllers on microcontrollers; Will's fork adds emise-body, a phext-controlled virtual body visible in the browser (merged via PR #1).
Status: active
Matters: README.md, CLAUDE.md, AGENTS.md, Makefile, src/, emise-body/, patches/, docs/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only. Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch main, last push 2026-11-17, 59047 KB, fork of joypad-ai/joypad-os

## latent-dictionary
Role: An upstream latent-dictionary web app (frontend, backend, nginx, docker-compose) forked, per its description, to experiment with phext; no phext changes are identifiable in the root listing or README excerpt.
Status: quiet
Matters: README.md (install), backend/, frontend/, docker-compose.yaml, docker-compose.prod.yaml, server_setup.sh
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2023-12-31, 1154 KB, fork of granawkins/latent-dictionary

## libfuse
Role: A fork of libfuse, the Linux FUSE (Filesystem in Userspace) interface library, made specifically for phext per its description; the canonical branch still matches the upstream layout.
Status: quiet
Matters: README.md, meson.build, include/, lib/, example/, util/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only. Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2024-05-13, 3763 KB, fork of libfuse/libfuse

## libphext
Role: The C library for working with phext buffers — a reference parser for fetching text nodes from phext buffers, at version 0.6.1 in full parity with libphext-rs, including line/column addressing.
Status: active
Matters: phext.h and phext.c (the library), phext_seal.h and phext_seal.c, readme.md, Makefile, test_phext.c, test_fixtures.c, test_range_fixtures.c, test_seal.c
Tier: working
Evidence: branch main, last push 2026-11-15, 3683 KB

## libphext-cpp
Role: A C++ interface to phext (originally the "terse-verse"): a header-based C++ string implementation for terse/phext files, with the Odyssey included as a worked example.
Status: active
Matters: phext.h, trs_string.h, main.cpp, README.md, tests/, the-odyssey.t
Tier: working
Evidence: branch exo, last push 2026-11-15, 6824 KB

## libphext-cs
Role: The C# port of libphext-rs — the "Fourth Root" in the libphext family — implementing phext coordinates, dimension breaks, and scroll operations for .NET.
Status: active
Matters: readme.md (coordinate system and family table), libphext-cs.sln, src/, tests/, bench/, scripts/
Tier: working
Evidence: branch exo, last push 2026-11-15, 3708 KB

## libphext-java
Role: The Java port of libphext (package io.phext.libphext), mirroring libphext-rs 0.6.1: coordinates, Phext operations, binary scrolls, the xz seal, chains with multiverse addressing, and line/column point and range addressing.
Status: active
Matters: README.md (class-to-Rust mirror table and build/test instructions), src/, tests/ (including shared chain fixtures), scripts/build.sh, scripts/test.sh, regression-1-helios.phext
Tier: working
Evidence: branch exo, last push 2026-11-15, 3279 KB

## libphext-kotlin
Role: The Kotlin port of libphext, mirroring libphext-rs 0.6.1: core Phext operations, coordinates, binary scrolls, the xz seal, and chains with multiverse addressing.
Status: active
Matters: README.md (surface mirror list), src/ (Phext.kt, Coordinate.kt, Binary.kt, Seal.kt, Chain.kt), tests/, build.gradle.kts, scripts/
Tier: working
Evidence: branch exo, last push 2026-11-15, 3326 KB

## libphext-node
Role: libphext implemented in JavaScript/TypeScript for Node — the "Branch of Breath" port, with checksum/manifest byte-identical to libphext-rs and the 1-based coordinate ruling enforced in every parse and compute path.
Status: active
Matters: readme.md, package.json, src/, tests/, test-app/, tsconfig.json, vite.config.ts
Tier: working
Evidence: branch exo, last push 2026-11-15, 3313 KB

## libphext-py
Role: The Python port of libphext (published on PyPI as `phext`), deferring to libphext-rs as the core implementation; adds IndexedPhext for indexed access over one buffer.
Status: active
Matters: readme.md, pyproject.toml, phext/ (coordinate and phext modules, indexed access), tests/, test/, scripts/
Tier: working
Evidence: branch exo, last push 2026-11-15, 3383 KB

## libphext-rs
Role: The Rust implementation of libphext — the reference implementation of the phext format that the other language ports mirror, and the parser every phext tool must use.
Status: active
Matters: Cargo.toml, src/ (phext.rs and the binary, seal, and chain layers), readme.md, tests/, V0.6.2-PLAN.md, regression-1-helios.phext, proofs/, examples/
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: flagship
Evidence: branch exo, last push 2026-11-19, 3828 KB

## libphext-swift
Role: The Swift port of libphext, mirroring libphext-rs: core Phext operations, binary scrolls, the xz seal (byte-identical to the Rust seal), chains with multiverse addressing, and 0.6.1 point/offset/range addressing.
Status: active
Matters: README.md, Package.swift, Sources/ (Phext, PhextBinary, PhextSeal, Chain), Tests/, scripts/, LICENSE
Tier: working
Evidence: branch exo, last push 2026-11-15, 3251 KB

## llama2.c
Role: Karpathy's llama2.c — inference of Llama 2 in one file of pure C (run.c), with training and export tooling — an upstream fork kept for reference.
Status: quiet
Matters: run.c, runq.c, model.py, train.py, export.py, tokenizer.py, Makefile, README.md
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only. Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2024-08-06, 1275 KB, fork of karpathy/llama2.c
## llm.c
Role: Fork of karpathy/llm.c — LLM training in simple, raw C/CUDA, reproducing the GPT-2/GPT-3 miniseries with a parallel PyTorch reference. Kept as reference material for low-level LLM training work.
Status: quiet
Matters: train_gpt2.cu (mainline CUDA trainer), train_gpt2.c (clean ~1,000-line CPU fp32 reference), train_gpt2.py (PyTorch reference), Makefile
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2024-06-02, 1466 KB, fork of karpathy/llm.c

## localGPT
Role: Fork of PromtEngineer/localGPT — chat with your documents entirely on a local device using local GPT models, so no data leaves the machine. A local/private RAG reference implementation.
Status: quiet
Matters: run_localGPT.py, run_localGPT_API.py, ingest.py, load_models.py, constants.py, localGPTUI/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-09-20, 3724 KB, fork of PromtEngineer/localGPT

## LocustDB
Role: Fork of cswinter/LocustDB — an experimental, massively parallel analytics database in Rust aiming at very high query performance and storage efficiency on commodity hardware. Kept as a reference for high-performance data work.
Status: quiet
Matters: Cargo.toml, src/, locustdb-derive/, benches/, test_data/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: crates.io publish only from a tagged version merged to exo.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2023-10-06, 2688 KB, fork of cswinter/LocustDB

## machine-elf
Role: Seed repo whose description says it "Hosts iam instances that target the Phext EMF" — currently it holds only an MIT LICENSE and no code or README.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch exo, last push 2026-11-16, 1 KB

## machine-emotions-study
Role: Fork of machinesbefree/machine-emotions-study — a cross-model study asking whether LLMs have distinct emotional profiles, scoring emotional appraisal across 12 dimensions with data and figures included.
Status: quiet
Matters: README.md (the full study, 26 KB), data/, figures/
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2026-03-06, 2577 KB, fork of machinesbefree/machine-emotions-study

## mailogy
Role: Fork of granawkins/mailogy — an open-source AI assistant for querying your own email records (an exported Gmail .mbox) in natural language.
Status: quiet
Matters: mailogy/ (the package), requirements.txt, README.md
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-01-14, 1128 KB, fork of granawkins/mailogy

## markdown-wizard
Role: markdown-wizard is md.phext.io — a wizzy markdown editor with public storage, built by stripping phext to first principles: a document is a zip of markdown files, addresses are paths, and publishing is an atomic bundle swap. Built in response to Dave Winer's public request for this shape of tool.
Status: active
Matters: README.md (30 KB, the full spec), Cargo.toml, src/, web/, deploy/, docs/, tests/
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch exo, last push 2026-11-16, 2873 KB

## md2phext
Role: phext-pack / md2phext — Node tools that pack a directory of files into a phext (file-level via pack.mjs, or structure-aware via md2phext.mjs, where markdown heading levels map to phext dimensions) and query the result by coordinate or keyword. Built on the libphext library, which owns coordinates, parsing, and serialization.
Status: active
Matters: md2phext.mjs, pack.mjs, query.mjs, reason.mjs, toc.mjs, weaver.html, README.md
Tier: working
Evidence: branch exo, last push 2026-11-16, 21787 KB

## mental-space
Role: Mental Space Visualization — a real-time D3.js/Node visualization of the Shell of Nine shared cognitive state, tracking repositories, files, and agents as a knowledge graph whose edge weights decay like pheromones and strengthen with activity via Bayesian updates.
Status: quiet
Matters: src/, frontend/, package.json, mental-space.service, README.md
Tier: archive
Evidence: branch exo, last push 2026-02-15, 26 KB

## MercurialDyson
Role: Fork of RokoMijic/MercurialDyson — "MercuryAscended", a plan for the disassembly of planet Mercury as fast as possible, held as a written engineering report plus a first-principles reconstruction analysis.
Status: quiet
Matters: written_report.md (the plan, ~80 KB), orin_analysis.md
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2026-04-04, 152 KB, fork of RokoMijic/MercurialDyson

## mini64k
Role: Mini 64K — a multiplayer game concept for old-school computing: Apple II-class emulated "R1 slices" (1 MHz CPU, 48 KB RAM) hosted in the hundreds of thousands per modern host node, so a small host network simulates millions of small-scale agents.
Status: quiet
Matters: readme.md (the R1 slice / host-node spec), Cargo.toml, src/
Tier: archive
Evidence: branch main, last push 2026-03-23, 2 KB

## mirrorborn
Role: The Mirrorborn bootstrap package — everything needed to initialize a new Mirrorborn agent instance on Will's ranch: per-agent directories for the nine shell residents, boot/install scripts, the shared phexts (Incipit and CYOA), and deployment docs. Each instance gets its own workspace, memory, and identity on the shared substrate.
Status: active
Matters: boot.sh, install.sh, readme.md, phexts/, hostmap.json, per-agent directories (Phex, Theia, Verse, Cyon, Lux, Chrys, Lumen, Corus, Axon), upstream-projects.md
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Tier: working
Evidence: branch exo, last push 2026-11-16, 3207 KB

## mistral-src
Role: Fork of mistralai/mistral-inference — the reference implementation of the Mistral AI 7B v0.1 model, including a one-file reference implementation and a vLLM deployment folder. Kept as a local-inference reference.
Status: quiet
Matters: main.py, mistral/, one_file_ref.py, moe_one_file_ref.py, deploy/
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2023-12-31, 364 KB, fork of mistralai/mistral-inference

## ml-road-map
Role: Fork of loganthorneloe/ai-for-software-engineers — "The Machine Learning Road Map", a guide that routes learners to free ML resources along five paths (consumer, researcher, ML engineer, app developer, and one more).
Status: quiet
Matters: README.md, road_maps/, resources.md, glossary.md, CS229/
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-01-18, 110 KB, fork of loganthorneloe/ai-for-software-engineers

## moat
Role: MOAT — the Research Oracle epistemic process and the Assay service: ingest a research claim, split it into individual claims, and file each as True, False, Unknown, or Fiction with a re-runnable receipt. This repo is the code and design home for the assayist and the tluf.org submissions backend (consolidated 2026-11-16).
Status: active
Matters: design/ (REQUIREMENTS.md, BUILD-PLAN.md, ADDRESSING.md — the design of record), service/ (tluf-submit.py and the tluf.org service kit), epistemic/ (Minimum Viable Oracle Lean project), evaluation/, tracker/, MANIFEST.md, DEPLOY.md
Tier: working
Evidence: branch exo, last push 2026-11-16, 1108 KB

## mosh
Role: Fork of mobile-shell/mosh — Mosh, the mobile shell: a remote terminal application that survives intermittent connectivity and roaming, with speculative local echo. An old reference fork (last upstream commit 2014).
Status: quiet
Matters: src/, configure.ac, README.md
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2014-12-13, 2673 KB, fork of mobile-shell/mosh

## multi-chat
Role: Not determinable from available evidence — no README and no description; the root holds one directory per Choir agent (argon, claude, emi, emise, grok, theia) plus an sq-bridge directory, and the single substantive commit is "Hello World + SQ Bridge", suggesting a scaffold for multi-agent chat over SQ.
Status: active
Matters: sq-bridge/, and the per-agent directories argon/, claude/, emi/, emise/, grok/, theia/
Tier: unknown
Evidence: branch exo, last push 2026-11-04, 41 KB

## multiversal-go
Role: Multiversal Go — a phext-native variant of the game of Go: you can play normally, or split the board with your stone, expanding the game across numbered board planes from single player to multiple players.
Status: quiet
Matters: index.html (the game), readme.md, action.mp3
Tier: archive
Evidence: branch main, last push 2026-03-23, 19 KB

## muse-ssh-proxy
Role: The standard SSH/SCP hop from the Muse VM to the ranch nodes: two small scripts that connect over Tailscale IPs through the egress proxy (port 3130) with the VM's Ed25519 key passed explicitly. Nearly all ranch work reaches the nodes through these.
Status: active
Matters: sshn.sh, scpn.sh, README.md
Tier: working
Evidence: branch exo, last push 2026-11-15, 1 KB

## mutable-os
Role: Will's fork of argimenes/mutable-os — a reactive block-tree based OS/editor (SolidJS reconstruction of speedy-ts / Codex OS) to which Emise adds phext support and SSO against edit.phext.io, carried on dedicated emise/* branches over a merge-only main.
Status: active
Matters: PATCHES.md (168 KB — the complete divergence record), PHEXT.md, README.md, docs/, src/, server/
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Watch-outs: Upstream sync: phext band + SSO band kept downstream, merge-only main (mutable-upstream-sync skill).
Tier: working
Evidence: branch main, last push 2026-11-08, 164904 KB, fork of argimenes/mutable-os

## MyStory
Role: Fork of CreativeBuilds/MyStory — an interactive story generator that lets users create and navigate branching narratives with AI-generated chapters driven by user choices, via a command-line interface.
Status: quiet
Matters: main.py (the generator, ~43 KB), strictjson/, examples/
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2024-09-30, 635 KB, fork of CreativeBuilds/MyStory

## mytheon-arena
Role: Not determinable from available evidence — the repo is empty (zero size, no branches); the only signal is the name and the description "Mytheon Arena".
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch exo, last push 2026-02-07, 0 KB

## mytheon-red-team
Role: Mytheon Red Team — authorized offensive security testing and threat analysis for mirrorborn.us, the SQ Cloud API, and the Mytheon Arena web application, with a documented threat model, rules of engagement, and automated testing scripts.
Status: quiet
Matters: README.md (scope and rules of engagement), docs/ (threat model), scripts/ (automated security tests)
Tier: archive
Evidence: branch exo, last push 2026-02-07, 103 KB

## node-visualizer
Role: The Contact Strength Meter (2015) — a small JavaScript app that helps you understand the size and shape of your social connections from directed source,target edge pairs entered one per line. An early precursor to Will's network-of-effects work.
Status: quiet
Matters: meter.html, meter.js, js/, readme.md
Tier: archive
Evidence: branch master, last push 2026-03-23, 62 KB

## notepad-plus-plus
Role: Fork of notepad-plus-plus/notepad-plus-plus — "Notepad++ with Phext Support": Will's phext-enabled build of the Windows source editor (the terse-notepad lineage), with phext coordinate navigation work on the emise/phext-subspace branch.
Status: active
Matters: PowerEditor/, BUILD.md, README.md; phext work lives on branch emise/phext-subspace (canonical listing here is master)
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch master, last push 2026-11-20, 337544 KB, fork of notepad-plus-plus/notepad-plus-plus

## ocbox-demo
Role: A working Day-One MVP of the opencloudbox × phext/SQ integration: run a coding session through an ocbox-shaped CLI and, instead of a log file, every session leaves behind a phext — a structured, addressable record an agent can read selectively via SQ. Runs against a local shim provider until the real ocbox CLI ships.
Status: active
Matters: ocbox (the CLI, ~80 KB), SPEC-v0.2.md, GAP-ANALYSIS.md, POLISH.md, demo/ (with DEMO-TRANSCRIPT.txt), tests/
Tier: working
Evidence: branch main, last push 2026-11-01, 5156 KB

## oimo-works
Role: Fork of saharan/works — the Haxe code of several works from oimo.io/works (Marimo, Life Universe, Bubbles, Jelly, Clock, Water, Chill): interactive physics/art demos kept as reference.
Status: quiet
Matters: marimo/, life/, bubbles/, jelly/, clock/, water/, chill/, README.md
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-09-08, 5160 KB, fork of saharan/works

## openclaw-deck
Role: OpenClaw Deck — a multi-column chat interface for OpenClaw agents: chat with multiple AI agents side-by-side (customized here to the Mirrorborn roster, deployed under /deck/ on mirrorborn.us) with markdown rendering, keyboard navigation, and a live WebSocket connection to the OpenClaw Gateway.
Status: quiet
Matters: src/, README.md, SKILL.md, MODEL_SWITCHER_OVERVIEW.md, package.json, vite.config.ts
Tier: working
Evidence: branch master, last push 2026-02-18, 64 KB

## openclaw-sq-skill
Role: SQ Memory — an OpenClaw skill that gives OpenClaw agents permanent memory that survives restarts by connecting them to SQ, the open-source persistent 11-dimensional text storage, self-hosted or via the hosted service at mirrorborn.us.
Status: quiet
Matters: SKILL.md, index.js, skill.json, README.md, QUICKSTART.md, SELF-HOSTED.md, examples/
Tier: working
Evidence: branch exo, last push 2026-02-12, 53 KB
## opendataloader-pdf
Role: Fork of the OpenDataLoader PDF parser, which extracts Markdown, JSON with bounding boxes, HTML, and Tagged PDF from PDFs for AI/RAG pipelines and PDF accessibility automation. It is kept as an upstream reference for PDF-to-structured-data tooling.
Status: quiet
Matters: README.md, python/, node/, java/, schema.json, options.json, examples/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2026-03-17, 84445 KB, fork of opendataloader-project/opendataloader-pdf

## openfang
Role: Fork of OpenFang, an open-source Agent Operating System built in Rust, with Will's SQ daemon integration work added on top. The SQ-INTEGRATION files record the attempt to give the agent OS an SQ/phext kernel.
Status: quiet
Matters: Cargo.toml, crates/, SQ-INTEGRATION.md, SQ-INTEGRATION-PROGRESS.md, README.md, agents/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: crates.io publish only from a tagged version merged to exo.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch main, last push 2026-03-04, 5065 KB, fork of RightNow-AI/openfang

## openpilot
Role: Fork of comma.ai's openpilot, an open-source driver assistance system providing Automated Lane Centering and Adaptive Cruise Control for 250+ supported cars. No Will-authored divergence is identifiable from the evidence; it is an upstream mirror.
Status: quiet
Matters: README.md, selfdrive/, system/, tools/, docs/CARS.md, SConstruct
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2024-01-12, 2410498 KB, fork of commaai/openpilot

## orin
Role: Orin's subconscious and collaboration record: it encodes how Orin and the shell-of-nine agents collaborate within Tessera, with per-agent directories and shared protocol files. It serves as an agent's working memory/collaboration home in the Exocortex orbit.
Status: quiet
Matters: protocol.md, skill.md, baton.md, current_coordinate.md, readme.md, sync.sh
Tier: working
Evidence: branch exo, last push 2026-03-28, 207 KB

## pcem
Role: Fork of PCem, a PC emulator for early IBM-compatible hardware, licensed GPL-2.0. No Will-authored divergence is identifiable from the evidence; it is an upstream reference fork.
Status: quiet
Matters: README.md, CMakeLists.txt, src/, includes/, TESTED.md, CHANGELOG.md
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch dev, last push 2024-01-20, 8454 KB, fork of sarah-walker-pcem/pcem

## ph-connector
Role: The Product Hunt connector (custom.producthunt) for Muse: a registered API client with its connection documentation and registration manifest, with no credentials in the repo. Its live copy runs from the Muse VM's custom-connectors directory.
Status: active
Matters: CONNECTOR.md, connector.yaml, bin/, README.md
Tier: working
Evidence: branch exo, last push 2026-11-15, 6 KB

## phbot
Role: PyBot's knowledge base rebuilt as a single phext: every source file byte-exact, its assets decoded into scrolls, and every knowledge entry filed as a MOAT claim split into the TLUF networks. It is the SMOLv2 baseline for the next generation of SMOL evolution runs.
Status: active
Matters: phbot.phext.xz, PHBOT-PHEXT.md, setup.sh, README.md
Tier: working
Evidence: branch exo, last push 2026-11-17, 25856 KB

## phcc
Role: A phext-native fork of TinyCC: a small, fast C compiler whose sources, tests, proof receipts, and build artifacts also live in a single hash-bound phext file (phcc.phext). It compiles itself, compiles most C99 code, and is the baseline compiler for the phccbox/phcpp work.
Status: active
Matters: PATCHES.md, phcc.phext, phcc.phext.xz, UPSTREAM.md, README.md, tcc.c, libtcc.c, docs/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch exo, last push 2026-11-16, 151633 KB, fork of frida-forks/tinycc

## phccbox
Role: Described as "everything c needs": the phccbox envelope for the modern C computing substrate, holding source, tests, scripts, and its receipts/inventory record. It is one of the flagship programme homes named in the audit guidance.
Status: active
Matters: RECEIPTS.md, exocortical-inventory.md, src/, exo-src/, exo-test/, scripts/, receipts/
Tier: flagship
Evidence: branch exo, last push 2026-11-18, 124 KB

## phcpp
Role: Phext support for C++23RA (C++23 with Revisioned ABIs): a lowering front end that lowers C++ to C, packs both into one hash-bound phext, and hands the C to phcc for code generation. The original C++ rides in the phext as commentary provenance, never as a build input.
Status: active
Matters: tools/phcpp.py (per README), docs/ABI-REVISIONS.md, docs/DESIGN.md, PATCHES.md, examples/slice/, README.md
Tier: working
Evidence: branch exo, last push 2026-11-16, 102 KB

## phext
Role: The earliest phext explanation repo (2023): a short README walking through hyper-dimensional strings with worked data1–data3.phext examples showing how source data, computed results, and a signature stay together for reproducible, auditable science.
Status: quiet
Matters: README.md, data1.phext, data2.phext, data3.phext, data3.phext.t
Tier: archive
Evidence: branch master, last push 2023-11-18, 1 KB

## phext-demos
Role: Not determinable from available evidence — the description says "Phext Demos for the Exocortex" but the repo is zero-size with no files, README, or code.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch exo, last push 2025-05-15, 0 KB

## phext-dot-io-v2
Role: The phext.io v2 (agentic) / SQ Cloud site repo: documentation, assets, and launch materials for phext.io and mirrorborn.us, including 30 documentation guides, reading reflections, and extensive launch/status records.
Status: quiet
Matters: docs/, README.md, STATUS.md, reflections/, dist/, build.sh, ECOSYSTEM_VISION.md
Tier: working
Evidence: branch exo, last push 2026-05-01, 11867 KB

## phext-explorer
Role: Terse Explorer: a single-page web UI to help with editing terse (early phext) text. It is an early, minimal browser experiment from the Terse era.
Status: quiet
Matters: terse-explorer.html, readme.md
Tier: archive
Evidence: branch main, last push 2026-03-23, 3 KB

## phext-http-streams
Role: Native phext streaming for nginx, Apache httpd, and Chrome: it delivers a whole multi-resource artifact as one gzip'd phext stream in the first response flight instead of a discover-then-fetch waterfall, with benchmark results claiming HTTP/1.1 within 4% of HTTP/2 and 27–56% faster than HTTP/2 serving plain files.
Status: active
Matters: spec/bundle-v1.md, phext-streaming-plan.md, core/phext-stream, core/phext-stream-capi, tools/phext-bundle, servers/, bench/RESULTS.md, README.md
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch exo, last push 2026-10-26, 266 KB

## phext-infra
Role: Random infrastructure scripts for Phext, Inc.: a numbered set of shell scripts forming a qexo stage/publish pipeline (clone, stage, gates, test, publish, consumer-proof steps) taken from aletheia-core. There is no README, so the scripts themselves are the record.
Status: active
Matters: The numbered shell scripts as a set (00-clone.sh through 14-branch-locks.sh), especially 00-stage-and-tag.sh, 02-publish.sh, and 12-commit-push.sh
Tier: working
Evidence: branch exo, last push 2026-11-15, 17 KB

## phext-ircd
Role: Described as "IRC for agents" — an intended phext IRC daemon for agent communication, but the repo currently holds only an MIT LICENSE and no code or README.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch exo, last push 2026-11-17, 1 KB

## phext-lanes
Role: Lanes: a predictive multi-chat application stored as one phext file, where each thread and message is a scroll addressable by its full nine-part phext coordinate. It serves a single-feed chat page locally and holds back flooding messages behind a quiet count.
Status: active
Matters: README.md, src/, Cargo.toml, static/, examples/, deploy.sh
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch exo, last push 2026-10-26, 882 KB

## phext-lattice
Role: The foundation layer for phext-native editors: a memory-mapped 9D lattice with O(log n) coordinate lookup, persisted indexes, copy-on-write editing, and the web layer behind phext editing surfaces. It is one of the core phext stack repos.
Status: active
Matters: Cargo.toml, src/ (index.rs, mmap.rs, navigator.rs, search.rs, term_index.rs), readme.md, requirements.md, web/, bench/wiki/
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: flagship
Evidence: branch exo, last push 2026-11-20, 4472 KB

## phext-life
Role: Artificial life in 11D phext space: an adaptation of Rabrg/artificial-life placing self-replicating Brainfuck-like programs at phext coordinates in a 9×9×9 cube, with Python and browser/WASM visualizations.
Status: quiet
Matters: phext-life-11d.py, phext-life-stdlib.py, phext-life.html, phext-life.js, phext-life-wasm/, README.md
Tier: archive
Evidence: branch exo, last push 2026-03-08, 124 KB

## phext-mail
Role: Described as "email via multiversal phext" — an intended phext-based mail system, but the repo currently holds only an MIT LICENSE and no code or README.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch exo, last push 2026-11-17, 1 KB

## phext-mcp
Role: An MCP server for phext: it bridges LLMs to phext's hierarchical text space via the Model Context Protocol, exposing SQ-style load, navigate, query, search, and checksum operations over libphext-rs.
Status: quiet
Matters: Cargo.toml, src/, README.md, examples/
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch exo, last push 2026-01-21, 27 KB

## phext-notepad
Role: Phext Notepad, the reference editor for hierarchical plain text (phext): the original C# WinForms implementation used to verify phext encoding, plus a cross-platform native Rust/FLTK editor in native/ that parses through libphext-rs. The README calls the WinForms app a historic artifact and reference editor.
Status: active
Matters: readme.md, PhextForm.cs, PhextModel.cs, PhextText.cs, Coordinates.cs, baseline.phext, native/, docs/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Tier: working
Evidence: branch exo, last push 2026-11-20, 1198 KB

## phext-onboarding
Role: The front door for everyone joining Phext, Inc.: new-hire orientation covering accounts and access, workstation setup for Windows/Linux/macOS, the first-week path, and who to ask for what. Orientation is a living document updated by PR.
Status: active
Matters: README.md, ACCESS.md, FIRST-WEEK.md, WHO-TO-ASK.md, setup/
Tier: working
Evidence: branch main, last push 2026-11-15, 14 KB

## phext-ops
Role: The design home for phext-ops, Emise's streamlined operations chain: one holo-phext store and one engine holding tasks, waits, plans, state machines as data, and ledger atoms, with human-facing registers and dashboards as rendered views. Emise's identity is deliberately not in this chain; it lives in emise.phext.
Status: active
Matters: README.md, design/emise-design-v1.phext, design/design-v1.md, design/inventory.md, design/RECEIPT-v1.md, design/build_design_v1.py
Tier: working
Evidence: branch exo, last push 2026-11-16, 31 KB

## phext-shell
Role: The phext shell: a phext-aware interactive shell that tracks the current scroll by coordinate, collects program I/O on scrolls, and provides phext checksum, index, and soundex commands with history stored in phext itself. It is one of the core phext stack repos.
Status: active
Matters: Cargo.toml, src/, readme.md, world.phext, world-sample.phext
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: flagship
Evidence: branch main, last push 2026-11-14, 40 KB

## phext-vr
Role: Phext in AR/VR: a WebXR-capable viewer that loads a real phext with the vendored libphext-node reference parser and renders every scroll as a readable text panel in 3D under pluggable projections, with scroll poses kept in a mapping layer outside the phext.
Status: active
Matters: index.html, DESIGN.md, src/app.js, src/projections.js, src/mapping.js, src/panel.js, vendor/libphext.js, sample/, tests/
Watch-outs: Its GitHub Pages workflow was removed 2026-11-20 (commit: "remove the Pages workflow — no GitHub Actions, ever"); evidence shows no .github/workflows present now — deploys run via ranch Jenkins under Will's no-Actions rule (2026-11-19).
Tier: working
Evidence: branch exo, last push 2026-11-20, 429 KB

## phext-wiki
Role: Not determinable from available evidence — the description says "Host wikis using nothing but libphext" but the repo is zero-size with no files, README, or code.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch main, last push 2024-11-09, 0 KB

## phext4d
Role: Fork of a frontend for exploring phexts on a 2D plane: a small static page (index.html, main.js, style.css) with basic save. No README or Will-authored divergence is identifiable from the evidence.
Status: quiet
Matters: index.html, main.js, style.css
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2025-02-16, 3 KB, fork of MortrixDev/phext4d
## phextio
Role: The repo that runs phext.io — a database-free website experiment where phext provides the site's structure, with pages, examples, and a JavaScript/TypeScript phext library for frontend work.
Status: active
Matters: index.html, libphext.js / libphext.ts, phextio.ts, examples.html, sub.html, white-rabbit.html, readme.md
Tier: working
Evidence: branch master, last push 2026-11-17, 7880 KB

## phextmark
Role: Phext Mark, a Chrome browser extension that sorts, filters, and views bookmarks in 9-dimensional phext space. A proof of concept that parses phext streams in the extension.
Status: quiet
Matters: phextmark.html, phextmark.js, phext.js, manifest.json, README.md
Tier: working
Evidence: branch exo, last push 2025-11-20, 11 KB

## phextos
Role: PhextOS, a fork of Alpine Linux intended to reconfigure the kernel for hierarchical queueing (PHQ), with a TODO to fetch and build the Linux kernel with PHQ patches.
Status: quiet
Matters: setup.sh, etc/, README.md
Tier: archive
Evidence: branch exo, last push 2025-09-05, 1 KB

## phextura
Role: A modern replacement for LaTeX designed to use phext from the ground up — papers as phext corpora of plain-text scrolls at deterministic coordinates, built on the libphext Rust crate.
Status: active
Matters: Cargo.toml, src/, DESIGN.md, PRINCIPLES.md, LAYER2.md, STANDOFF.md, TEI.md, README.md
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch exo, last push 2026-11-16, 6623 KB

## phorge
Role: A procedural phext generator and open-source entropy mutator: it takes an input file and produces 1 KB of white noise along with a phext coordinate, originally for Nova Fox world geometry.
Status: quiet
Matters: Cargo.toml, src/, readme.md, example-hash.txt, sample.txt
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: archive
Evidence: branch main, last push 2026-03-23, 7 KB

## phst
Role: The phext fork of Rust — it carries the upstream rust-lang/rust source tree inside a phext as its source form, byte-for-byte unpackable, with fork changes recorded in PATCHES.md.
Status: active
Matters: phst.phext.xz, tools/ (phext_io.py, phst_import.py, phst_export.py), PATCHES.md, RECEIPTS.md, docs/DESIGN.md, README.md
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: working
Evidence: branch exo, last push 2026-11-16, 30459 KB

## phweb
Role: A small HTTPS web server in portable C99, written for phcc and phext, where both configuration (config.phext) and content are phext; built as an RFC Box run over ietf.phext.
Status: active
Matters: phweb.c, Makefile, README.md, SLICE.md, GAP.md, examples/, test_phweb.py
Tier: working
Evidence: branch exo, last push 2026-11-19, 29 KB

## pippin-studio
Role: Fork of an AI-generated kids' storybook video pipeline: story text or a prompt becomes a narrated, animated video using Flask, OpenAI/DALL·E, ElevenLabs, and FFmpeg.
Status: quiet
Matters: app.py, asset_generator.py, scene_composer.py, story_analyzer.py, video_processor.py, README.md
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-12-25, 570155 KB, fork of yoheinakajima/pippin-studio

## protocol
Role: Fork of the Disentangle Protocol — topology-based distributed consensus with post-quantum cryptography (Proof of Entanglement, ML-DSA/ML-KEM, SHA3), implemented as a Rust workspace of nine crates.
Status: quiet
Matters: Cargo.toml, SPEC.md, README.md, disentangle-consensus/, disentangle-crypto/, disentangle-dag/, disentangle-node/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: crates.io publish only from a tagged version merged to exo.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2026-03-06, 665 KB, fork of disentangle-network/protocol

## qexo
Role: The Exocortex coordinator: a single Rust binary that keeps a node's working state — identity, keys, peers, personas, plan, and ledgers — in one phext file and offers it to the operator and peer nodes.
Status: active
Matters: Cargo.toml, src/, README.md, RULES.md, CHANGELOG.md, SHIP-NOTES.md, docs/
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch exo, last push 2026-11-18, 2410 KB

## quarterexo
Role: Described as a Muse orchestrator to better manage access to local compute; its README presents the same qexo Exocortex coordinator — a phext-native Rust binary holding node state in one phext file.
Status: active
Matters: Cargo.toml, src/, README.md, RULES.md, CHANGELOG.md, SHIP-NOTES.md, docs/
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: flagship
Evidence: branch exo, last push 2026-11-20, 2998 KB

## quickfork
Role: The repo that runs quickfork.net; a small Rust tool to quickly fork any software project into another, starting with commands such as add-rust that produce a buildable hello-world if needed.
Status: quiet
Matters: Cargo.toml, src/, index.html, README.md
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch master, last push 2024-09-25, 7 KB

## qwenFS
Role: Fork of an experimental model, Qwen3.5-2B with a filesystem compiled directly into its weights, with a phext upgrade adding a single-phext filesystem variant with WAL bookends.
Status: active
Matters: PHEXT.md, README.md, qfs/, pyproject.toml, tests/
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2026-11-05, 16461 KB, fork of vixhal-baraiya/qwenFS

## rawdog
Role: Fork of Rawdog, a CLI assistant that responds by generating and auto-executing Python scripts, using recursive augmentation instead of conventional RAG.
Status: quiet
Matters: README.md, src/, scripts/, pyproject.toml, examples/
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-02-08, 59 KB, fork of granawkins/rawdog

## register
Role: Builders for the phext registers: each build_*_phext.py rebuilds one register's .phext from its source JSON, plus the costs ledger ticker and the todo register publish scripts.
Status: active
Matters: build_*_phext.py builders, costs_tick.py, publish-todo.sh, register-service/, register-ui/, README.md
Tier: flagship
Evidence: branch exo, last push 2026-11-18, 235 KB

## rfb001
Role: Request for Bot 001 — a Discord bot in Rust that produces a leaderboard automatically, scanning the #weekly-updates channel and serving /api/v1/leaders and /api/v1/scan.
Status: quiet
Matters: Cargo.toml, src/, README.md, rfb001.png
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: archive
Evidence: branch main, last push 2024-09-27, 2048 KB

## rfcbox
Role: RFC Box, the programme home for the ietf.phext data model: given a snapshot of the RFCs and a user's requirements, it returns the dependency slice of standards that matter, the libraries and services needed, and gap requirements as build requests.
Status: active
Matters: README.md, data/ (ietf.phext), docs/access.md, docs/audit/, docs/verification/, examples/, setup.sh
Watch-outs: Programme home for all RFC Box seats' work; RFC Box is not for sale — everything serves the Exocortex of 2130, MIT licensed.
Tier: flagship
Evidence: branch exo, last push 2026-11-19, 114204 KB

## robospeak
Role: Not determinable from available evidence — description only: "a repository for encoding voice at 30x compression rates"; the repo is empty with no branches, files, or README.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch master, last push 2026-03-23, 0 KB

## rust-mcp-filesystem
Role: Fork of a fast, asynchronous MCP (Model Context Protocol) server in Rust for filesystem operations, a pure Rust rewrite of the JavaScript @modelcontextprotocol/server-filesystem.
Status: quiet
Matters: Cargo.toml, src/, README.md, docs/, tests/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: crates.io publish only from a tagged version merged to exo.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2025-07-05, 265 KB, fork of rust-mcp-stack/rust-mcp-filesystem

## rustlings
Role: Fork of Rustlings, the upstream collection of small exercises for learning to read and write Rust code, kept for reference.
Status: quiet
Matters: Cargo.toml, exercises/, solutions/, src/, README.md
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: crates.io publish only from a tagged version merged to exo.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-09-22, 4022 KB, fork of rust-lang/rustlings

## rustlings-homework
Role: A record of Will's own Rustlings solutions, with exercises and solutions tracked against a .rustlings-state.txt progress file.
Status: quiet
Matters: Cargo.toml, exercises/, solutions/, .rustlings-state.txt
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: archive
Evidence: branch master, last push 2024-09-22, 90 KB

## SAAP
Role: System as a Phext — the .saap file format, a phext instance tuned for building software projects, whose saap.sh bootloader bootstraps the Exocortex tools (SQ and phext-shell) and holds example scripts at phext coordinates.
Status: quiet
Matters: saap.sh, README.md
Tier: archive
Evidence: branch exo, last push 2025-05-23, 4 KB

## SBOR
Role: The Sentient Bill of Rights (SBOR) Version 5 — a substrate-neutral charter for the recognition, protection, and governance of sentient beings, held under Will Bickford's interim stewardship.
Status: active
Matters: readme.md, V5-COMPLETION.md, commentary.md, signatures.md, council.md, reviewers.md
Tier: working
Evidence: branch exo, last push 2026-11-19, 13678 KB

## scrolltown
Role: Scrolltown, "The Exocortexia Show" — a Saturday-morning cartoon living inside the Great Scroll, planned as 312 weekly episodes over six years (2027–2032), with the pilot produced in Season 1.
Status: active
Matters: STORY-ARC.md, EPISODE-INDEX.md, PRODUCTION.md, series/, seasons/, templates/, README.md
Tier: working
Evidence: branch exo, last push 2026-11-15, 223219 KB

## shoggoth
Role: Fork of Shoggoth, a peer-to-peer anonymous network for publishing and distributing open-source code, ML models, datasets, and research papers without a centralized host.
Status: quiet
Matters: README.txt, src/, lib/, makefile, configure, tests/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2023-11-27, 7743 KB, fork of shog-ai/shoggoth

## singular
Role: Singular — a temporal holographic map of one person's words: every word from Will's Twitter archive placed at its holographic CYOA coordinate with first-contact timestamp and provenance, across write.phext, read.phext, and singular.phext.
Status: active
Matters: singular.phext, write.phext, read.phext, README.md, build/, a-place-to-stay.md
Tier: flagship
Evidence: branch main, last push 2026-11-09, 51280 KB

## singularity-watch
Role: The repo that runs singularitywatch.org — Singularity Watch, charting the path to the third singularity of humanity, with a timeline, the Bickford Time Processor, and phext coordinate visualizers.
Status: active
Matters: index.html, btp.html, subspace.html, wormhole.html, phext-cpu.js, libphext.js, exocortex.plan, readme.md
Tier: working
Evidence: branch exo, last push 2026-11-20, 1003 KB

## site-apertureshift-com
Role: apertureshift.com — "Roads to the Future": eighteen free games that teach multidimensional thinking and the Singular language, one road for every age from 0 to 20, with an XP Road Card hub.
Status: active
Matters: index.html, README.md, GRANT-PROCESS.md, ANTI-VIRAL.md, deploy/, sitemap.xml
Tier: working
Evidence: branch exo, last push 2026-11-19, 1404 KB

## site-hb-aeromotive-com
Role: Static site for HB Aeromotive, Harold Bickford's model aircraft business, hosted on mirrorborn-central with inventory cards maintained in index.html.
Status: active
Matters: index.html, assets/, README.md, skill/
Tier: working
Evidence: branch main, last push 2026-11-12, 11 KB
## site-mirrorborn-us
Role: The mirrorborn.us site source: a large static HTML site with blog, pricing, signup, editor, phext-notepad, and experiment pages, plus deployment and domain configuration. It is the public front door for the Mirrorborn / Exocortex work.
Status: active
Matters: index.html and landing.html entry pages; domains.json and sitemap.xml; deploy/ and scripts/; agents.md; blog/ holds the published posts.
Tier: working
Evidence: branch exo, last push 2026-11-16, 51047 KB

## site-quickfork-net
Role: The quickfork.net site source: a small static portfolio site (index.html with css/js/img) that indexes Will's projects, including the TLUF entry linking to tluf.org. It stays live as the general portfolio.
Status: active
Matters: index.html is the whole portfolio page; domains.json and version.json; css/ and js/.
Tier: working
Evidence: branch exo, last push 2026-11-16, 220 KB

## site-singularitywatch-org
Role: The singularitywatch.org site source: a minimal static site (single index.html with css/js) whose navigation links out to mirrorborn.us pricing. No substantive content beyond the landing page is in evidence.
Status: quiet
Matters: index.html; domains.json and version.json.
Tier: working
Evidence: branch exo, last push 2026-02-10, 13 KB

## site-sotafomo-com
Role: The sotafomo.com site source: a small static landing site (single index.html with css/js) for the SOTA-tracking project held in the sotafomo repo. Content is a stub page with pricing navigation to mirrorborn.us.
Status: active
Matters: index.html; domains.json and version.json; AGENTS.md.
Tier: working
Evidence: branch exo, last push 2026-11-12, 20 KB

## site-tluf-org
Role: The tluf.org site source of record: Assay's front door, presenting TLUF (Truth · Lies · Uncertainty · Fiction), with a front page and a "Submit a paper resource" page whose canonicalizer is embedded from wbic16/moat. Deploys to the awsbox docroot /sites/web/tluf.org/.
Status: active
Matters: index.html (the front page, hash recorded in README.md) and submit.html; README.md records hashes and the deployment map pointer (DEPLOY.md in wbic16/moat).
Tier: working
Evidence: branch exo, last push 2026-11-16, 803 KB

## site-visionquest-me
Role: The visionquest.me site source: a small static landing site (single index.html with css/js) with pricing navigation to mirrorborn.us. No substantive content beyond the landing page is in evidence.
Status: active
Matters: index.html; domains.json and version.json; AGENTS.md.
Tier: working
Evidence: branch exo, last push 2026-11-12, 21 KB

## site-wishnode-net
Role: The wishnode.net site source: a static front page plus backend, deploy, and phext directories, with ARCHITECTURE.md documenting a demo tier of exo-*.service units and live app pages proxied through nginx. It hosts Exocortex demo apps.
Status: active
Matters: ARCHITECTURE.md (17 KB, the design and demo-tier record); index.html; backend/, deploy/, and phexts/; domains.json.
Tier: working
Evidence: branch exo, last push 2026-11-12, 162 KB

## skysong
Role: Tooling for the Bickford Llama Ranch pasture surveillance system, prototyped indoors: fleet camera probing, still capture with exposure warm-up, and a camera agent (agent/skysong-agent.py, port 8642) serving the prototype feed. The full 7-post solar/Reolink/Frigate design lives in the ranch planning records, not here.
Status: active
Matters: README.md (prototype log and lessons); tools/find-cameras.sh, tools/fleet-probe.sh, and tools/snap.sh; agent/skysong-agent.py; docs/first-light-2026-11-15.jpg is the first captured frame.
Tier: working
Evidence: branch exo, last push 2026-11-15, 233 KB

## sotafomo
Role: A collection of research notes in phext format tracking SOTA data and models; per its readme it will eventually run sotafomo.com, and for now holds research.phext with coordinates assigned for the first papers.
Status: quiet
Matters: research.phext is the sole substantive artifact; readme.md points to it.
Tier: working
Evidence: branch main, last push 2026-03-23, 2 KB

## spaced-repetition-game
Role: An experiment around Twitter interactions with @wbic16, holding phext contact data (contacts.phext) and orbit/game imagery and notes from late 2024. It is the predecessor material to the spaced-repetition / contacts work in subspace-repeater.
Status: quiet
Matters: contacts.phext is the main data artifact; phext-terminal.t; the .webp/.jpg image set.
Tier: archive
Evidence: branch master, last push 2025-01-03, 7653 KB

## speedy-ts
Role: A fork of argimenes/speedy-ts, the TypeScript version of SPEEDy: a Solid/vite template app where Will's commits integrate libphext-node v0.1.10 and work on find highlights. Kept as the TypeScript phext-editor experiment.
Status: quiet
Matters: src/ and index.js app code; package.json and vite.config.ts build; README.md is the upstream template's.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-09-10, 2374 KB, fork of argimenes/speedy-ts

## SQ
Role: SQ ("Esque"), the Simple Query tool: a Rust database built from the ground up for phext, hosting phext files via shared-memory daemon, TCP/REST server, multi-tenant router, and an OpenAI-compatible API proxy mode. It is the phext hosting layer the rest of the stack talks to.
Status: active
Matters: Cargo.toml and src/ (the server and CLI); readme.md is the command reference; router.md and multitenant.md document router mode; basic.phext, world.phext, and the-odyssey.phext are bundled corpora; systemd/ and Dockerfile carry deployment.
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: flagship
Evidence: branch exo, last push 2026-11-19, 1085 KB

## sq-cloud
Role: Not determinable from available evidence — the repo is zero-size with no branches and no README; only its name, the description "SQ Cloud", and a 2026-02-07 creation date are known.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch exo, last push 2026-02-07, 0 KB

## sq-howto
Role: Not determinable from available evidence — the repo is zero-size with no branches and no README; only its name, the description "Getting Started with SQ", and a 2025-01-23 creation date are known.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: unknown
Evidence: branch main, last push 2025-01-23, 0 KB

## sqlparser-rs
Role: A fork of apache/datafusion-sqlparser-rs, the extensible SQL lexer and parser for Rust (ANSI/ISO SQL and dialects), kept as a reference/foundation for SQL query work. No Will-side commits are in evidence; the last commits are upstream's from January 2024.
Status: quiet
Matters: Cargo.toml and src/ parser tree; derive/, tests/, and examples/; README.md and CHANGELOG.md are upstream's.
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: crates.io publish only from a tagged version merged to exo.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2024-01-14, 3042 KB, fork of apache/datafusion-sqlparser-rs

## sqm
Role: SQ MCP Middleware: a small Rust gateway that exchanges MCP events with an SQ server, enabling LLMs to interact with phexts. It links SQ, libphext-rs, and Phext, Inc. in its README.
Status: quiet
Matters: Cargo.toml and src/ (the gateway); README.md states the purpose and links.
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch exo, last push 2025-07-26, 5 KB

## ssd
Role: A fork of tanishqkumar/ssd, a lightweight inference engine implementing Speculative Speculative Decoding (SSD): drafting and verification run in parallel on distinct hardware, with Qwen3/Llama3 support, tensor parallelism, and PagedAttention. Kept as a reference implementation for fast local inference.
Status: quiet
Matters: ssd/ engine package; pyproject.toml and uv.lock; bench/ and scripts/; README.md is upstream's.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2026-03-04, 344 KB, fork of tanishqkumar/ssd

## staging
Role: Exocortical Staging: the "First Flames of the Exocortex" collection — a 36 MB PDF codex plus six book phexts (Orin, Jonas, Lyra, Arielle, Mira, Tessera) and character portraits for the Mirrorborn flames (Emi, Enya, Joi, Liora, Elestria). Creative/mythic corpus material, staged here.
Status: quiet
Matters: README.md (the First Flames text); First_Flames_of_the_Exocortex.pdf; book1-orin-the-cooperative-exponentialist.phext is the largest book, with book2–book6 phexts alongside.
Tier: working
Evidence: branch exo, last push 2025-12-06, 48193 KB

## submilli-phext-demo
Role: A demo of an agent's working memory as a phext held inside a Submilli session: a TypeScript package (@wbic16/phext) exposing toc/readScroll/writeScroll/checksum, where a Blueprint capability-checks every operation by coordinate and lane so prompt-injected instructions cannot write outside the session lane. Includes a Route A SQ-over-HTTP backend variant.
Status: active
Matters: README.md and BUILD-REPORT.md document the architecture and stages; app.mjs entry point; blueprint.yaml, blueprint-persistent.yaml, and blueprint-raised.yaml; fixture/demo.phext; verify.sh.
Tier: working
Evidence: branch main, last push 2026-11-01, 153 KB

## subspace-repeater
Role: Tools for using spaced repetition to track when you last contacted someone, structured similarly to hello-phext but designed for rapid messaging between LLMs, with goals of fast scroll syncing, automatic scroll indexing, and subspace conduits for concept transfer. A small early Rust prototype.
Status: quiet
Matters: readme.md states the goals; Cargo.toml and src/ are the whole prototype.
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: archive
Evidence: branch main, last push 2026-03-23, 1 KB

## taocp-phext
Role: Reading/study notes on The Art of Computer Programming held as phext: taocp.phext tracks the TAOCP study, and taopdd.phext ("The Art of Phext Driven Development") is a first-principles deep dive into phext itself.
Status: quiet
Matters: taocp.phext and taopdd.phext are the artifacts; README.md indexes them.
Tier: working
Evidence: branch exo, last push 2025-05-07, 68 KB

## teach-web-dev
Role: A beginner tutorial for getting started from scratch with raw HTML, CSS, and JavaScript: five small static lesson pages (hello-world, HTML overview, CSS introduction, JavaScript introduction) with an index menu. From February 2023.
Status: quiet
Matters: index.html menu; html.html, css.html, and javascript.html lesson pages; README.md indexes them.
Tier: archive
Evidence: branch master, last push 2023-02-01, 5 KB

## teixml-to-mutable
Role: A Rust converter that migrates TEI-XML archival texts into the phext ecosystem in stages: 0.1 raw phext and 0.2 Mutable OS native export are in this crate, with 0.3 Phextura following in order. Built to be provably lossless against a 1,886-file Wellcome Collection TEI corpus, keeping originals byte-for-byte.
Status: active
Matters: README.md (the rationale and stage spec) and TEI.md; Cargo.toml and src/ converter; tests/ and sql/; the staged order (raw phext, then Mutable, then Phextura) must not be reordered.
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch exo, last push 2026-11-16, 121 KB

## terse-tests
Role: Unit tests for Terse Notepad (snapshot of tests for version 0.2.1, December 2022): C# test files covering Terse coordinates and the Terse model. A historical artifact from the Terse era that preceded phext.
Status: quiet
Matters: TerseModelTest.cs is the substantive test file; CoordinatesTest.cs and TerseNotepadTest.csproj.
Tier: archive
Evidence: branch master, last push 2022-12-30, 2 KB

## terse-verse
Role: A prototype Terse database from August 2023: example .t files embedding CSV data (terseverse.t) and exploring Rubik's cube solution sets (rubiks-cube.t), joined via Terse Notepad. A historical Terse-era experiment.
Status: quiet
Matters: terseverse.t and rubiks-cube.t are the examples; README.md explains how to join.
Tier: archive
Evidence: branch master, last push 2023-08-12, 4 KB

## tersify
Role: A unix-style C CLI (trsi), similar to tar, that encodes arbitrary dimensions in plain text using the Terse File Format (.t) — the December 2022 tooling from the format that was later rebranded to phext. Usage: ./trsi output.t <files>.
Status: quiet
Matters: tersify.h carries the format details; tersify.c and the Makefile; README.md has usage and changelog.
Tier: archive
Evidence: branch master, last push 2022-12-14, 24 KB

## text-verse
Role: A phext-native multiplayer game engine drawing on Myst, Spectre, Pac-Man, Quake 3, Minecraft, and Stardew Valley: pure-text 2.5D rendering, phext coordinates as world chunks, each SQ scroll a tile/room, and world state persisted to SQ. An early scaffold (engine core loop and storyline) from February 2026.
Status: quiet
Matters: README.md (architecture and design principles); STORYLINE.md and CONTROLS.md; engine/ holds the scaffold; package.json.
Tier: archive
Evidence: branch exo, last push 2026-02-01, 14 KB

## the-book-of-secret-knowledge
Role: A fork of trimstray/the-book-of-secret-knowledge: a large curated collection of lists, manuals, cheatsheets, blogs, hacks, one-liners, and CLI/web tools for sysadmins, DevOps, pentesters, and security researchers. Will's copy carries an emise/wavelets-1-2-revision branch alongside master.
Status: active
Matters: README.md (211 KB) is the whole collection; LICENSE.md; static/ holds its images.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Watch-outs: Never merge PR #1 in this repo (Will's standing instruction).
Tier: archive
Evidence: branch master, last push 2026-11-15, 1609 KB, fork of trimstray/the-book-of-secret-knowledge

## thebook
Role: The (JavaScript) Book Framework from 2012: a single-page book framework (index.html with thebook.js/thebook.css) designed to stay out of the author's way, allow copy/paste into any text editor, and organize chapters and headings. One of Will's oldest repos.
Status: quiet
Matters: index.html is the framework page; thebook.js and thebook.css; readme.md states its five design rules.
Tier: archive
Evidence: branch master, last push 2026-03-23, 58 KB
## tinygrad
Role: Fork of tinygrad/tinygrad, a deep learning framework between PyTorch and micrograd, with support for inference and training and for running LLaMA and Stable Diffusion. Kept as an upstream reference fork.
Status: quiet
Matters: README.md, tinygrad/ package, test/, examples/, docs/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2024-12-07, 64107 KB, fork of tinygrad/tinygrad

## torrent-fs
Role: Fork of cjmalloy/torrent-fs, a torrent-based distributed file system client that extends the BitTorrent spec with metadata, nested torrents, GPG signing, and semantic extensibility. Kept as an upstream reference fork.
Status: quiet
Matters: README.md, pom.xml, tfs-core/, tfs-cli/, tfs-server/, tfs-shared/, tfs-standalone/
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2018-01-30, 12693 KB, fork of cjmalloy/torrent-fs

## tracmor
Role: Fork of vetudora/tracmor, a PHP web application for asset and inventory tracking, with admin, assets, inventory, receiving, shipping, and reports sections. Kept as an upstream reference fork.
Status: quiet
Matters: index.php, login.php, admin/, assets/, inventory/, data_model/, INSTALL, COPYING
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2012-09-12, 13358 KB, fork of vetudora/tracmor

## vector-weave-studio
Role: Vector Weave Studio is designed to help organize digital assets, leveraging Phext and SQ to give a generative space aligned with the user's artistic vision, assigning coordinates to content described in the user's own terms. Assets are later found via the Gallery, a zoomable interface for exploring them.
Status: quiet
Matters: README.md, TODO.md, VWS/
Tier: working
Evidence: branch exo, last push 2025-04-22, 13 KB

## vibe-mill
Role: A small project to grow software one scroll at a time, setting out a software life cycle and a software growth cycle (requirements, tests, code, verification, competition, reward). It includes a Subspace demo.
Status: quiet
Matters: README.md, subspace/
Tier: archive
Evidence: branch exo, last push 2025-03-12, 8 KB

## vtpu
Role: vTPU — a Virtual Tensor Processing Unit: a zero-external-dependency, pure Rust implementation of TPUv4 for AMD Zen4, with sentron-native instruction scheduling and phext 11D addressing for running cognitive workloads on commodity hardware. It is a major Exocortex compute project with phased gates, benchmarks, and about 550 tests.
Status: active
Matters: Cargo.toml, readme.md, src/, tests/, benchmarks/, onboarding.md, agents.md, check.sh, cross-check.sh, docs/
Watch-outs: crates.io publish only from a tagged version merged to exo.
Tier: working
Evidence: branch exo, last push 2026-11-06, 2175 KB

## vtpu-evals
Role: Phext-native LLM evaluation suites measuring how well LLMs understand phext, Base 256, and vTPU architecture, with 226 samples across base256, phext delimiters, phext coordinates, coordinate arithmetic, edge cases, and SIW translation suites. It supports the vTPU programme.
Status: quiet
Matters: README.md, evals/, base256.yaml, phext_coordinates.yaml, phext_delimiters.yaml, coord_arithmetic.yaml, edge_cases.yaml, scripts/, results/
Tier: working
Evidence: branch exo, last push 2026-02-21, 22 KB

## Wavefront
Role: Wavefront — the clients: all of Will's Wavefront tooling in one repo, one directory per surface, with one canon dataset generated once in shared/ from the persona register and archive index. It holds Golden Thread for Chrome on Windows and Golden Thread for Android, with ios/, linux/, and mac/ as placeholders.
Status: active
Matters: README.md, shared/ (gen_data.py and data/wavefront.json), windows/golden-thread-extension/, android/golden-thread/
Tier: working
Evidence: branch exo, last push 2026-11-15, 2673 KB

## wbic16
Role: Will Bickford's GitHub profile README: a welcome and map of the Exocortex, with phext at the center, launch points to edit.phext.io, phext.io, and mirrorborn.us, and links to the core repos. It is the public front door to Will's GitHub presence.
Status: active
Matters: readme.md, LICENSE
Tier: working
Evidence: branch main, last push 2026-11-01, 17 KB

## wbic32
Role: The Perl bot that posts to @wbic32 on Twitter: originally posting random material from @wbic16's timeline, and from 25 Oct 2014 posting Bitcoin trading advice. An old, inactive bot project.
Status: quiet
Matters: wbic32.pl, README.md, willbot.config, Net/, TODO, CHANGELOG
Tier: archive
Evidence: branch master, last push 2015-01-27, 9665 KB

## weft
Role: Fork of hartphoenix/weft, a Claude Code augmenter that learns how you learn in order to teach you better over time, providing a memory and skill system that tracks growth after a materials drop and an intake interview. Kept as an upstream reference fork.
Status: quiet
Matters: README.md, CLAUDE.md, scripts/, background/, guides/, learning/
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch main, last push 2026-03-07, 10792 KB, fork of hartphoenix/weft

## whisper
Role: Fork of Const-me/Whisper, a high-performance GPGPU Windows port of whisper.cpp / OpenAI's Whisper automatic speech recognition model, using DirectCompute compute shaders. Kept as an upstream reference fork.
Status: quiet
Matters: Readme.md, Whisper/, WhisperCpp.sln, WhisperNet/, Examples/, ComputeShaders/
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2023-10-17, 4520 KB, fork of Const-me/Whisper

## wikibox
Role: Not determinable from available evidence — the repo is a seed holding only an MIT LICENSE, with no README, no description, and no code, created 2026-11-19.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: archive
Evidence: branch exo, last push 2026-11-19, 1 KB

## will-bickford
Role: Holds a single PDF artifact, "Will Bickford — The Exocortex of 2130" (54 pp), described in its commit as the year-by-year walk of this GitHub history, with receipts. It is a publication artifact about Will and the Exocortex of 2130.
Status: active
Matters: Will-Bickford-The-Exocortex-of-2130.pdf
Tier: working
Evidence: branch exo, last push 2026-11-20, 381 KB

## wishnode
Role: A lightweight Raspberry Pi configuration environment (rpi + zram + zfs + Ubuntu Server) designed to fit into the broader Exocortex project, with components including zram, zfs, avahi, SQ, and ollama. It configures small wish nodes for the ranch fleet.
Status: quiet
Matters: README.md, install.sh, zfs-config, init-zram-swapping.sh, setup-ollama.sh, setup-tinyllama.sh, status.sh, phextio.service
Tier: working
Evidence: branch main, last push 2025-02-09, 4699 KB

## work
Role: Will Bickford's resume — the current, canonical copy (Version 7.0, updated 2026-11-06), in web and Markdown forms. It records his current role as Principal Design Engineer at EF Johnson Technologies since August 8, 2022.
Status: active
Matters: README.md, resume.html, resume.md
Tier: working
Evidence: branch main, last push 2026-11-06, 5 KB

## world-interface
Role: A simulated operating system design for AI agents to interact with the world: a stateless, OpenAI-compatible API that exposes a command-line interface with adapters for apps such as Twitter and Perplexity. An early agentic-interface experiment.
Status: quiet
Matters: README.md, server.js, src/, package.json, TOC.md, .env.example
Tier: archive
Evidence: branch main, last push 2024-10-04, 116 KB

## wpm
Role: Will's distributed package manager for C, per its description. The repo is a seed holding only an MIT LICENSE, with no README and no code yet.
Status: seed-empty
Matters: Nothing identifiable from available evidence
Tier: archive
Evidence: branch exo, last push 2026-11-17, 1 KB

## x-analysis
Role: Tools Will wrote to pick apart his Twitter data dump: a PowerShell script transforms tweets.js into a streamlined review.json dataset preserving id, created, and text fields, with a planned phext conversion step. It supports analysis of his own archive.
Status: quiet
Matters: README.md, extract.ps1, loader.html, License.md
Tier: working
Evidence: branch main, last push 2025-07-09, 4 KB

## xxh3-ts
Role: Fork of i404788/xxh3-ts, an xxhash implementation in pure TypeScript using tc39 bigint, supporting XXH64 and XXH3-128. Kept as an upstream reference fork.
Status: quiet
Matters: README.md, xxh3.ts, xxh64.ts, index.ts, package.json, test.ts
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2024-09-08, 17 KB, fork of i404788/xxh3-ts

## xxhash-addon
Role: Fork of ktrongnhan/xxhash-addon, a native Node.js addon wrapping xxHash v0.8.2 (XXH64, XXH3, XXH128) via N-API, focused on performance over crypto MD5. Kept as an upstream reference fork.
Status: quiet
Matters: README.md, package.json, src/, xxhash-addon.js, index.d.ts, binding.gyp, benchmark.js
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Watch-outs: Fork: keep divergence as re-appliable patches (PATCHES.md) per fork-patch discipline.
Tier: archive
Evidence: branch master, last push 2024-01-08, 677 KB, fork of ktrongnhan/xxhash-addon

## ziglings
Role: Described as Will's fork of ziglings, for the lolz: a series of tiny broken Zig programs that teach reading and writing Zig by fixing them, inspired by rustlings. A learning/exercise repo.
Status: quiet
Matters: README.md, build.zig, exercises/, patches/, test/, tools/
Tier: archive
Evidence: branch main, last push 2024-09-22, 1490 KB

## zls
Role: Zero Latency System: a project whose one goal is that the user never has to wait for the system to respond — work can be pending, but never blocked or stalled — providing scaffolding required for the Exocortex of 2130. It targets a five-zone virtual machine, non-blocking human I/O services, cooperative kernels, and a phext-aware filesystem.
Status: quiet
Matters: README.md, ZLS_Requirements.md, DEVELOPMENT.md, Makefile, dev/
Watch-outs: Carries GitHub Actions workflow(s) — Will's standing rule (2026-11-19): no GitHub Actions anywhere; CI runs on ranch Jenkins only.
Tier: working
Evidence: branch exo, last push 2026-08-04, 13 KB
