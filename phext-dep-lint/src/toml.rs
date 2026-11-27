//! A small TOML reader, written from scratch on std only.
//!
//! It covers the subset of TOML that Cargo manifests, Cargo.lock, and
//! this tool's own policy files actually use: section and
//! array-of-tables headers, dotted and quoted keys, basic and literal
//! strings, integers, booleans, arrays, and inline tables. It is a
//! reader for linting, not a general TOML implementation.

use std::fmt;

#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Str(String),
    Int(i64),
    Bool(bool),
    Array(Vec<Value>),
    Table(Vec<(String, Value)>),
}

impl Value {
    pub fn as_str(&self) -> Option<&str> {
        match self {
            Value::Str(s) => Some(s),
            _ => None,
        }
    }
    pub fn as_table(&self) -> Option<&Vec<(String, Value)>> {
        match self {
            Value::Table(t) => Some(t),
            _ => None,
        }
    }
    pub fn get<'a>(&'a self, key: &str) -> Option<&'a Value> {
        self.as_table()
            .and_then(|t| t.iter().find(|(k, _)| k == key).map(|(_, v)| v))
    }
}

#[derive(Debug, Clone)]
pub struct Table {
    /// Section path, e.g. ["dependencies"] or ["target", "cfg(..)", "dependencies"].
    pub path: Vec<String>,
    pub entries: Vec<(String, Value)>,
}

impl Table {
    pub fn get<'a>(&'a self, key: &str) -> Option<&'a Value> {
        self.entries.iter().find(|(k, _)| k == key).map(|(_, v)| v)
    }
}

#[derive(Debug, Clone, Default)]
pub struct Document {
    pub tables: Vec<Table>,
}

impl Document {
    /// All tables whose path equals `path` exactly.
    pub fn tables_at<'a>(&'a self, path: &[&str]) -> Vec<&'a Table> {
        self.tables
            .iter()
            .filter(|t| t.path.iter().map(|s| s.as_str()).collect::<Vec<_>>() == path)
            .collect()
    }
    /// The first table at `path`, if any.
    pub fn table_at<'a>(&'a self, path: &[&str]) -> Option<&'a Table> {
        self.tables_at(path).into_iter().next()
    }
}

#[derive(Debug)]
pub struct ParseError(pub String);

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "toml parse error: {}", self.0)
    }
}
impl std::error::Error for ParseError {}

struct P {
    chars: Vec<char>,
    pos: usize,
}

impl P {
    fn peek(&self) -> Option<char> {
        self.chars.get(self.pos).copied()
    }
    fn next(&mut self) -> Option<char> {
        let c = self.peek();
        if c.is_some() {
            self.pos += 1;
        }
        c
    }
    fn skip_ws_and_comments(&mut self) {
        loop {
            match self.peek() {
                Some(c) if c == ' ' || c == '\t' || c == '\n' || c == '\r' => {
                    self.pos += 1;
                }
                Some('#') => {
                    while let Some(c) = self.peek() {
                        if c == '\n' {
                            break;
                        }
                        self.pos += 1;
                    }
                }
                _ => break,
            }
        }
    }
    fn skip_inline_ws(&mut self) {
        while matches!(self.peek(), Some(' ') | Some('\t')) {
            self.pos += 1;
        }
    }
    fn expect(&mut self, c: char) -> Result<(), ParseError> {
        if self.next() == Some(c) {
            Ok(())
        } else {
            Err(ParseError(format!("expected {:?} at offset {}", c, self.pos)))
        }
    }

    fn parse_key(&mut self) -> Result<String, ParseError> {
        self.skip_inline_ws();
        match self.peek() {
            Some('"') => self.parse_basic_string(),
            Some('\'') => self.parse_literal_string(),
            _ => {
                let mut s = String::new();
                while let Some(c) = self.peek() {
                    if c.is_alphanumeric() || c == '_' || c == '-' {
                        s.push(c);
                        self.pos += 1;
                    } else {
                        break;
                    }
                }
                if s.is_empty() {
                    Err(ParseError(format!("empty key at offset {}", self.pos)))
                } else {
                    Ok(s)
                }
            }
        }
    }

