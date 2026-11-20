//! Path helpers shared by every service crate.

use std::path::{Path, PathBuf};

/// Join a relative request path under a configured root.
pub fn join_under(root: &Path, rel: &str) -> PathBuf {
    root.join(rel.trim_start_matches('/'))
}

/// Sanitizer: the candidate must canonicalize to a path inside `root`.
pub fn canonicalize_prefix_ok(root: &Path, candidate: &Path) -> bool {
    let Ok(root) = root.canonicalize() else {
        return false;
    };
    let Ok(full) = candidate.canonicalize() else {
        return false;
    };
    full.starts_with(&root)
}

/// Keep only a single, boring path component; reject anything else.
pub fn sanitize_component(raw: &str) -> Option<String> {
    let mut out = String::new();
    for ch in raw.chars() {
        if ch.is_ascii_alphanumeric() || ch == '.' || ch == '_' || ch == '-' {
            out.push(ch);
        }
    }
    if out.is_empty() || out.contains("..") {
        None
    } else {
        Some(out)
    }
}

