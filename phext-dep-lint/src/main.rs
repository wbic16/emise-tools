//! phext-dep-lint — enforce phext-minimum-viable-dependencies.
//!
//! Policy comes from a phext-based audit (policy/audits.phext): one
//! scroll per crate, a passing verdict on record, or the crate is
//! denied — "no audit on record" — whether or not existing code
//! already uses it. See README.md.
//!
//! Zero external dependencies: std only, by policy and by design.

mod lock;
mod manifest;
mod phext;
mod policy;
mod toml;

use manifest::DepSource;
use policy::{AuditSet, Exception, Verdict};
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

#[derive(Debug, Clone)]
struct Violation {
    kind: String,
    krate: String,
    detail: String,
    path: Option<Vec<String>>,
}

#[derive(Debug)]
struct ProjectReport {
    name: String,
    path: String,
    direct_count: usize,
    transitive_count: Option<usize>,
    budget: u64,
    status: String, // "pass" | "fail"
    violations: Vec<Violation>,
    exceptions_applied: Vec<String>,
    notes: Vec<String>,
}

struct Args {
    policy: PathBuf,
    exceptions: Option<PathBuf>,
    format: String,
    budget_override: Option<u64>,
    targets: Vec<PathBuf>,
}

fn parse_args(argv: &[String]) -> Result<Args, String> {
    let mut args = Args {
        policy: PathBuf::from("policy/audits.phext"),
        exceptions: None,
        format: "text".to_string(),
        budget_override: None,
        targets: Vec::new(),
    };
    let mut i = 0;
    while i < argv.len() {
        let a = &argv[i];
        let take = |i: &mut usize| -> Result<String, String> {
            *i += 1;
            argv.get(*i).cloned().ok_or_else(|| format!("missing value for {}", a))
        };
        match a.as_str() {
            "--policy" => args.policy = PathBuf::from(take(&mut i)?),
            "--exceptions" => args.exceptions = Some(PathBuf::from(take(&mut i)?)),
            "--format" => args.format = take(&mut i)?,
            "--budget" => {
                args.budget_override = Some(
                    take(&mut i)?
                        .parse::<u64>()
                        .map_err(|_| "bad --budget value".to_string())?,
                )
            }
            "--all" => {
                let list = take(&mut i)?;
                let text = std::fs::read_to_string(&list)
                    .map_err(|e| format!("cannot read {}: {}", list, e))?;
                for line in text.lines() {
                    let line = line.trim();
                    if !line.is_empty() && !line.starts_with('#') {
                        args.targets.push(PathBuf::from(line));
                    }
                }
            }
            "--scan" => {
                let dir = PathBuf::from(take(&mut i)?);
                args.targets.extend(scan_projects(&dir, 4));
            }
            "-h" | "--help" => {
                println!(
                    "usage: phext-dep-lint [--policy audits.phext] [--exceptions exceptions.toml]\n"
                );
                println!("                       [--format text|json] [--budget N]");
                println!("                       <project-dir>... | --all <list-file> | --scan <dir>");
                std::process::exit(0);
            }
            other if other.starts_with('-') => {
                return Err(format!("unknown flag {}", other));
            }
            other => args.targets.push(PathBuf::from(other)),
        }
        i += 1;
    }
    if args.targets.is_empty() {
        return Err("no project targets given".to_string());
    }
    Ok(args)
}

/// Find directories holding a Cargo.toml, up to `depth` levels deep,
/// skipping target/ and hidden dirs. Workspace member dirs of an
/// already-found root are dropped by the caller via member dedup.
fn scan_projects(dir: &Path, depth: usize) -> Vec<PathBuf> {
    let mut out = Vec::new();
    if depth == 0 || !dir.is_dir() {
        return out;
    }
    if dir.join("Cargo.toml").exists() {
        out.push(dir.to_path_buf());
    }
    if let Ok(rd) = std::fs::read_dir(dir) {
        let mut subs: Vec<PathBuf> = rd
            .flatten()
            .map(|e| e.path())
            .filter(|p| {
                p.is_dir()
                    && p.file_name()
                        .map(|n| {
                            let n = n.to_string_lossy();
                            n != "target" && !n.starts_with('.')
                        })
                        .unwrap_or(false)
            })
            .collect();
        subs.sort();
        for s in subs {
            out.extend(scan_projects(&s, depth - 1));
        }
    }
    out
}

