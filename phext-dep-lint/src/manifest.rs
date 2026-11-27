//! Project model: read a Cargo workspace (root manifest + members)
//! and expose its direct dependencies, from scratch on std only.

use crate::toml::{self, Document, Value};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, PartialEq)]
pub enum DepSource {
    Registry,
    Git(String),
    Path(String),
    OtherRegistry(String),
}

#[derive(Debug, Clone)]
pub struct DirectDep {
    /// Real crate name (after `package =` rename resolution).
    pub name: String,
    /// Key as written in the manifest.
    pub key: String,
    /// Workspace member (package name) declaring it.
    pub member: String,
    /// "normal" | "dev" | "build"
    pub kind: String,
    pub source: DepSource,
    pub optional: bool,
}

#[derive(Debug, Clone)]
pub struct Member {
    pub name: String,
    pub dir: PathBuf,
}

#[derive(Debug, Clone)]
pub struct Project {
    pub root: PathBuf,
    pub name: String,
    pub members: Vec<Member>,
    pub direct_deps: Vec<DirectDep>,
}

fn read_doc(path: &Path) -> Result<Document, String> {
    let text = std::fs::read_to_string(path)
        .map_err(|e| format!("cannot read {}: {}", path.display(), e))?;
    toml::parse(&text).map_err(|e| format!("{}: {}", path.display(), e))
}

fn dep_from_value(
    key: &str,
    v: &Value,
    member: &str,
    kind: &str,
    workspace_deps: &BTreeMap<String, Value>,
) -> Option<DirectDep> {
    match v {
        Value::Str(_) => Some(DirectDep {
            name: key.to_string(),
            key: key.to_string(),
            member: member.to_string(),
            kind: kind.to_string(),
            source: DepSource::Registry,
            optional: false,
        }),
        Value::Table(t) => {
            let get = |k: &str| t.iter().find(|(n, _)| n == k).map(|(_, val)| val);
            if let Some(Value::Bool(true)) = get("workspace") {
                // Inherited: resolve against [workspace.dependencies].
                if let Some(wv) = workspace_deps.get(key) {
                    let mut d = dep_from_value(key, wv, member, kind, workspace_deps)?;
                    d.key = key.to_string();
                    return Some(d);
                }
                return None;
            }
            let name = get("package")
                .and_then(|p| p.as_str())
                .unwrap_or(key)
                .to_string();
            let source = if let Some(g) = get("git") {
                DepSource::Git(g.as_str().unwrap_or("").to_string())
            } else if let Some(p) = get("path") {
                DepSource::Path(p.as_str().unwrap_or("").to_string())
            } else if let Some(r) = get("registry") {
                DepSource::OtherRegistry(r.as_str().unwrap_or("").to_string())
            } else {
                DepSource::Registry
            };
            let optional = matches!(get("optional"), Some(Value::Bool(true)));
            Some(DirectDep {
                name,
                key: key.to_string(),
                member: member.to_string(),
                kind: kind.to_string(),
                source,
                optional,
            })
        }
        _ => None,
    }
}

fn collect_deps(
    doc: &Document,
    member: &str,
    workspace_deps: &BTreeMap<String, Value>,
    out: &mut Vec<DirectDep>,
) {
    for table in &doc.tables {
        let path: Vec<&str> = table.path.iter().map(|s| s.as_str()).collect();
        let kind = match path.as_slice() {
            ["dependencies"] => Some("normal"),
            ["dev-dependencies"] => Some("dev"),
            ["build-dependencies"] => Some("build"),
            ["target", _, "dependencies"] => Some("normal"),
            ["target", _, "dev-dependencies"] => Some("dev"),
            ["target", _, "build-dependencies"] => Some("build"),
            _ => None,
        };
        if let Some(kind) = kind {
            for (key, v) in &table.entries {
                if let Some(d) = dep_from_value(key, v, member, kind, workspace_deps) {
                    out.push(d);
                }
            }
        }
    }
}