    fn parse_basic_string(&mut self) -> Result<String, ParseError> {
        self.expect('"')?;
        // triple-quoted?
        if self.peek() == Some('"') && self.chars.get(self.pos + 1) == Some(&'"') {
            self.pos += 2;
            let mut s = String::new();
            loop {
                match self.next() {
                    None => return Err(ParseError("unterminated string".into())),
                    Some('"')
                        if self.peek() == Some('"')
                            && self.chars.get(self.pos + 1) == Some(&'"') =>
                    {
                        self.pos += 2;
                        return Ok(s);
                    }
                    Some(c) => s.push(c),
                }
            }
        }
        let mut s = String::new();
        loop {
            match self.next() {
                None => return Err(ParseError("unterminated string".into())),
                Some('"') => return Ok(s),
                Some('\\') => match self.next() {
                    Some('n') => s.push('\n'),
                    Some('t') => s.push('\t'),
                    Some('r') => s.push('\r'),
                    Some('\\') => s.push('\\'),
                    Some('"') => s.push('"'),
                    Some(other) => {
                        s.push('\\');
                        s.push(other);
                    }
                    None => return Err(ParseError("unterminated escape".into())),
                },
                Some(c) => s.push(c),
            }
        }
    }

    fn parse_literal_string(&mut self) -> Result<String, ParseError> {
        self.expect('\'')?;
        let mut s = String::new();
        loop {
            match self.next() {
                None => return Err(ParseError("unterminated literal string".into())),
                Some('\'') => return Ok(s),
                Some(c) => s.push(c),
            }
        }
    }

    fn parse_value(&mut self) -> Result<Value, ParseError> {
        self.skip_ws_and_comments();
        match self.peek() {
            Some('"') => Ok(Value::Str(self.parse_basic_string()?)),
            Some('\'') => Ok(Value::Str(self.parse_literal_string()?)),
            Some('[') => {
                self.pos += 1;
                let mut items = Vec::new();
                loop {
                    self.skip_ws_and_comments();
                    if self.peek() == Some(']') {
                        self.pos += 1;
                        return Ok(Value::Array(items));
                    }
                    items.push(self.parse_value()?);
                    self.skip_ws_and_comments();
                    if self.peek() == Some(',') {
                        self.pos += 1;
                    }
                }
            }
            Some('{') => {
                self.pos += 1;
                let mut entries = Vec::new();
                loop {
                    self.skip_ws_and_comments();
                    if self.peek() == Some('}') {
                        self.pos += 1;
                        return Ok(Value::Table(entries));
                    }
                    let mut key_path = vec![self.parse_key()?];
                    loop {
                        self.skip_inline_ws();
                        if self.peek() == Some('.') {
                            self.pos += 1;
                            key_path.push(self.parse_key()?);
                        } else {
                            break;
                        }
                    }
                    self.skip_inline_ws();
                    self.expect('=')?;
                    let v = self.parse_value()?;
                    insert_dotted(&mut entries, &key_path, v);
                    self.skip_ws_and_comments();
                    if self.peek() == Some(',') {
                        self.pos += 1;
                    }
                }
            }
            Some(c) if c == 't' || c == 'f' => {
                let mut w = String::new();
                while let Some(c) = self.peek() {
                    if c.is_alphabetic() {
                        w.push(c);
                        self.pos += 1;
                    } else {
                        break;
                    }
                }
                match w.as_str() {
                    "true" => Ok(Value::Bool(true)),
                    "false" => Ok(Value::Bool(false)),
                    _ => Err(ParseError(format!("bad literal {:?}", w))),
                }
            }
            Some(c) if c.is_ascii_digit() || c == '-' || c == '+' => {
                let mut w = String::new();
                while let Some(c) = self.peek() {
                    if c.is_ascii_digit() || c == '_' || c == '-' || c == '+' {
                        w.push(c);
                        self.pos += 1;
                    } else {
                        break;
                    }
                }
                let cleaned: String = w.chars().filter(|&c| c != '_').collect();
                cleaned
                    .parse::<i64>()
                    .map(Value::Int)
                    .map_err(|_| ParseError(format!("bad integer {:?}", w)))
            }
            other => Err(ParseError(format!(
                "unexpected value start {:?} at offset {}",
                other, self.pos
            ))),
        }
    }
}

