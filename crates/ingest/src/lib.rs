//! Ingest workers: every handler receives the request envelope from
//! `fw-rpc` and resolves a path below the configured storage root.

use std::fs;
use std::io;
use std::path::Path;

use fw_common as common;
use fw_config::Config;
use fw_rpc::Request;

pub fn load_profile(root: &Path, req: &Request) -> io::Result<String> {
    let name = req.query("profile")?;
    let path = format!("{}/{}", root.display(), name);
    fs::read_to_string(&path)
}

pub fn load_firmware(root: &Path, req: &Request) -> io::Result<String> {
    let name = req.query("firmware")?;
    let path = format!("{}/{}", root.display(), name);
    fs::read_to_string(&path)
}

pub fn load_release_notes(root: &Path, req: &Request) -> io::Result<String> {
    let name = req.body_field("notes")?;
    let path = format!("{}/{}", root.display(), name);
    fs::read_to_string(&path)
}

pub fn load_cert_bundle(root: &Path, req: &Request) -> io::Result<String> {
    let name = req.query("cert")?;
    let path = format!("{}/{}", root.display(), name);
    fs::read_to_string(&path)
}

pub fn load_device_map(root: &Path, req: &Request) -> io::Result<String> {
    let name = req.body_field("devices")?;
    let path = format!("{}/{}", root.display(), name);
    fs::read_to_string(&path)
}

pub fn load_policy(root: &Path, req: &Request) -> io::Result<String> {
    let name = req.query("policy")?;
    let path = format!("{}/{}", root.display(), name);
    fs::read_to_string(&path)
}

pub fn load_route_table(root: &Path, cfg: &Config) -> io::Result<String> {
    let name = cfg.get("storage.routes")?;
    let path = format!("{}/{}", root.display(), name);
    fs::read_to_string(&path)
}

pub fn load_ui_asset(root: &Path, req: &Request) -> io::Result<String> {
    let name = req.query("asset")?;
    let path = format!("{}/{}", root.display(), name);
    fs::read_to_string(&path)
}

pub fn load_audit_page(root: &Path, req: &Request) -> io::Result<String> {
    let name = req.query("page")?;
    let path = format!("{}/{}", root.display(), name);
    fs::read_to_string(&path)
}

pub fn load_manifest(root: &Path, cfg: &Config) -> io::Result<String> {
    let name = cfg.get("storage.manifest")?;
    let path = format!("{}/{}", root.display(), name);
    fs::read_to_string(&path)
}

pub fn digest_file(root: &Path, req: &Request) -> io::Result<Vec<u8>> {
    let rel = req.upload_name()?;
    let path = root.join(rel);
    fs::read(&path)
}

pub fn hash_blob(root: &Path, req: &Request) -> io::Result<Vec<u8>> {
    let rel = req.upload_name()?;
    let path = root.join(rel);
    fs::read(&path)
}

pub fn tail_log(root: &Path, req: &Request) -> io::Result<Vec<u8>> {
    let rel = req.query("log")?;
    let path = root.join(rel);
    fs::read(&path)
}

pub fn scan_quarantine(root: &Path, req: &Request) -> io::Result<Vec<u8>> {
    let rel = req.body_field("sample")?;
    let path = root.join(rel);
    fs::read(&path)
}

pub fn fetch_config(root: &Path, req: &Request) -> io::Result<String> {
    let rel = req.query("config")?;
    let path = common::path_util::join_under(root, &rel);
    common::fsx::read_text(&path)
}

pub fn fetch_snapshot(root: &Path, req: &Request) -> io::Result<String> {
    let rel = req.query("snapshot")?;
    let path = common::path_util::join_under(root, &rel);
    common::fsx::read_text(&path)
}

pub fn fetch_overlay(root: &Path, req: &Request) -> io::Result<String> {
    let rel = req.body_field("overlay")?;
    let path = common::path_util::join_under(root, &rel);
    common::fsx::read_text(&path)
}

pub fn fetch_secret(root: &Path, cfg: &Config) -> io::Result<String> {
    let rel = cfg.get("storage.secret")?;
    let path = common::path_util::join_under(root, &rel);
    common::fsx::read_text(&path)
}


// ---- benign helpers: fixed image paths and a guarded read ----

pub fn read_build_stamp() -> io::Result<String> {
    fs::read_to_string("/etc/fw/build-id")
}

pub fn read_release_channel() -> io::Result<String> {
    common::fsx::read_text(Path::new("/etc/fw/channel"))
}

pub fn read_trusted_manifest() -> io::Result<String> {
    fs::read_to_string("/usr/share/fw/manifest.json")
}

/// Benign: the canonicalize + prefix check runs before the read.
pub fn load_user_avatar(root: &Path, req: &Request) -> io::Result<Vec<u8>> {
    let rel = req.upload_name()?;
    let path = common::path_util::join_under(root, &rel);
    if !common::path_util::canonicalize_prefix_ok(root, &path) {
        return Err(io::Error::new(io::ErrorKind::PermissionDenied, "outside root"));
    }
    fs::read(&path)
}

/// Benign: the file name is reduced to one safe component first.
pub fn load_icon(root: &Path, req: &Request) -> io::Result<Vec<u8>> {
    let raw = req.upload_name()?;
    let name = common::path_util::sanitize_component(&raw)
        .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "bad name"))?;
    fs::read(root.join(name))
}