fn lint_project(
    root: &Path,
    audits: &AuditSet,
    exceptions: &[Exception],
    budget_override: Option<u64>,
) -> ProjectReport {
    let mut violations: Vec<Violation> = Vec::new();
    let mut notes: Vec<String> = Vec::new();
    let mut applied: Vec<String> = Vec::new();

    let project = match manifest::load_project(root) {
        Ok(p) => p,
        Err(e) => {
            return ProjectReport {
                name: root
                    .file_name()
                    .map(|s| s.to_string_lossy().into_owned())
                    .unwrap_or_default(),
                path: root.display().to_string(),
                direct_count: 0,
                transitive_count: None,
                budget: 0,
                status: "fail".to_string(),
                violations: vec![Violation {
                    kind: "unreadable-project".to_string(),
                    krate: String::new(),
                    detail: e,
                    path: None,
                }],
                exceptions_applied: Vec::new(),
                notes: Vec::new(),
            };
        }
    };

    // Exceptions for this project; validate their audit references.
    let proj_exceptions: Vec<&Exception> = exceptions
        .iter()
        .filter(|e| e.project == project.name)
        .collect();
    let mut covered: BTreeSet<String> = BTreeSet::new();
    let mut budget_exception: Option<u64> = None;
    for e in &proj_exceptions {
        if let Some(k) = &e.krate {
            let ref_name = e.audit_ref.clone().unwrap_or_else(|| k.clone());
            if audits.audits.contains_key(&ref_name) {
                covered.insert(k.clone());
                applied.push(format!("{} — {}", k, e.reason));
            } else {
                violations.push(Violation {
                    kind: "invalid-exception".to_string(),
                    krate: k.clone(),
                    detail: format!(
                        "exception references audit {:?} which is not on record — exceptions must reference an audit",
                        ref_name
                    ),
                    path: None,
                });
            }
        }
        if let Some(b) = e.budget {
            budget_exception = Some(b);
            applied.push(format!("budget {} — {}", b, e.reason));
        }
    }

    let budget = budget_override
        .or(budget_exception)
        .or(audits.transitive_budget)
        .unwrap_or(60);

    // (a) direct dependencies: audited-pass or exception-covered.
    let mut direct_names: BTreeSet<String> = BTreeSet::new();
    for d in &project.direct_deps {
        direct_names.insert(d.name.clone());
        if covered.contains(&d.name) {
            continue;
        }
        match audits.verdict(&d.name) {
            Some(Verdict::Pass) => {}
            Some(Verdict::Fail) => violations.push(Violation {
                kind: "audit-failed-direct".to_string(),
                krate: d.name.clone(),
                detail: format!(
                    "audit on record with verdict FAIL (member {}, {} dep) — see audit scroll {}",
                    d.member,
                    d.kind,
                    audits
                        .audits
                        .get(&d.name)
                        .map(|a| a.coord.clone())
                        .unwrap_or_default()
                ),
                path: None,
            }),
            None => violations.push(Violation {
                kind: "unaudited-direct".to_string(),
                krate: d.name.clone(),
                detail: format!(
                    "no audit on record (member {}, {} dep)",
                    d.member, d.kind
                ),
                path: None,
            }),
        }
        // (d, manifest side) git deps and escaping path deps.
        match &d.source {
            DepSource::Git(url) => violations.push(Violation {
                kind: "unvendorable-source".to_string(),
                krate: d.name.clone(),
                detail: format!("git dependency {} (member {})", url, d.member),
                path: None,
            }),
            DepSource::Path(p) => {
                if path_escapes(root, p) {
                    violations.push(Violation {
                        kind: "unvendorable-source".to_string(),
                        krate: d.name.clone(),
                        detail: format!(
                            "path dependency {:?} escapes the project workspace (member {})",
                            p, d.member
                        ),
                        path: None,
                    });
                }
            }
            DepSource::OtherRegistry(r) => violations.push(Violation {
                kind: "unvendorable-source".to_string(),
                krate: d.name.clone(),
                detail: format!("non-crates.io registry {:?} (member {})", r, d.member),
                path: None,
            }),
            DepSource::Registry => {}
        }
    }

    // Lock-side checks: (b) budget, (c) duplicates, (d) sources,
    // and audit status of the transitive tree.
    let member_names: BTreeSet<String> =
        project.members.iter().map(|m| m.name.clone()).collect();
    let lock_path = project.root.join("Cargo.lock");
    let mut transitive_count: Option<usize> = None;
    if lock_path.exists() {
        match lock::load_lock(&lock_path, &member_names) {
            Ok(lk) => {
                let ext = lk.external_count();
                transitive_count = Some(ext);
                if ext as u64 > budget {
                    violations.push(Violation {
                        kind: "budget-exceeded".to_string(),
                        krate: String::new(),
                        detail: format!(
                            "transitive tree is {} packages, budget is {}",
                            ext, budget
                        ),
                        path: None,
                    });
                }
                for (name, versions) in lk.duplicates() {
                    violations.push(Violation {
                        kind: "duplicate-versions".to_string(),
                        krate: name,
                        detail: format!("versions in one tree: {}", versions.join(", ")),
                        path: None,
                    });
                }
                let mut seen_transitive: BTreeSet<String> = BTreeSet::new();
                for pkg in &lk.packages {
                    if pkg.source.is_none() {
                        continue; // workspace member
                    }
                    // (d) resolved source must be the crates.io registry.
                    let src = pkg.source.clone().unwrap_or_default();
                    if !src.starts_with("registry+https://github.com/rust-lang/crates.io-index") {
                        violations.push(Violation {
                            kind: "unvendorable-source".to_string(),
                            krate: pkg.name.clone(),
                            detail: format!("resolved source {}", src),
                            path: lk.path_to(&pkg.name),
                        });
                    }
                    // Audit status of transitive crates (direct ones
                    // were already judged above; report the rest).
                    if direct_names.contains(&pkg.name) || covered.contains(&pkg.name) {
                        continue;
                    }
                    if !seen_transitive.insert(pkg.name.clone()) {
                        continue;
                    }
                    match audits.verdict(&pkg.name) {
                        Some(Verdict::Pass) => {}
                        Some(Verdict::Fail) => violations.push(Violation {
                            kind: "audit-failed-transitive".to_string(),
                            krate: pkg.name.clone(),
                            detail: "audit on record with verdict FAIL".to_string(),
                            path: lk.path_to(&pkg.name),
                        }),
                        None => violations.push(Violation {
                            kind: "unaudited-transitive".to_string(),
                            krate: pkg.name.clone(),
                            detail: "no audit on record".to_string(),
                            path: lk.path_to(&pkg.name),
                        }),
                    }
                }
            }
            Err(e) => notes.push(format!("Cargo.lock unreadable: {}", e)),
        }
    } else {
        violations.push(Violation {
            kind: "no-lock".to_string(),
            krate: String::new(),
            detail: "no Cargo.lock — transitive tree unverifiable".to_string(),
            path: None,
        });
    }

    ProjectReport {
        name: project.name.clone(),
        path: root.display().to_string(),
        direct_count: direct_names.len(),
        transitive_count,
        budget,
        status: if violations.is_empty() {
            "pass".to_string()
        } else {
            "fail".to_string()
        },
        violations,
        exceptions_applied: applied,
        notes,
    }
}