fn expand_members(root: &Path, patterns: &[String]) -> Vec<PathBuf> {
    let mut dirs = Vec::new();
    for pat in patterns {
        if let Some(prefix) = pat.strip_suffix("/*") {
            let base = root.join(prefix);
            if let Ok(rd) = std::fs::read_dir(&base) {
                let mut subs: Vec<PathBuf> = rd
                    .flatten()
                    .map(|e| e.path())
                    .filter(|p| p.is_dir() && p.join("Cargo.toml").exists())
                    .collect();
                subs.sort();
                dirs.extend(subs);
            }
        } else if !pat.contains('*') {
            let d = root.join(pat);
            if d.join("Cargo.toml").exists() {
                dirs.push(d);
            }
        }
    }
    dirs
}

/// Load the project rooted at `root` (the directory holding the
/// workspace or single-crate Cargo.toml).
pub fn load_project(root: &Path) -> Result<Project, String> {
    let root_doc = read_doc(&root.join("Cargo.toml"))?;
    let mut workspace_deps: BTreeMap<String, Value> = BTreeMap::new();
    if let Some(t) = root_doc.table_at(&["workspace", "dependencies"]) {
        for (k, v) in &t.entries {
            workspace_deps.insert(k.clone(), v.clone());
        }
    }

    let mut member_dirs: Vec<PathBuf> = Vec::new();
    let mut project_name = String::new();
    let has_package = root_doc.table_at(&["package"]).is_some();
    if let Some(ws) = root_doc.table_at(&["workspace"]) {
        if let Some(Value::Array(items)) = ws.get("members") {
            let patterns: Vec<String> = items
                .iter()
                .filter_map(|v| v.as_str().map(|s| s.to_string()))
                .collect();
            member_dirs = expand_members(root, &patterns);
        }
    }
    if has_package {
        member_dirs.insert(0, root.to_path_buf());
    }
    if member_dirs.is_empty() {
        member_dirs.push(root.to_path_buf());
    }
    member_dirs.sort();
    member_dirs.dedup();

    let mut members = Vec::new();
    let mut direct_deps = Vec::new();
    for dir in &member_dirs {
        let doc = if *dir == root {
            root_doc.clone()
        } else {
            read_doc(&dir.join("Cargo.toml"))?
        };
        let name = doc
            .table_at(&["package"])
            .and_then(|t| t.get("name"))
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        if project_name.is_empty() {
            project_name = name.clone();
        }
        collect_deps(&doc, &name, &workspace_deps, &mut direct_deps);
        members.push(Member {
            name,
            dir: dir.clone(),
        });
    }
    if project_name.is_empty() {
        project_name = root
            .file_name()
            .map(|s| s.to_string_lossy().into_owned())
            .unwrap_or_else(|| "project".to_string());
    }
    Ok(Project {
        root: root.to_path_buf(),
        name: project_name,
        members,
        direct_deps,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn workspace_inheritance_and_rename() {
        let base = std::env::temp_dir().join("pdl-manifest-test");
        let _ = fs::remove_dir_all(&base);
        fs::create_dir_all(base.join("crates/a")).unwrap();
        fs::write(
            base.join("Cargo.toml"),
            r#"
[workspace]
members = ["crates/*"]
[workspace.dependencies]
serde = "1.0"
"#,
        )
        .unwrap();
        fs::write(
            base.join("crates/a/Cargo.toml"),
            r#"
[package]
name = "a"
version = "0.1.0"
[dependencies]
serde = { workspace = true }
renamed = { package = "real-crate", version = "2" }
"#,
        )
        .unwrap();
        let p = load_project(&base).unwrap();
        assert_eq!(p.members.len(), 1);
        let names: Vec<&str> = p.direct_deps.iter().map(|d| d.name.as_str()).collect();
        assert!(names.contains(&"serde"));
        assert!(names.contains(&"real-crate"));
        let _ = fs::remove_dir_all(&base);
    }
}
