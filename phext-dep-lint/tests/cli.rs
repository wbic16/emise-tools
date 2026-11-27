//! End-to-end tests: fixture projects that pass and fail each rule.
//! Fixtures are generated in temp dirs so the suite is self-contained.

use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

const SCROLL_DELIM: u8 = 0x17;
const VOLUME_DELIM: u8 = 0x1C;

fn build_policy(dir: &Path) -> PathBuf {
    // home scroll (budget 60), then one volume per crate audit:
    // mid = pass, raw_sync = fail.
    let mut bytes = b"transitive-budget: 60\n".to_vec();
    bytes.push(VOLUME_DELIM);
    bytes.extend_from_slice(b"crate: mid\nverdict: pass\n");
    bytes.push(VOLUME_DELIM);
    bytes.extend_from_slice(b"crate: raw_sync\nverdict: fail\n");
    let p = dir.join("audits.phext");
    fs::write(&p, bytes).unwrap();
    p
}

fn write_project(dir: &Path, manifest: &str, lock: Option<&str>) -> PathBuf {
    fs::create_dir_all(dir).unwrap();
    fs::write(dir.join("Cargo.toml"), manifest).unwrap();
    if let Some(l) = lock {
        fs::write(dir.join("Cargo.lock"), l).unwrap();
    }
    dir.to_path_buf()
}

fn run(policy: &Path, extra: &[&str], target: &Path) -> (String, i32) {
    let bin = env!("CARGO_BIN_EXE_phext-dep-lint");
    let mut cmd = Command::new(bin);
    cmd.arg("--policy").arg(policy);
    for a in extra {
        cmd.arg(a);
    }
    cmd.arg(target);
    let out = cmd.output().unwrap();
    (
        String::from_utf8_lossy(&out.stdout).into_owned(),
        out.status.code().unwrap_or(-1),
    )
}

fn tmp(name: &str) -> PathBuf {
    let d = std::env::temp_dir().join(format!("pdl-cli-{}", name));
    let _ = fs::remove_dir_all(&d);
    fs::create_dir_all(&d).unwrap();
    d
}

const REG: &str = "registry+https://github.com/rust-lang/crates.io-index";

#[test]
fn pass_clean_project() {
    let d = tmp("pass-clean");
    let policy = build_policy(&d);
    let proj = write_project(
        &d.join("p"),
        "[package]\nname = \"p\"\nversion = \"0.1.0\"\n",
        Some("version = 3\n[[package]]\nname = \"p\"\nversion = \"0.1.0\"\n"),
    );
    let (out, code) = run(&policy, &[], &proj);
    assert_eq!(code, 0, "{}", out);
    assert!(out.contains("status: PASS"), "{}", out);
}

#[test]
fn fail_unaudited_direct() {
    let d = tmp("fail-unaudited");
    let policy = build_policy(&d);
    let lock = format!(
        "version = 3\n[[package]]\nname = \"p\"\nversion = \"0.1.0\"\ndependencies = [\"ghostcrate\"]\n[[package]]\nname = \"ghostcrate\"\nversion = \"1.0.0\"\nsource = \"{}\"\n",
        REG
    );
    let proj = write_project(
        &d.join("p"),
        "[package]\nname = \"p\"\nversion = \"0.1.0\"\n[dependencies]\nghostcrate = \"1\"\n",
        Some(&lock),
    );
    let (out, code) = run(&policy, &[], &proj);
    assert_eq!(code, 1);
    assert!(out.contains("[unaudited-direct]"), "{}", out);
    assert!(out.contains("no audit on record"), "{}", out);
}

