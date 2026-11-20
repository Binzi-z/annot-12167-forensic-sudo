#!/usr/bin/env python3
"""make_corpus.py -- deterministic corpus + labels generator for topic 12167.

Builds a small Rust workspace whose four sink families are reachable from
request parameters, uploaded file names and configuration values:

* file read with string concatenation (`fs::read_to_string`, `fs::read`);
* archive extraction (`ZipArchive::by_name` / `File::create` / `fs::write`);
* static directory service (`NamedFile::open`);
* template include (`TemplateEngine::add_template_file`, `fs::read_to_string`).

Taint also crosses crate boundaries (via `common::fsx::read_text`) and trait
objects (`dyn AssetSource`).  `common::path_util` contains the canonicalize +
prefix check sanitizer.

Every label is attached to the exact sink line; line numbers are produced while
the file is assembled, so they cannot drift.

Usage::

    python tools/make_corpus.py
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILLER_MODULES = 460
FILLER_TABLES = 8
FILLER_FUNCS = 34


class Doc:
    def __init__(self, relpath, header=()):
        self.relpath = relpath
        self.lines = list(header)

    def add(self, *lines):
        self.lines.extend(lines)

    def case(self, lines, anchor):
        start = len(self.lines)
        self.lines.extend(lines)
        for idx in range(start, len(self.lines)):
            if self.lines[idx] == anchor:
                return idx + 1
        raise SystemExit("anchor not found in %s: %r" % (self.relpath, anchor))

    def write(self):
        path = os.path.join(ROOT, self.relpath.replace("/", os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(self.lines) + "\n")


LABELS = []


def label(file, line, variant, source, text, entry, path, evidence):
    LABELS.append({
        "id": "V%02d" % (len(LABELS) + 1),
        "sink": "path_traversal",
        "rule": "path_traversal",
        "label": text,
        "file": file,
        "line": line,
        "variant": variant,
        "source": source,
        "entry": entry,
        "path": path,
        "evidence": evidence,
    })


def cargo(name, deps=()):
    lines = ["[package]", 'name = "%s"' % name, 'version = "0.1.0"',
             'edition = "2021"', ""]
    if deps:
        lines.append("[dependencies]")
        for dep, path in deps:
            lines.append('%s = { path = "%s" }' % (dep, path))
        lines.append("")
    return lines


# ---------------------------------------------------------------------------
# common crate: sanitizer + shared IO helpers (the "safe" helpers still hit a
# sink line when they are called with a tainted path -- that is the point)
# ---------------------------------------------------------------------------
common_files = {
    "crates/common/Cargo.toml": cargo("fw-common"),
    "crates/common/src/lib.rs": [
        "pub mod fsx;",
        "pub mod path_util;",
        "",
    ],
    "crates/common/src/path_util.rs": [
        "//! Path helpers shared by every service crate.",
        "",
        "use std::path::{Path, PathBuf};",
        "",
        "/// Join a relative request path under a configured root.",
        "pub fn join_under(root: &Path, rel: &str) -> PathBuf {",
        "    root.join(rel.trim_start_matches('/'))",
        "}",
        "",
        "/// Sanitizer: the candidate must canonicalize to a path inside `root`.",
        "pub fn canonicalize_prefix_ok(root: &Path, candidate: &Path) -> bool {",
        "    let Ok(root) = root.canonicalize() else {",
        "        return false;",
        "    };",
        "    let Ok(full) = candidate.canonicalize() else {",
        "        return false;",
        "    };",
        "    full.starts_with(&root)",
        "}",
        "",
        "/// Keep only a single, boring path component; reject anything else.",
        "pub fn sanitize_component(raw: &str) -> Option<String> {",
        "    let mut out = String::new();",
        "    for ch in raw.chars() {",
        "        if ch.is_ascii_alphanumeric() || ch == '.' || ch == '_' || ch == '-' {",
        "            out.push(ch);",
        "        }",
        "    }",
        "    if out.is_empty() || out.contains(\"..\") {",
        "        None",
        "    } else {",
        "        Some(out)",
        "    }",
        "}",
        "",
    ],
    "crates/common/src/fsx.rs": [
        "//! Thin wrappers used by the ingest side. They take a path that has",
        "//! already been assembled by the caller and do not validate it.",
        "",
        "use std::fs;",
        "use std::io;",
        "use std::path::Path;",
        "",
        "pub fn read_text(path: &Path) -> io::Result<String> {",
        "    fs::read_to_string(path)",
        "}",
        "",
        "pub fn read_bytes(path: &Path) -> io::Result<Vec<u8>> {",
        "    fs::read(path)",
        "}",
        "",
        "pub fn write_text(path: &Path, body: &str) -> io::Result<()> {",
        "    fs::write(path, body)",
        "}",
        "",
        "pub fn write_bytes(path: &Path, body: &[u8]) -> io::Result<()> {",
        "    fs::write(path, body)",
        "}",
        "",
    ],
}

rpc_files = {
    "crates/rpc/Cargo.toml": cargo("fw-rpc"),
    "crates/rpc/src/lib.rs": [
        "//! Minimal request envelope used by the prototype. The real gateway",
        "//! fills these fields from query strings, form bodies and multipart",
        "//! uploads; nothing in here validates them.",
        "",
        "use std::collections::HashMap;",
        "use std::io;",
        "",
        "#[derive(Default)]",
        "pub struct Request {",
        "    query: HashMap<String, String>,",
        "    body: HashMap<String, String>,",
        "    upload: Option<String>,",
        "}",
        "",
        "impl Request {",
        "    pub fn query(&self, key: &str) -> io::Result<String> {",
        "        self.query",
        "            .get(key)",
        "            .cloned()",
        "            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, \"missing query\"))",
        "    }",
        "",
        "    pub fn body_field(&self, key: &str) -> io::Result<String> {",
        "        self.body",
        "            .get(key)",
        "            .cloned()",
        "            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, \"missing body\"))",
        "    }",
        "",
        "    pub fn upload_name(&self) -> io::Result<String> {",
        "        self.upload",
        "            .clone()",
        "            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, \"missing file\"))",
        "    }",
        "}",
        "",
    ],
}

config_files = {
    "crates/config/Cargo.toml": cargo("fw-config"),
}

config_doc = Doc("crates/config/src/lib.rs", [
    "//! Configuration snapshot loaded from the deployment bundle.",
    "",
    "use std::collections::HashMap;",
    "use std::fs;",
    "use std::io;",
    "use std::path::Path;",
    "",
    "#[derive(Default)]",
    "pub struct Config {",
    "    values: HashMap<String, String>,",
    "}",
    "",
    "impl Config {",
    "    pub fn get(&self, key: &str) -> io::Result<String> {",
    "        self.values",
    "            .get(key)",
    "            .cloned()",
    "            .ok_or_else(|| io::Error::new(io::ErrorKind::NotFound, \"missing key\"))",
    "    }",
    "}",
    "",
])

CONFIG_JOIN_CASES = [
    ("load_defaults", "storage.defaults", "/var/lib/fw/defaults"),
    ("load_signing_key", "storage.signing_key", "/etc/fw/keys"),
    ("load_trust_store", "storage.trust_store", "/etc/fw/ca"),
    ("load_bundle_index", "storage.bundle_index", "/var/lib/fw/bundles"),
]
for fn, key, root in CONFIG_JOIN_CASES:
    line = config_doc.case([
        "pub fn %s(cfg: &Config) -> io::Result<String> {" % fn,
        '    let rel = cfg.get("%s")?;' % key,
        '    let path = Path::new("%s").join(rel);' % root,
        "    fs::read_to_string(&path)",
        "}",
        "",
    ], "    fs::read_to_string(&path)")
    label("crates/config/src/lib.rs", line, "read_join", "config_file",
          "配置里的相对路径 join 到固定根目录后 fs::read_to_string",
          'cfg.get("%s")' % key,
          "config::%s -> cfg.get(%s) -> Path::join -> fs::read_to_string" % (fn, key),
          "配置值可以是 `../../etc/shadow` 之类的相对路径，join 后直接读。")

# ---------------------------------------------------------------------------
# ingest crate: file read + cross-crate helper + trait dispatch targets
# ---------------------------------------------------------------------------
ingest = Doc("crates/ingest/src/lib.rs", [
    "//! Ingest workers: every handler receives the request envelope from",
    "//! `fw-rpc` and resolves a path below the configured storage root.",
    "",
    "use std::fs;",
    "use std::io;",
    "use std::path::Path;",
    "",
    "use fw_common as common;",
    "use fw_config::Config;",
    "use fw_rpc::Request;",
    "",
])

CONCAT_CASES = [
    ("load_profile", "profile", "query"),
    ("load_firmware", "firmware", "query"),
    ("load_release_notes", "notes", "body"),
    ("load_cert_bundle", "cert", "query"),
    ("load_device_map", "devices", "body"),
    ("load_policy", "policy", "query"),
    ("load_route_table", "routes", "config"),
    ("load_ui_asset", "asset", "query"),
    ("load_audit_page", "page", "query"),
    ("load_manifest", "manifest", "config"),
]

for fn, key, kind in CONCAT_CASES:
    if kind == "query":
        src = 'req.query("%s")?' % key
        src_line = '    let name = req.query("%s")?;' % key
        source = "http_query"
        sig = "pub fn %s(root: &Path, req: &Request) -> io::Result<String> {" % fn
    elif kind == "body":
        src = 'req.body_field("%s")?' % key
        src_line = '    let name = req.body_field("%s")?;' % key
        source = "http_body"
        sig = "pub fn %s(root: &Path, req: &Request) -> io::Result<String> {" % fn
    else:
        src = 'cfg.get("storage.%s")?' % key
        src_line = '    let name = cfg.get("storage.%s")?;' % key
        source = "config_file"
        sig = "pub fn %s(root: &Path, cfg: &Config) -> io::Result<String> {" % fn
    line = ingest.case([
        sig,
        src_line,
        '    let path = format!("{}/{}", root.display(), name);',
        "    fs::read_to_string(&path)",
        "}",
        "",
    ], "    fs::read_to_string(&path)")
    label("crates/ingest/src/lib.rs", line, "read_concat", source,
          "拼接出的路径直接 fs::read_to_string（%s 来源）" % {"http_query": "请求参数", "http_body": "请求体", "config_file": "配置"}[source],
          src,
          "rpc/config -> ingest::%s -> fs::read_to_string" % fn,
          "`format!(\"{}/{}\", root, name)` 直接拼路径，name 未做 canonicalize 或前缀校验。")

JOIN_CASES = [
    ("digest_file", "digest", "upload"),
    ("hash_blob", "blob", "upload"),
    ("tail_log", "log", "query"),
    ("scan_quarantine", "sample", "body"),
]
for fn, key, kind in JOIN_CASES:
    if kind == "upload":
        src = "req.upload_name()?"
        src_line = "    let rel = req.upload_name()?;"
        source = "upload_filename"
    elif kind == "query":
        src = 'req.query("%s")?' % key
        src_line = '    let rel = req.query("%s")?;' % key
        source = "http_query"
    else:
        src = 'req.body_field("%s")?' % key
        src_line = '    let rel = req.body_field("%s")?;' % key
        source = "http_body"
    line = ingest.case([
        "pub fn %s(root: &Path, req: &Request) -> io::Result<Vec<u8>> {" % fn,
        src_line,
        "    let path = root.join(rel);",
        "    fs::read(&path)",
        "}",
        "",
    ], "    fs::read(&path)")
    label("crates/ingest/src/lib.rs", line, "read_join", source,
          "root.join(上传文件名/参数) 后 fs::read",
          src,
          "rpc -> ingest::%s -> root.join -> fs::read" % fn,
          "PathBuf::join 遇到 `..` 或绝对路径会逃出 root；这里没有任何校验。")

CROSS_CASES = [
    ("fetch_config", "config", "query"),
    ("fetch_snapshot", "snapshot", "query"),
    ("fetch_overlay", "overlay", "body"),
    ("fetch_secret", "secret", "config"),
]
for fn, key, kind in CROSS_CASES:
    if kind == "query":
        src = 'req.query("%s")?' % key
        src_line = '    let rel = req.query("%s")?;' % key
        source = "http_query"
        sig = "pub fn %s(root: &Path, req: &Request) -> io::Result<String> {" % fn
    elif kind == "body":
        src = 'req.body_field("%s")?' % key
        src_line = '    let rel = req.body_field("%s")?;' % key
        source = "http_body"
        sig = "pub fn %s(root: &Path, req: &Request) -> io::Result<String> {" % fn
    else:
        src = 'cfg.get("storage.%s")?' % key
        src_line = '    let rel = cfg.get("storage.%s")?;' % key
        source = "config_file"
        sig = "pub fn %s(root: &Path, cfg: &Config) -> io::Result<String> {" % fn
    line = ingest.case([
        sig,
        src_line,
        "    let path = common::path_util::join_under(root, &rel);",
        "    common::fsx::read_text(&path)",
        "}",
        "",
    ], "    common::fsx::read_text(&path)")
    label("crates/ingest/src/lib.rs", line, "cross_crate", source,
          "跨 crate：common::fsx::read_text 读到拼接路径",
          src,
          "rpc/config -> ingest::%s -> common::path_util::join_under -> common::fsx::read_text -> fs::read_to_string" % fn,
          "污点经 common crate 的 join_under/read_text 跨 crate 传播；common 不知道调用者是谁。")

# benign tail of ingest: constants and one canonicalize+prefix guarded read
ingest.add(
    "",
    "// ---- benign helpers: fixed image paths and a guarded read ----",
    "",
    "pub fn read_build_stamp() -> io::Result<String> {",
    "    fs::read_to_string(\"/etc/fw/build-id\")",
    "}",
    "",
    "pub fn read_release_channel() -> io::Result<String> {",
    "    common::fsx::read_text(Path::new(\"/etc/fw/channel\"))",
    "}",
    "",
    "pub fn read_trusted_manifest() -> io::Result<String> {",
    "    fs::read_to_string(\"/usr/share/fw/manifest.json\")",
    "}",
    "",
    "/// Benign: the canonicalize + prefix check runs before the read.",
    "pub fn load_user_avatar(root: &Path, req: &Request) -> io::Result<Vec<u8>> {",
    "    let rel = req.upload_name()?;",
    "    let path = common::path_util::join_under(root, &rel);",
    "    if !common::path_util::canonicalize_prefix_ok(root, &path) {",
    "        return Err(io::Error::new(io::ErrorKind::PermissionDenied, \"outside root\"));",
    "    }",
    "    fs::read(&path)",
    "}",
    "",
    "/// Benign: the file name is reduced to one safe component first.",
    "pub fn load_icon(root: &Path, req: &Request) -> io::Result<Vec<u8>> {",
    "    let raw = req.upload_name()?;",
    "    let name = common::path_util::sanitize_component(&raw)",
    "        .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, \"bad name\"))?;",
    "    fs::read(root.join(name))",
    "}",
    "",
)

# ---------------------------------------------------------------------------
# unpack crate: archive extraction
# ---------------------------------------------------------------------------
unpack = Doc("crates/unpack/src/lib.rs", [
    "//! Update-bundle extraction. The zip reader is a small in-tree stub so the",
    "//! corpus does not depend on an external crate; entry semantics match the",
    "//! real one (by_name / entries / name).",
    "",
    "use std::fs::{self, File};",
    "use std::io::{self, Write};",
    "use std::path::Path;",
    "",
    "use fw_rpc::Request;",
    "",
    "pub struct ZipFile {",
    "    name: String,",
    "    data: Vec<u8>,",
    "}",
    "",
    "impl ZipFile {",
    "    pub fn name(&self) -> &str {",
    "        &self.name",
    "    }",
    "",
    "    pub fn data(&self) -> &[u8] {",
    "        &self.data",
    "    }",
    "",
    "    pub fn enclosed_name(&self) -> Option<String> {",
    "        let mut parts = Vec::new();",
    "        for part in self.name.split('/') {",
    "            if part == \"..\" {",
    "                return None;",
    "            }",
    "            if !part.is_empty() && part != \".\" {",
    "                parts.push(part);",
    "            }",
    "        }",
    "        Some(parts.join(\"/\"))",
    "    }",
    "}",
    "",
    "pub struct ZipArchive<R> {",
    "    entries: Vec<ZipFile>,",
    "    _reader: R,",
    "}",
    "",
    "impl<R> ZipArchive<R> {",
    "    pub fn by_name(&mut self, name: &str) -> io::Result<ZipFile> {",
    "        for entry in &self.entries {",
    "            if entry.name == name {",
    "                return Ok(ZipFile { name: entry.name.clone(), data: entry.data.clone() });",
    "            }",
    "        }",
    "        Err(io::Error::new(io::ErrorKind::NotFound, \"entry\"))",
    "    }",
    "",
    "    pub fn entries(&mut self) -> Vec<ZipFile> {",
    "        self.entries",
    "            .iter()",
    "            .map(|e| ZipFile { name: e.name.clone(), data: e.data.clone() })",
    "            .collect()",
    "    }",
    "}",
    "",
])

EXTRACT_CASES = [
    ("extract_update", "package", "query"),
    ("extract_theme", "theme", "query"),
    ("extract_plugin", "plugin", "upload"),
    ("extract_locale", "locale", "body"),
    ("extract_ca_bundle", "ca", "query"),
    ("extract_doc", "doc", "config"),
    ("extract_font", "font", "upload"),
]
for fn, key, kind in EXTRACT_CASES:
    if kind == "query":
        src = 'req.query("%s")?' % key
        src_line = '    let name = req.query("%s")?;' % key
        source = "http_query"
        sig = "pub fn %s(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {" % fn
    elif kind == "body":
        src = 'req.body_field("%s")?' % key
        src_line = '    let name = req.body_field("%s")?;' % key
        source = "http_body"
        sig = "pub fn %s(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {" % fn
    elif kind == "upload":
        src = "req.upload_name()?"
        src_line = "    let name = req.upload_name()?;"
        source = "upload_filename"
        sig = "pub fn %s(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {" % fn
    else:
        src = 'cfg.get("bundle.%s")?' % key
        src_line = '    let name = cfg.get("bundle.%s")?;' % key
        source = "config_file"
        sig = ("pub fn %s(archive: &mut ZipArchive<File>, dest: &Path,"
               " cfg: &fw_config::Config) -> io::Result<()> {" % fn)
    line = unpack.case([
        sig,
        src_line,
        "    let mut entry = archive.by_name(&name)?;",
        "    let out = dest.join(entry.name());",
        "    let mut file = File::create(&out)?;",
        "    file.write_all(entry.data())?;",
        "    Ok(())",
        "}",
        "",
    ], "    let mut entry = archive.by_name(&name)?;")
    label("crates/unpack/src/lib.rs", line, "unzip_entry", source,
          "压缩包条目名从请求/上传/配置来，by_name 后落盘",
          src,
          "rpc/config -> unpack::%s -> ZipArchive::by_name -> File::create -> 写盘" % fn,
          "条目名没有走 enclosed_name() 校验，`../` 可以写到 dest 之外。")

UNPACK_CASES = [
    ("unpack_all", "dir", "query", '    let prefix = req.query("dir")?;'),
    ("unpack_assets", "bundle", "upload", "    let prefix = req.upload_name()?;"),
    ("unpack_modules", "target", "query", '    let prefix = req.query("target")?;'),
    ("unpack_samples", "stage", "body", '    let prefix = req.body_field("stage")?;'),
    ("unpack_static", "extract.dir", "config", '    let prefix = cfg.get("extract.dir")?;'),
]
for fn, _key, kind, prefix_line in UNPACK_CASES:
    if kind == "config":
        sig = ("pub fn %s(archive: &mut ZipArchive<File>, dest: &Path,"
               " cfg: &fw_config::Config) -> io::Result<()> {" % fn)
    else:
        sig = ("pub fn %s(archive: &mut ZipArchive<File>, dest: &Path,"
               " req: &Request) -> io::Result<()> {" % fn)
    line = unpack.case([
        sig,
        prefix_line,
        "    for entry in archive.entries() {",
        "        let out = dest.join(prefix.as_str()).join(entry.name());",
        "        fs::write(&out, entry.data())?;",
        "    }",
        "    Ok(())",
        "}",
        "",
    ], "        fs::write(&out, entry.data())?;")
    label("crates/unpack/src/lib.rs", line, "unzip_write",
          {"query": "http_query", "upload": "upload_filename",
           "body": "http_body", "config": "config_file"}[kind],
          "整包解压：请求/配置给出的子目录 + 归档条目名直接 fs::write 落盘",
          prefix_line.strip().rstrip(";"),
          "unpack::%s -> 请求/配置前缀 + entry.name() -> fs::write" % fn,
          "解压目录由请求/配置决定，条目名又是压缩包自带的；两者都没有做 `..` 校验。")

unpack.add(
    "",
    "// ---- benign: fixed output path and an enclosed_name-guarded loop ----",
    "",
    "pub fn write_unpack_log(body: &str) -> io::Result<()> {",
    "    fs::write(\"/var/log/fw-unpack.log\", body)",
    "}",
    "",
    "pub fn create_marker() -> io::Result<File> {",
    "    File::create(\"/var/lib/fw/unpacked\")",
    "}",
    "",
    "pub fn extract_checked(archive: &mut ZipArchive<File>, dest: &Path) -> io::Result<()> {",
    "    for entry in archive.entries() {",
    "        let Some(safe) = entry.enclosed_name() else {",
    "            continue;",
    "        };",
    "        let out = dest.join(safe);",
    "        fs::write(&out, entry.data())?;",
    "    }",
    "    Ok(())",
    "}",
    "",
)

# ---------------------------------------------------------------------------
# serve crate: static directory service
# ---------------------------------------------------------------------------
serve = Doc("crates/serve/src/lib.rs", [
    "//! Static asset service. `NamedFile` is an in-tree stub of the framework",
    "//! type: it only records the path it was asked to open.",
    "",
    "use std::fs;",
    "use std::io;",
    "use std::path::{Path, PathBuf};",
    "",
    "use fw_rpc::Request;",
    "",
    "pub struct NamedFile {",
    "    path: PathBuf,",
    "}",
    "",
    "impl NamedFile {",
    "    pub fn open<P: AsRef<Path>>(path: P) -> io::Result<NamedFile> {",
    "        let path = path.as_ref();",
    "        if !path.exists() {",
    "            return Err(io::Error::new(io::ErrorKind::NotFound, \"asset\"));",
    "        }",
    "        Ok(NamedFile { path: path.to_path_buf() })",
    "    }",
    "",
    "    pub fn path(&self) -> &Path {",
    "        &self.path",
    "    }",
    "}",
    "",
])

SERVE_CASES = [
    ("serve_asset", "file", "query"),
    ("serve_download", "download", "query"),
    ("serve_media", "media", "body"),
    ("serve_font", "font", "query"),
    ("serve_doc", "doc", "upload"),
    ("serve_report", "report", "query"),
    ("serve_upload", "upload", "upload"),
]
for fn, key, kind in SERVE_CASES:
    if kind == "query":
        src = 'req.query("%s")?' % key
        src_line = '    let rel = req.query("%s")?;' % key
        source = "http_query"
    elif kind == "body":
        src = 'req.body_field("%s")?' % key
        src_line = '    let rel = req.body_field("%s")?;' % key
        source = "http_body"
    else:
        src = "req.upload_name()?"
        src_line = "    let rel = req.upload_name()?;"
        source = "upload_filename"
    line = serve.case([
        "pub fn %s(public: &Path, req: &Request) -> io::Result<NamedFile> {" % fn,
        src_line,
        "    let path = public.join(rel);",
        "    NamedFile::open(&path)",
        "}",
        "",
    ], "    NamedFile::open(&path)")
    label("crates/serve/src/lib.rs", line, "static_dir", source,
          "静态目录服务：请求路径 join 后 NamedFile::open",
          src,
          "rpc -> serve::%s -> public.join -> NamedFile::open" % fn,
          "静态目录服务直接把请求路径 join 到 public 下，`..` 可以读到目录外文件。")

serve.add(
    "",
    "// ---- benign: fixed entry points and a guarded download ----",
    "",
    "pub fn serve_index(public: &Path) -> io::Result<NamedFile> {",
    "    NamedFile::open(public.join(\"index.html\"))",
    "}",
    "",
    "pub fn serve_favicon(public: &Path) -> io::Result<NamedFile> {",
    "    NamedFile::open(public.join(\"favicon.ico\"))",
    "}",
    "",
    "pub fn serve_readme() -> io::Result<NamedFile> {",
    "    NamedFile::open(\"/usr/share/doc/fw/README\")",
    "}",
    "",
    "pub fn serve_guarded(public: &Path, req: &Request) -> io::Result<NamedFile> {",
    "    let rel = req.query(\"file\")?;",
    "    let path = public.join(rel);",
    "    if !fw_common::path_util::canonicalize_prefix_ok(public, &path) {",
    "        return Err(io::Error::new(io::ErrorKind::PermissionDenied, \"outside\"));",
    "    }",
    "    NamedFile::open(&path)",
    "}",
    "",
)

# ---------------------------------------------------------------------------
# render crate: template include
# ---------------------------------------------------------------------------
render = Doc("crates/render/src/lib.rs", [
    "//! Template include. `TemplateEngine` is an in-tree stub: it keeps the",
    "//! rendered bodies in memory, but `add_template_file` reads from disk.",
    "",
    "use std::collections::HashMap;",
    "use std::fs;",
    "use std::io;",
    "",
    "use fw_rpc::Request;",
    "",
    "#[derive(Default)]",
    "pub struct TemplateEngine {",
    "    templates: HashMap<String, String>,",
    "}",
    "",
    "impl TemplateEngine {",
    "    pub fn add_template_file(&mut self, path: &str) -> io::Result<()> {",
    "        let body = fs::read_to_string(path)?;",
    "        self.templates.insert(path.to_string(), body);",
    "        Ok(())",
    "    }",
    "",
    "    pub fn render(&self, name: &str, _ctx: &[(&str, String)]) -> io::Result<String> {",
    "        Ok(self.templates.get(name).cloned().unwrap_or_default())",
    "    }",
    "}",
    "",
])

TMPL_CASES = [
    ("render_report", "template", "query", "add"),
    ("render_invoice", "invoice", "query", "add"),
    ("render_receipt", "receipt", "body", "add"),
    ("render_digest", "digest", "upload", "read"),
    ("render_summary", "summary", "query", "read"),
    ("render_alert", "alert", "config", "read"),
]
for fn, key, kind, mode in TMPL_CASES:
    if kind == "query":
        src = 'req.query("%s")?' % key
        src_line = '    let name = req.query("%s")?;' % key
        source = "http_query"
    elif kind == "body":
        src = 'req.body_field("%s")?' % key
        src_line = '    let name = req.body_field("%s")?;' % key
        source = "http_body"
    elif kind == "upload":
        src = "req.upload_name()?"
        src_line = "    let name = req.upload_name()?;"
        source = "upload_filename"
    else:
        src = 'cfg.get("templates.%s")?' % key
        src_line = '    let name = cfg.get("templates.%s")?;' % key
        source = "config_file"
    if mode == "add":
        sig = "pub fn %s(engine: &mut TemplateEngine, req: &Request) -> io::Result<String> {" % fn
        lines = [
            sig,
            src_line,
            '    let path = format!("templates/{}", name);',
            "    engine.add_template_file(&path)?;",
            '    engine.render("report", &[])',
            "}",
            "",
        ]
        anchor = "    engine.add_template_file(&path)?;"
        path = "rpc/config -> render::%s -> engine.add_template_file -> fs::read_to_string" % fn
    else:
        sig = "pub fn %s(req: &Request) -> io::Result<String> {" % fn if kind != "config" \
            else "pub fn %s(cfg: &fw_config::Config) -> io::Result<String> {" % fn
        lines = [
            sig,
            src_line,
            '    let path = format!("templates/{}", name);',
            "    fs::read_to_string(&path)",
            "}",
            "",
        ]
        anchor = "    fs::read_to_string(&path)"
        path = "rpc/config -> render::%s -> fs::read_to_string(模板路径)" % fn
    line = render.case(lines, anchor)
    label("crates/render/src/lib.rs", line, "template_include", source,
          "模板名来自请求/上传/配置，include 后整文件读出",
          src, path,
          "模板 include 的路径可被 `../` 改写，读到模板目录之外的文件（源码/密钥）。")

render.add(
    "",
    "// ---- benign: fixed templates and an allowlisted name ----",
    "",
    "pub fn render_base(engine: &mut TemplateEngine) -> io::Result<String> {",
    "    engine.add_template_file(\"templates/base.hbs\")?;",
    "    engine.render(\"base\", &[])",
    "}",
    "",
    "pub fn read_mail_template() -> io::Result<String> {",
    "    fs::read_to_string(\"templates/mail.hbs\")",
    "}",
    "",
    "pub fn read_report_template() -> io::Result<String> {",
    "    fs::read_to_string(\"templates/report.hbs\")",
    "}",
    "",
    "pub fn render_allowlisted(engine: &mut TemplateEngine, req: &Request) -> io::Result<String> {",
    "    let name = req.query(\"template\")?;",
    "    let path = match name.as_str() {",
    "        \"base\" => \"templates/base.hbs\",",
    "        \"mail\" => \"templates/mail.hbs\",",
    "        _ => return Err(io::Error::new(io::ErrorKind::InvalidInput, \"unknown\")),",
    "    };",
    "    engine.add_template_file(path)?;",
    "    engine.render(&name, &[])",
    "}",
    "",
)

# ---------------------------------------------------------------------------
# app crate: trait dispatch + wiring
# ---------------------------------------------------------------------------
app = Doc("crates/app/src/main.rs", [
    "//! Composition root. The asset resolver is chosen at start-up from the",
    "//! deployment profile and used through a trait object, so the concrete",
    "//! implementation is not visible to a purely syntactic call graph.",
    "",
    "use std::fs;",
    "use std::io;",
    "use std::path::{Path, PathBuf};",
    "",
    "use fw_rpc::Request;",
    "",
    "pub trait AssetSource {",
    "    fn resolve(&self, key: &str) -> String;",
    "}",
    "",
    "pub struct FsSource {",
    "    root: PathBuf,",
    "}",
    "",
    "pub struct CdnSource {",
    "    base: String,",
    "}",
    "",
    "impl AssetSource for FsSource {",
    "    fn resolve(&self, key: &str) -> String {",
    "        format!(\"{}/{}\", self.root.display(), key)",
    "    }",
    "}",
    "",
    "impl AssetSource for CdnSource {",
    "    fn resolve(&self, key: &str) -> String {",
    "        format!(\"{}/{}\", self.base, key)",
    "    }",
    "}",
    "",
])

TRAIT_CASES = [
    ("resolve_and_open_profile", "asset"),
    ("resolve_and_open_theme", "theme"),
    ("resolve_and_open_locale", "locale"),
]
for fn, key in TRAIT_CASES:
    line = app.case([
        "fn %s(source: &dyn AssetSource, req: &Request) -> io::Result<String> {" % fn,
        '    let key = req.query("%s")?;' % key,
        "    let path = source.resolve(&key);",
        "    fs::read_to_string(&path)",
        "}",
        "",
    ], "    fs::read_to_string(&path)")
    label("crates/app/src/main.rs", line, "trait_dispatch", "http_query",
          "trait 对象 AssetSource::resolve 返回的路径直接 fs::read_to_string",
          'req.query("%s")' % key,
          "rpc -> app::%s -> dyn AssetSource::resolve -> fs::read_to_string" % fn,
          "路径由 trait 对象的实现拼接，静态调用图停在 `source.resolve`；实现可能是 FsSource 或 CdnSource。")

app.add(
    "",
    "fn read_version() -> io::Result<String> {",
    "    fs::read_to_string(\"/etc/fw/version\")",
    "}",
    "",
    "fn read_boot_config() -> io::Result<String> {",
    "    fs::read_to_string(\"/boot/fw.cfg\")",
    "}",
    "",
    "fn main() -> io::Result<()> {",
    "    let root = Path::new(\"/srv/assets\");",
    "    let source = FsSource { root: root.to_path_buf() };",
    "    let req = Request::default();",
    "    let _profile = resolve_and_open_profile(&source, &req)?;",
    "    let _version = read_version()?;",
    "    Ok(())",
    "}",
    "",
)

# ---------------------------------------------------------------------------
# workspace files, templates, config, filler
# ---------------------------------------------------------------------------
cargo_files = {
    "Cargo.toml": [
        "[workspace]",
        'members = [',
        '    "crates/common",',
        '    "crates/rpc",',
        '    "crates/config",',
        '    "crates/ingest",',
        '    "crates/unpack",',
        '    "crates/serve",',
        '    "crates/render",',
        '    "crates/app",',
        "]",
        'resolver = "2"',
        "",
    ],
    "pyproject.toml": [
        "[project]",
        'name = "annot-12167-path-traversal"',
        'version = "0.1.0"',
        'requires-python = ">=3.10"',
        'dependencies = ["tree-sitter>=0.21", "tree-sitter-rust>=0.21"]',
        "",
        "[tool.pytest.ini_options]",
        'testpaths = ["tests"]',
        "",
    ],
    "crates/ingest/Cargo.toml": cargo("fw-ingest", [
        ("fw-common", "../common"), ("fw-config", "../config"), ("fw-rpc", "../rpc")]),
    "crates/unpack/Cargo.toml": cargo("fw-unpack", [
        ("fw-config", "../config"), ("fw-rpc", "../rpc")]),
    "crates/serve/Cargo.toml": cargo("fw-serve", [
        ("fw-common", "../common"), ("fw-rpc", "../rpc")]),
    "crates/render/Cargo.toml": cargo("fw-render", [
        ("fw-config", "../config"), ("fw-rpc", "../rpc")]),
    "crates/app/Cargo.toml": cargo("fw-app", [
        ("fw-common", "../common"), ("fw-rpc", "../rpc")]),
}
cargo_files.update(common_files)
cargo_files.update(rpc_files)
cargo_files.update(config_files)

for rel, lines in cargo_files.items():
    Doc(rel, lines).write()

TEMPLATES = {
    "templates/base.hbs": ["<!doctype html>", "<title>{{title}}</title>", "<main>{{body}}</main>"],
    "templates/mail.hbs": ["Subject: {{subject}}", "", "Hi {{name}},", "{{body}}"],
    "templates/report.hbs": ["# {{title}}", "", "{{rows}}"],
    "templates/selftest.hbs": ["selftest {{run}}", "{{status}}"],
}

for rel, lines in TEMPLATES.items():
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

CONFIG = {
    "note": ("可配置的 source / sanitizer / 静态目录 / 模板白名单。"
             "分析器读它决定哪些调用算净化；增删条目应该能改变召回与误报，用来做消融。"),
    "sources": {
        "http_query": ["Request::query"],
        "http_body": ["Request::body_field"],
        "upload_filename": ["Request::upload_name"],
        "config_file": ["Config::get"],
    },
    "sanitizers": [
        {"name": "canonicalize_prefix_ok", "kind": "canonicalize_prefix",
         "note": "canonicalize 后必须仍位于 root 之下"},
        {"name": "sanitize_component", "kind": "single_component"},
        {"name": "enclosed_name", "kind": "zip_enclosed_name"},
    ],
    "static_dirs": ["public"],
    "template_dirs": ["templates"],
    "safe_templates": ["base.hbs", "mail.hbs", "report.hbs"],
}
with open(os.path.join(ROOT, "config", "sanitizers.json"), "w",
          encoding="utf-8", newline="\n") as fh:
    json.dump(CONFIG, fh, ensure_ascii=False, indent=2)
    fh.write("\n")


def filler_rs(idx):
    name = "bshim_%03d" % idx
    up = name.upper()
    lines = [
        "// %s -- register table helpers, generated from the %04d pinout." % (name, idx),
        "// Pure table math; no filesystem or process interaction.",
        "",
    ]
    for t in range(FILLER_TABLES):
        lines.append("pub const %s_TAB%d: [u32; 96] = [" % (up, t))
        for row in range(12):
            vals = ", ".join(
                "0x%08xu" % (((idx * 131 + t * 17 + row * 8 + k) * 2654435761) & 0xFFFFFFFF)
                for k in range(8)
            )
            lines.append("    " + vals + ",")
        lines.append("];")
        lines.append("")
    lines += [
        "pub struct %s {" % ("Shim%03d" % idx),
        "    pub head: u32,",
        "    pub tail: u32,",
        "    pub flags: u32,",
        "}",
        "",
        "impl %s {" % ("Shim%03d" % idx),
        "    pub fn new() -> Self {",
        "        Self { head: 0, tail: 0, flags: 0x%08xu }" % ((idx * 7919) & 0xFFFFFFFF),
        "    }",
        "",
    ]
    for f in range(FILLER_FUNCS):
        lines += [
            "    pub fn mix%d(&self, seed: u32, buf: &[u8]) -> u32 {" % f,
            "        let mut acc = seed ^ 0x%08xu;" % (((idx + f) * 2246822519) & 0xFFFFFFFF),
            "        for (i, byte) in buf.iter().enumerate() {",
            "            acc = acc.rotate_left(5) ^ (*byte as u32);",
            "            acc = acc.wrapping_add(%s_TAB%d[((i as u32).wrapping_add(acc) & 95) as usize]);"
            % (up, f % FILLER_TABLES),
            "        }",
            "        acc",
            "    }",
            "",
        ]
    lines += ["}", ""]
    return lines


for i in range(FILLER_MODULES):
    Doc("filler/%s.rs" % ("bshim_%03d" % i), filler_rs(i)).write()

for doc in (config_doc, ingest, unpack, serve, render, app):
    doc.write()

LABELS.sort(key=lambda item: (item["file"], item["line"]))
for idx, item in enumerate(LABELS, 1):
    item["id"] = "V%02d" % idx
assert len(LABELS) == 50, len(LABELS)

labels_doc = {
    "topic": "12167",
    "note": ("标注 = 不可信路径（请求参数 / 上传文件名 / 配置）到达文件系统落点的那些行。"
             "常量路径、canonicalize+前缀校验、sanitize_component 单段化、"
             "enclosed_name 校验过的条目都算良性，报了就是误报。"),
    "total": len(LABELS),
    "vulns": LABELS,
}
with open(os.path.join(ROOT, "labels.json"), "w", encoding="utf-8", newline="\n") as fh:
    json.dump(labels_doc, fh, ensure_ascii=False, indent=2)
    fh.write("\n")

total_lines = 0
total_files = 0
for dirpath, _dirnames, names in os.walk(ROOT):
    if ".git" in dirpath or "tools" in dirpath or "tests" in dirpath:
        continue
    for name in names:
        if name.endswith((".rs", ".hbs")):
            total_files += 1
            with open(os.path.join(dirpath, name), encoding="utf-8") as fh:
                total_lines += sum(1 for _ in fh)

print("corpus: %d rust/template files, %d lines" % (total_files, total_lines))
print("labels: %d" % len(LABELS))
