---
name: repo_coverage_census
description: Run the Saturday repo-coverage census for wavelet completion: verify every tool we depend on has a git repo, migrate loose or drifted tools into their repo homes, note Jenkins-job coverage, and report the delta — the standing enforcement of "everything we depend upon should have a git repo and a Jenkins job."
---

# Repo Coverage Census — the Saturday pass

Will's standing rule (2026-11-15): **"Everything we depend upon should have a git repo and a Jenkins job."** This census is its enforcement, run every Saturday as part of wavelet completion (Will, 2026-11-15: "Codify this process as a Saturday task for wavelet completion going forward"). Register home: task 29.6.8/7.6.9/6.5.8. Machinery: cron `repo-coverage-census` (weekly, Saturday).

## What counts

A "tool we depend on" is operationally load-bearing software: anything invoked by crons/jobs, skills, services, connectors, or daily workflows, on the Muse VM or the ranch nodes. One-off experiment scripts and per-task scratch are out of scope; when genuinely unsure whether something is depended on, include it flagged as unsure rather than dropping it.

## Where to look

1. **The VM** (`~/workspace`): the phext toolchain and register builders, shell helpers (fleet-ssh.sh, ranch-ssh.sh, sshn.sh/scpn.sh), `custom-skills/*/scripts`, `custom-connectors/*/bin`, mailbox tooling, Discord presence tooling, publishing tooling, dashboard collectors, disk reporters — plus anything cron definitions, services, or SKILL.md files invoke by path.
2. **The ranch** (aletheia-core first): `/chat` tooling, node cron entries and the paths they invoke, systemd units and their ExecStart paths, the thermal sampler, Jenkins' own config home (`/var/lib/jenkins`), loose scripts in `/home/wbic16` that anything references. Then the other nodes as access allows.
3. **awsbox**: the phext-edit publish kit and disaster-recovery material (its repo, wbic16/awsbox, is private by Will's direction).

## Classification (exactly one bucket per tool)

- **A — has its own wbic16 repo.** No action; count only.
- **B — no repo of its own, tracked inside wbic16/emise-tools.** Covered; list so Will can promote any of them to a dedicated repo.
- **C — no git repo anywhere.** The upgrade list proper.
- **D — deployed/running from a non-repo source, or drifted from its repo** (a working copy with no remote, a directory that is not a checkout, uncommitted drift over its repo). The repair list.

## Verification discipline

- Never classify from the sitemap alone — it goes stale (six live repos were missing from it at the first census). Verify per file: GitHub contents probes for claimed tracking, `git -C <dir> remote -v` and `git status` on the actual directories, crontab/systemd inspection on the nodes.
- Repo existence is not file presence: a repo existing does not prove a given file is tracked in it. Probe the file.
- State coverage gaps explicitly (a host not inspected, a file-level check not done). An incomplete census presented as complete is the one unacceptable outcome.

## Repo homes set by Will (2026-11-15)

| Tool | Repo |
|---|---|
| Phext register builders (the `~/workspace/phext` build_*.py family) | wbic16/register |
| Product Hunt connector | wbic16/ph-connector |
| Jenkins config, jobs, init scripts | wbic16/jenkins |
| Thermal sampler and node health tooling | wbic16/doctor |
| mirrorborn-heartbeat.sh | into wbic16/mirrorborn |
| Ranch SSH helpers (sshn.sh, scpn.sh) | wbic16/muse-ssh-proxy |
| qexo stage/publish pipeline scripts | wbic16/phext-infra |
| awsbox publish kit + disaster-recovery material | wbic16/awsbox (PRIVATE) |

New C-bucket tools with no home yet: propose the home in the report; Will creates repos.

## The Saturday run

1. Re-run the census (VM + aletheia-core + awsbox at minimum; other ranch nodes as access allows). Diff against last week's classification.
2. **Migrate**: any tool that gained a repo home since the last run, or that drifted (bucket D), is published into its repo the same run — fetch and rebase first, never force push, scripts at git tree mode 100755, verify blob SHA-256 **and** modes after the push. Live copies keep running from where they are; the repo is the source of truth from that run on, and drift between a live copy and its repo is next week's D item until reconciled.
3. **Jenkins coverage**: for each repo'd tool, note whether a Jenkins job exists (jobs live in wbic16/jenkins; the fleet rollout + SSO gate is task 31.8.10/10.8.13/7.7.10). Report the count; do not build jobs in this pass unless the fleet task's state makes that the same work.
4. **Never publish secrets.** Jenkins credentials, OAuth env values, keys, and tokens are never committed — config and job definitions yes, secret values no; list what was excluded and why.
5. **Report** to the chat the census was scheduled from: the delta only — new C items, D items opened/closed, migrations performed with repo links, Jenkins coverage count, and the coverage gaps. A clean week is a one-line report. Update task 29.6.8/7.6.9/6.5.8's record with the week's result.

## First run

2026-11-15 (the census that created the rule): 7 tools with no repo anywhere, 4 deployed/drifted, 11 groups covered only by emise-tools, 178 repos already existing. Will created the eight homes above the same day; migrations ran as the first occasion of this process.