fn path_escapes(root: &Path, rel: &str) -> bool {
    let p = Path::new(rel);
    if p.is_absolute() {
        return true;
    }
    // Normalize: any ".." that climbs above the project root escapes.
    let mut depth: i64 = 0;
    for comp in p.components() {
        match comp {
            std::path::Component::ParentDir => {
                depth -= 1;
                if depth < 0 {
                    return true;
                }
            }
            std::path::Component::Normal(_) => depth += 1,
            _ => {}
        }
    }
    let _ = root;
    false
}

// ---------- JSON output (hand-rolled, std only) ----------

fn json_escape(s: &str) -> String {
    let mut out = String::with_capacity(s.len() + 2);
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out
}

fn report_json(audits: &AuditSet, reports: &[ProjectReport]) -> String {
    let mut s = String::new();
    s.push_str("{\n  \"tool\": \"phext-dep-lint\",\n  \"mode\": \"report\",\n");
    s.push_str(&format!(
        "  \"policy\": {{\"audited_pass\": {}, \"audited_fail\": {}, \"transitive_budget\": {}}},\n",
        audits.pass_count(),
        audits.fail_count(),
        audits
            .transitive_budget
            .map(|b| b.to_string())
            .unwrap_or_else(|| "null".to_string())
    ));
    s.push_str("  \"projects\": [");
    for (i, r) in reports.iter().enumerate() {
        if i > 0 {
            s.push(',');
        }
        s.push_str("\n    {");
        s.push_str(&format!(
            "\"name\": \"{}\", \"path\": \"{}\", \"status\": \"{}\", \"direct_count\": {}, \"transitive_count\": {}, \"budget\": {}",
            json_escape(&r.name),
            json_escape(&r.path),
            r.status,
            r.direct_count,
            r.transitive_count
                .map(|n| n.to_string())
                .unwrap_or_else(|| "null".to_string()),
            r.budget
        ));
        s.push_str(", \"exceptions_applied\": [");
        for (j, e) in r.exceptions_applied.iter().enumerate() {
            if j > 0 {
                s.push_str(", ");
            }
            s.push_str(&format!("\"{}\"", json_escape(e)));
        }
        s.push_str("], \"violations\": [");
        for (j, v) in r.violations.iter().enumerate() {
            if j > 0 {
                s.push(',');
            }
            s.push_str("\n      {");
            s.push_str(&format!(
                "\"kind\": \"{}\", \"crate\": \"{}\", \"detail\": \"{}\"",
                json_escape(&v.kind),
                json_escape(&v.krate),
                json_escape(&v.detail)
            ));
            if let Some(p) = &v.path {
                s.push_str(", \"path\": [");
                for (k, step) in p.iter().enumerate() {
                    if k > 0 {
                        s.push_str(", ");
                    }
                    s.push_str(&format!("\"{}\"", json_escape(step)));
                }
                s.push(']');
            }
            s.push('}');
        }
        if !r.violations.is_empty() {
            s.push_str("\n    ");
        }
        s.push_str("]}");
    }
    s.push_str("\n  ]\n}\n");
    s
}