#[test]
fn fail_duplicate_versions() {
    let d = tmp("fail-dup");
    let policy = build_policy(&d);
    let lock = format!(
        "version = 3\n\
         [[package]]\nname = \"p\"\nversion = \"0.1.0\"\ndependencies = [\"mid\"]\n\
         [[package]]\nname = \"mid\"\nversion = \"1.0.0\"\nsource = \"{r}\"\ndependencies = [\"leaf 0.1.0\", \"leaf 0.2.0\"]\n\
         [[package]]\nname = \"leaf\"\nversion = \"0.1.0\"\nsource = \"{r}\"\n\
         [[package]]\nname = \"leaf\"\nversion = \"0.2.0\"\nsource = \"{r}\"\n",
        r = REG
    );
    let proj = write_project(
        &d.join("p"),
        "[package]\nname = \"p\"\nversion = \"0.1.0\"\n[dependencies]\nmid = \"1\"\n",
        Some(&lock),
    );
    let (out, code) = run(&policy, &[], &proj);
    assert_eq!(code, 1);
    assert!(out.contains("[duplicate-versions]"), "{}", out);
    assert!(out.contains("0.1.0, 0.2.0"), "{}", out);
}

#[test]
fn fail_budget_exceeded() {
    let d = tmp("fail-budget");
    let policy = build_policy(&d);
    let mut lock = String::from(
        "version = 3\n[[package]]\nname = \"p\"\nversion = \"0.1.0\"\ndependencies = [\"mid\"]\n",
    );
    lock.push_str(&format!(
        "[[package]]\nname = \"mid\"\nversion = \"1.0.0\"\nsource = \"{}\"\ndependencies = [\"a1\", \"a2\", \"a3\"]\n",
        REG
    ));
    for a in ["a1", "a2", "a3"] {
        lock.push_str(&format!(
            "[[package]]\nname = \"{}\"\nversion = \"1.0.0\"\nsource = \"{}\"\n",
            a, REG
        ));
    }
    let proj = write_project(
        &d.join("p"),
        "[package]\nname = \"p\"\nversion = \"0.1.0\"\n[dependencies]\nmid = \"1\"\n",
        Some(&lock),
    );
    let (out, code) = run(&policy, &["--budget", "2"], &proj);
    assert_eq!(code, 1);
    assert!(out.contains("[budget-exceeded]"), "{}", out);
}

#[test]
fn fail_git_dependency() {
    let d = tmp("fail-git");
    let policy = build_policy(&d);
    let proj = write_project(
        &d.join("p"),
        "[package]\nname = \"p\"\nversion = \"0.1.0\"\n[dependencies]\ngitdep = { git = \"https://example.com/gitdep\" }\n",
        Some("version = 3\n[[package]]\nname = \"p\"\nversion = \"0.1.0\"\n"),
    );
    let (out, code) = run(&policy, &[], &proj);
    assert_eq!(code, 1);
    assert!(out.contains("[unvendorable-source]"), "{}", out);
    assert!(out.contains("git dependency"), "{}", out);
}

#[test]
fn fail_audit_failed_direct_without_exception() {
    let d = tmp("fail-verdict");
    let policy = build_policy(&d);
    let lock = format!(
        "version = 3\n[[package]]\nname = \"p\"\nversion = \"0.1.0\"\ndependencies = [\"raw_sync\"]\n[[package]]\nname = \"raw_sync\"\nversion = \"0.1.5\"\nsource = \"{}\"\n",
        REG
    );
    let proj = write_project(
        &d.join("p"),
        "[package]\nname = \"p\"\nversion = \"0.1.0\"\n[dependencies]\nraw_sync = \"0.1\"\n",
        Some(&lock),
    );
    let (out, code) = run(&policy, &[], &proj);
    assert_eq!(code, 1);
    assert!(out.contains("[audit-failed-direct]"), "{}", out);
}

