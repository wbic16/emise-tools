//! Cargo.lock model: packages, the resolved dependency graph, and
//! shortest-path inversion (who pulled a crate in), on std only.

use crate::toml;
use std::collections::{BTreeMap, BTreeSet, HashMap, VecDeque};
use std::path::Path;

#[derive(Debug, Clone)]
pub struct Package {
    pub name: String,
    pub version: String,
    /// Lock `source` string; None for path/workspace members.
    pub source: Option<String>,
    /// Raw dependency strings as written in the lock.
    pub dep_strings: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct Lock {
    pub packages: Vec<Package>,
    /// package index -> resolved dependency package indices
    pub edges: Vec<Vec<usize>>,
    /// indices of workspace-member packages (no source, name matches a member)
    pub roots: Vec<usize>,
}

fn parse_dep_string(s: &str) -> (String, Option<String>) {
    // Forms: "name", "name version", "name version (source)".
    let mut parts = s.splitn(3, ' ');
    let name = parts.next().unwrap_or("").to_string();
    let version = parts.next().map(|v| v.to_string());
    (name, version)
}

pub fn load_lock(path: &Path, member_names: &BTreeSet<String>) -> Result<Lock, String> {
    let text = std::fs::read_to_string(path)
        .map_err(|e| format!("cannot read {}: {}", path.display(), e))?;
    let doc = toml::parse(&text).map_err(|e| format!("{}: {}", path.display(), e))?;
    let mut packages = Vec::new();
    for t in doc.tables_at(&["package"]) {
        let name = t
            .get("name")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        let version = t
            .get("version")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        let source = t.get("source").and_then(|v| v.as_str()).map(|s| s.to_string());
        let dep_strings = match t.get("dependencies") {
            Some(toml::Value::Array(items)) => items
                .iter()
                .filter_map(|v| v.as_str().map(|s| s.to_string()))
                .collect(),
            _ => Vec::new(),
        };
        packages.push(Package {
            name,
            version,
            source,
            dep_strings,
        });
    }
    // Index by (name, version) and by name.
    let mut by_nv: HashMap<(String, String), usize> = HashMap::new();
    let mut by_name: HashMap<String, Vec<usize>> = HashMap::new();
    for (i, p) in packages.iter().enumerate() {
        by_nv.insert((p.name.clone(), p.version.clone()), i);
        by_name.entry(p.name.clone()).or_default().push(i);
    }
    let mut edges: Vec<Vec<usize>> = vec![Vec::new(); packages.len()];
    for (i, p) in packages.iter().enumerate() {
        for ds in &p.dep_strings {
            let (dn, dv) = parse_dep_string(ds);
            let target = match &dv {
                Some(v) => by_nv.get(&(dn.clone(), v.clone())).copied(),
                None => by_name
                    .get(&dn)
                    .and_then(|v| if v.len() == 1 { Some(v[0]) } else { None }),
            };
            if let Some(t) = target {
                edges[i].push(t);
            }
        }
    }
    let roots = packages
        .iter()
        .enumerate()
        .filter(|(_, p)| p.source.is_none() && member_names.contains(&p.name))
        .map(|(i, _)| i)
        .collect();
    Ok(Lock {
        packages,
        edges,
        roots,
    })
}

impl Lock {
    /// External (non-workspace) resolved packages.
    pub fn external_count(&self) -> usize {
        self.packages.iter().filter(|p| p.source.is_some()).count()
    }

    /// Crate names appearing at two or more distinct versions.
    pub fn duplicates(&self) -> BTreeMap<String, Vec<String>> {
        let mut m: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
        for p in &self.packages {
            m.entry(p.name.clone()).or_default().insert(p.version.clone());
        }
        m.into_iter()
            .filter(|(_, vs)| vs.len() > 1)
            .map(|(k, vs)| (k, vs.into_iter().collect()))
            .collect()
    }

    /// Shortest path from any workspace root to the named crate,
    /// as a chain of "name version" strings (root first). None when
    /// the crate is not reachable (or not present).
    pub fn path_to(&self, crate_name: &str) -> Option<Vec<String>> {
        let targets: Vec<usize> = self
            .packages
            .iter()
            .enumerate()
            .filter(|(_, p)| p.name == crate_name)
            .map(|(i, _)| i)
            .collect();
        if targets.is_empty() {
            return None;
        }
        let target_set: BTreeSet<usize> = targets.iter().copied().collect();
        let mut prev: HashMap<usize, usize> = HashMap::new();
        let mut queue: VecDeque<usize> = VecDeque::new();
        let mut seen: BTreeSet<usize> = BTreeSet::new();
        for &r in &self.roots {
            if seen.insert(r) {
                queue.push_back(r);
            }
        }
        let mut found: Option<usize> = None;
        while let Some(u) = queue.pop_front() {
            if target_set.contains(&u) && !self.roots.contains(&u) {
                found = Some(u);
                break;
            }
            for &v in &self.edges[u] {
                if seen.insert(v) {
                    prev.insert(v, u);
                    queue.push_back(v);
                }
            }
        }
        let mut node = found?;
        let mut chain = vec![node];
        while let Some(&p) = prev.get(&node) {
            chain.push(p);
            node = p;
        }
        chain.reverse();
        Some(
            chain
                .iter()
                .map(|&i| format!("{} {}", self.packages[i].name, self.packages[i].version))
                .collect(),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn graph_and_duplicates() {
        let dir = std::env::temp_dir().join("pdl-lock-test");
        let _ = fs::remove_dir_all(&dir);
        fs::create_dir_all(&dir).unwrap();
        let lock = dir.join("Cargo.lock");
        fs::write(
            &lock,
            r#"
version = 3
[[package]]
name = "root"
version = "0.1.0"
dependencies = ["mid"]
[[package]]
name = "mid"
version = "1.0.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
dependencies = ["leaf 0.1.0", "leaf 0.2.0"]
[[package]]
name = "leaf"
version = "0.1.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
[[package]]
name = "leaf"
version = "0.2.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
"#,
        )
        .unwrap();
        let members: BTreeSet<String> = ["root".to_string()].into_iter().collect();
        let l = load_lock(&lock, &members).unwrap();
        assert_eq!(l.external_count(), 3);
        let dups = l.duplicates();
        assert_eq!(dups.get("leaf").map(|v| v.len()), Some(2));
        let path = l.path_to("leaf").unwrap();
        assert_eq!(path[0], "root 0.1.0");
        assert_eq!(path[1], "mid 1.0.0");
        let _ = fs::remove_dir_all(&dir);
    }
}
