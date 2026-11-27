//! Policy: the audit phext is the source of truth.
//!
//! One scroll per crate records what the crate is, its own transitive
//! tree, why it is needed, and a verdict. A crate is allowed only when
//! a scroll exists with `verdict: pass`. No scroll = "no audit on
//! record" = denied. The home scroll (1.1.1/1.1.1/1.1.1) carries the
//! policy knobs, currently `transitive-budget: N`.
//!
//! Per-project exceptions live in exceptions.toml. An exception is
//! recorded, never silent, and must reference an audit scroll that
//! exists — an exception pointing at nothing is itself a violation.

use crate::phext;
use crate::toml;
use std::collections::BTreeMap;
use std::path::Path;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Verdict {
    Pass,
    Fail,
}

#[derive(Debug, Clone)]
pub struct Audit {
    pub verdict: Verdict,
    pub coord: String,
}

#[derive(Debug, Default)]
pub struct AuditSet {
    pub audits: BTreeMap<String, Audit>,
    pub transitive_budget: Option<u64>,
}

fn scroll_fields(text: &str) -> BTreeMap<String, String> {
    let mut m = BTreeMap::new();
    for line in text.lines() {
        if let Some((k, v)) = line.split_once(':') {
            let key = k.trim().to_lowercase();
            if !key.is_empty() && key.chars().all(|c| c.is_alphanumeric() || c == '-' || c == '_') {
                m.entry(key).or_insert_with(|| v.trim().to_string());
            }
        }
    }
    m
}

pub fn load_audits(path: &Path) -> Result<AuditSet, String> {
    let bytes = std::fs::read(path)
        .map_err(|e| format!("cannot read audit phext {}: {}", path.display(), e))?;
    let scrolls = phext::parse(&bytes);
    let mut set = AuditSet::default();
    for s in scrolls {
        let fields = scroll_fields(&s.text);
        if s.coord == [1; 9] {
            if let Some(b) = fields.get("transitive-budget") {
                set.transitive_budget = b.parse::<u64>().ok();
            }
            continue;
        }
        if let Some(krat) = fields.get("crate") {
            let verdict = match fields.get("verdict").map(|v| v.to_lowercase()) {
                Some(v) if v == "pass" => Some(Verdict::Pass),
                Some(v) if v == "fail" => Some(Verdict::Fail),
                _ => None,
            };
            if let Some(verdict) = verdict {
                set.audits.insert(
                    krat.clone(),
                    Audit {
                        verdict,
                        coord: s.coord_string(),
                    },
                );
            }
        }
    }
    Ok(set)
}

impl AuditSet {
    pub fn verdict(&self, krate: &str) -> Option<Verdict> {
        self.audits.get(krate).map(|a| a.verdict)
    }
    pub fn pass_count(&self) -> usize {
        self.audits
            .values()
            .filter(|a| a.verdict == Verdict::Pass)
            .count()
    }
    pub fn fail_count(&self) -> usize {
        self.audits
            .values()
            .filter(|a| a.verdict == Verdict::Fail)
            .count()
    }
}

#[derive(Debug, Clone)]
pub struct Exception {
    pub project: String,
    /// Crate the exception covers; None for budget exceptions.
    pub krate: Option<String>,
    pub budget: Option<u64>,
    pub reason: String,
    /// Audit scroll the exception references (defaults to the crate).
    pub audit_ref: Option<String>,
}

pub fn load_exceptions(path: &Path) -> Result<Vec<Exception>, String> {
    let text = std::fs::read_to_string(path)
        .map_err(|e| format!("cannot read exceptions {}: {}", path.display(), e))?;
    let doc = toml::parse(&text).map_err(|e| format!("{}: {}", path.display(), e))?;
    let mut out = Vec::new();
    for t in doc.tables_at(&["exception"]) {
        let project = t
            .get("project")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        let krate = t.get("crate").and_then(|v| v.as_str()).map(|s| s.to_string());
        let budget = t.get("budget").and_then(|v| match v {
            toml::Value::Int(i) => Some(*i as u64),
            _ => None,
        });
        let reason = t
            .get("reason")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        let audit_ref = t
            .get("audit")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());
        out.push(Exception {
            project,
            krate,
            budget,
            reason,
            audit_ref,
        });
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn audits_and_budget() {
        let dir = std::env::temp_dir().join("pdl-policy-test");
        let _ = fs::remove_dir_all(&dir);
        fs::create_dir_all(&dir).unwrap();
        let mut bytes = b"transitive-budget: 40\n".to_vec();
        bytes.push(crate::phext::LEVEL_BYTES[4]); // volume -> 2
        bytes.extend_from_slice(b"crate: serde\nverdict: pass\n");
        bytes.push(crate::phext::LEVEL_BYTES[4]);
        bytes.extend_from_slice(b"crate: badcrate\nverdict: fail\n");
        let p = dir.join("audits.phext");
        fs::write(&p, &bytes).unwrap();
        let set = load_audits(&p).unwrap();
        assert_eq!(set.transitive_budget, Some(40));
        assert_eq!(set.verdict("serde"), Some(Verdict::Pass));
        assert_eq!(set.verdict("badcrate"), Some(Verdict::Fail));
        assert_eq!(set.verdict("ghost"), None);
        let _ = fs::remove_dir_all(&dir);
    }
}