fn report_text(audits: &AuditSet, policy_path: &Path, reports: &[ProjectReport]) -> String {
    let mut s = String::new();
    s.push_str("phext-dep-lint — REPORT MODE (findings only; not wired as a gate)\n");
    s.push_str(&format!(
        "policy: {} — {} audits passing, {} failing on record; transitive budget {}\n",
        policy_path.display(),
        audits.pass_count(),
        audits.fail_count(),
        audits
            .transitive_budget
            .map(|b| b.to_string())
            .unwrap_or_else(|| "unset".to_string())
    ));
    let failed = reports.iter().filter(|r| r.status == "fail").count();
    s.push_str(&format!(
        "projects: {} checked, {} passing, {} failing\n",
        reports.len(),
        reports.len() - failed,
        failed
    ));
    for r in reports {
        s.push_str(&format!(
            "\n== {} ({})\n   direct: {} · transitive: {} · budget: {} · status: {}\n",
            r.name,
            r.path,
            r.direct_count,
            r.transitive_count
                .map(|n| n.to_string())
                .unwrap_or_else(|| "unknown (no lock)".to_string()),
            r.budget,
            r.status.to_uppercase()
        ));
        for e in &r.exceptions_applied {
            s.push_str(&format!("   exception applied: {}\n", e));
        }
        for n in &r.notes {
            s.push_str(&format!("   note: {}\n", n));
        }
        // Group violations by kind for readability.
        let mut by_kind: BTreeMap<&str, Vec<&Violation>> = BTreeMap::new();
        for v in &r.violations {
            by_kind.entry(v.kind.as_str()).or_default().push(v);
        }
        for (kind, vs) in by_kind {
            s.push_str(&format!("   [{}] ×{}\n", kind, vs.len()));
            for v in vs {
                if v.krate.is_empty() {
                    s.push_str(&format!("     - {}\n", v.detail));
                } else {
                    s.push_str(&format!("     - {} — {}\n", v.krate, v.detail));
                }
                if let Some(p) = &v.path {
                    s.push_str(&format!("       via {}\n", p.join(" → ")));
                }
            }
        }
    }
    s
}

fn main() -> ExitCode {
    let argv: Vec<String> = std::env::args().skip(1).collect();
    let args = match parse_args(&argv) {
        Ok(a) => a,
        Err(e) => {
            eprintln!("phext-dep-lint: {}", e);
            return ExitCode::from(2);
        }
    };
    let audits = match policy::load_audits(&args.policy) {
        Ok(a) => a,
        Err(e) => {
            eprintln!("phext-dep-lint: {}", e);
            return ExitCode::from(2);
        }
    };
    let exceptions = match &args.exceptions {
        Some(p) => match policy::load_exceptions(p) {
            Ok(e) => e,
            Err(e) => {
                eprintln!("phext-dep-lint: {}", e);
                return ExitCode::from(2);
            }
        },
        None => Vec::new(),
    };

    // Dedup targets that are members of an already-included workspace.
    let mut targets: Vec<PathBuf> = Vec::new();
    let mut member_dirs: BTreeSet<PathBuf> = BTreeSet::new();
    let mut sorted = args.targets.clone();
    sorted.sort();
    for t in sorted {
        let canon = t.canonicalize().unwrap_or_else(|_| t.clone());
        if member_dirs.contains(&canon) {
            continue;
        }
        if let Ok(p) = manifest::load_project(&t) {
            for m in &p.members {
                if m.dir != t {
                    if let Ok(c) = m.dir.canonicalize() {
                        member_dirs.insert(c);
                    }
                }
            }
        }
        targets.push(t);
    }

    let mut reports = Vec::new();
    let mut any_fail = false;
    for t in &targets {
        let r = lint_project(t, &audits, &exceptions, args.budget_override);
        if r.status == "fail" {
            any_fail = true;
        }
        reports.push(r);
    }

    if args.format == "json" {
        print!("{}", report_json(&audits, &reports));
    } else {
        print!("{}", report_text(&audits, &args.policy, &reports));
    }
    if any_fail {
        ExitCode::from(1)
    } else {
        ExitCode::SUCCESS
    }
}