fn insert_dotted(entries: &mut Vec<(String, Value)>, path: &[String], v: Value) {
    if path.len() == 1 {
        entries.push((path[0].clone(), v));
        return;
    }
    // Find or create the sub-table for path[0].
    let idx = entries.iter().position(|(k, _)| k == &path[0]);
    let idx = match idx {
        Some(i) => i,
        None => {
            entries.push((path[0].clone(), Value::Table(Vec::new())));
            entries.len() - 1
        }
    };
    if let Value::Table(sub) = &mut entries[idx].1 {
        insert_dotted(sub, &path[1..], v);
    }
}

pub fn parse(src: &str) -> Result<Document, ParseError> {
    let mut p = P {
        chars: src.chars().collect(),
        pos: 0,
    };
    let mut doc = Document::default();
    let mut current = Table {
        path: Vec::new(),
        entries: Vec::new(),
    };
    let mut have_current = false;
    loop {
        p.skip_ws_and_comments();
        match p.peek() {
            None => break,
            Some('[') => {
                if have_current {
                    doc.tables.push(current);
                }
                p.pos += 1;
                let array_of_tables = if p.peek() == Some('[') {
                    p.pos += 1;
                    true
                } else {
                    false
                };
                let mut path = Vec::new();
                loop {
                    path.push(p.parse_key()?);
                    p.skip_inline_ws();
                    if p.peek() == Some('.') {
                        p.pos += 1;
                    } else {
                        break;
                    }
                }
                p.skip_inline_ws();
                p.expect(']')?;
                if array_of_tables {
                    p.expect(']')?;
                }
                current = Table {
                    path,
                    entries: Vec::new(),
                };
                have_current = true;
            }
            Some(_) => {
                let mut key_path = vec![p.parse_key()?];
                loop {
                    p.skip_inline_ws();
                    if p.peek() == Some('.') {
                        p.pos += 1;
                        key_path.push(p.parse_key()?);
                    } else {
                        break;
                    }
                }
                p.skip_inline_ws();
                p.expect('=')?;
                let v = p.parse_value()?;
                insert_dotted(&mut current.entries, &key_path, v);
                have_current = true;
            }
        }
    }
    if have_current {
        doc.tables.push(current);
    }
    Ok(doc)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn manifest_subset() {
        let src = r#"
[package]
name = "demo"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = { version = "1", features = ["full",
    "macros"], optional = true }
local = { path = "../local" }

[target.'cfg(unix)'.dependencies]
libc = "0.2"

[[package]]
name = "locked"
version = "1.2.3"
dependencies = [
    "serde 1.0.228",
]
"#;
        let doc = parse(src).unwrap();
        let deps = doc.table_at(&["dependencies"]).unwrap();
        assert_eq!(deps.get("serde").unwrap().as_str(), Some("1.0"));
        let tokio = deps.get("tokio").unwrap();
        assert_eq!(tokio.get("version").unwrap().as_str(), Some("1"));
        assert_eq!(tokio.get("optional").unwrap(), &Value::Bool(true));
        let target = doc
            .tables_at(&["target", "cfg(unix)", "dependencies"])
            .into_iter()
            .next()
            .unwrap();
        assert_eq!(target.get("libc").unwrap().as_str(), Some("0.2"));
        let pkgs = doc.tables_at(&["package"]);
        assert_eq!(pkgs.len(), 2);
    }
}