#[test]
fn pass_with_recorded_exception() {
    let d = tmp("pass-exception");
    let policy = build_policy(&d);
    let lock = format!(
        "version = 3\n[[package]]\nname = \"p\"\nversion = \"0.1.0\"\ndependencies = [\"raw_sync\"]\n[[package]]\nname = \"raw_sync\"\nversion = \"0.1.5\"\nsource = \"{}\"\n",
        REG
    );
    let proj = write_project(
        &d.join("p"),
        "[package]\nname = \"p\"\nversion = \"0.1.0\"\n[dependencies]\nraw_sync = \"0.1\"\n",
        Some(&lock),
    );
    let exc = d.join("exceptions.toml");
    fs::write(
        &exc,
        "[[exception]]\nproject = \"p\"\ncrate = \"raw_sync\"\naudit = \"raw_sync\"\nreason = \"recorded test exception\"\n",
    )
    .unwrap();
    let (out, code) = run(&policy, &["--exceptions", exc.to_str().unwrap()], &proj);
    assert_eq!(code, 0, "{}", out);
    assert!(out.contains("exception applied: raw_sync"), "{}", out);
}

#[test]
fn fail_exception_referencing_missing_audit() {
    let d = tmp("fail-bad-exception");
    let policy = build_policy(&d);
    let lock = format!(
        "version = 3\n[[package]]\nname = \"p\"\nversion = \"0.1.0\"\ndependencies = [\"raw_sync\"]\n[[package]]\nname = \"raw_sync\"\nversion = \"0.1.5\"\nsource = \"{}\"\n",
        REG
    );
    let proj = write_project(
        &d.join("p"),
        "[package]\nname = \"p\"\nversion = \"0.1.0\"\n[dependencies]\nraw_sync = \"0.1\"\n",
        Some(&lock),
    );
    let exc = d.join("exceptions.toml");
    fs::write(
        &exc,
        "[[exception]]\nproject = \"p\"\ncrate = \"raw_sync\"\naudit = \"no-such-audit\"\nreason = \"points at nothing\"\n",
    )
    .unwrap();
    let (out, code) = run(&policy, &["--exceptions", exc.to_str().unwrap()], &proj);
    assert_eq!(code, 1);
    assert!(out.contains("[invalid-exception]"), "{}", out);
}

#[test]
fn fail_unaudited_transitive_reports_path() {
    let d = tmp("fail-transitive");
    let policy = build_policy(&d);
    let lock = format!(
        "version = 3\n\
         [[package]]\nname = \"p\"\nversion = \"0.1.0\"\ndependencies = [\"mid\"]\n\
         [[package]]\nname = \"mid\"\nversion = \"1.0.0\"\nsource = \"{r}\"\ndependencies = [\"sneaky\"]\n\
         [[package]]\nname = \"sneaky\"\nversion = \"3.0.0\"\nsource = \"{r}\"\n",
        r = REG
    );
    let proj = write_project(
        &d.join("p"),
        "[package]\nname = \"p\"\nversion = \"0.1.0\"\n[dependencies]\nmid = \"1\"\n",
        Some(&lock),
    );
    let (out, code) = run(&policy, &[], &proj);
    assert_eq!(code, 1);
    assert!(out.contains("[unaudited-transitive]"), "{}", out);
    assert!(out.contains("p 0.1.0 → mid 1.0.0 → sneaky 3.0.0"), "{}", out);
}

#[test]
fn json_format_is_wellformed() {
    let d = tmp("json");
    let policy = build_policy(&d);
    let proj = write_project(
        &d.join("p"),
        "[package]\nname = \"p\"\nversion = \"0.1.0\"\n",
        Some("version = 3\n[[package]]\nname = \"p\"\nversion = \"0.1.0\"\n"),
    );
    let bin = env!("CARGO_BIN_EXE_phext-dep-lint");
    let out = Command::new(bin)
        .arg("--policy")
        .arg(&policy)
        .arg("--format")
        .arg("json")
        .arg(&proj)
        .output()
        .unwrap();
    let s = String::from_utf8_lossy(&out.stdout).into_owned();
    assert!(s.contains("\"tool\": \"phext-dep-lint\""), "{}", s);
    assert!(s.contains("\"status\": \"pass\""), "{}", s);
    // crude balance check
    assert_eq!(s.matches('{').count(), s.matches('}').count());
    let _ = SCROLL_DELIM;
}
