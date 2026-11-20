//! Configuration snapshot loaded from the deployment bundle.

use std::collections::HashMap;
use std::fs;
use std::io;
use std::path::Path;

#[derive(Default)]
pub struct Config {
    values: HashMap<String, String>,
}

impl Config {
    pub fn get(&self, key: &str) -> io::Result<String> {
        self.values
            .get(key)
            .cloned()
            .ok_or_else(|| io::Error::new(io::ErrorKind::NotFound, "missing key"))
    }
}

pub fn load_defaults(cfg: &Config) -> io::Result<String> {
    let rel = cfg.get("storage.defaults")?;
    let path = Path::new("/var/lib/fw/defaults").join(rel);
    fs::read_to_string(&path)
}

pub fn load_signing_key(cfg: &Config) -> io::Result<String> {
    let rel = cfg.get("storage.signing_key")?;
    let path = Path::new("/etc/fw/keys").join(rel);
    fs::read_to_string(&path)
}

pub fn load_trust_store(cfg: &Config) -> io::Result<String> {
    let rel = cfg.get("storage.trust_store")?;
    let path = Path::new("/etc/fw/ca").join(rel);
    fs::read_to_string(&path)
}

pub fn load_bundle_index(cfg: &Config) -> io::Result<String> {
    let rel = cfg.get("storage.bundle_index")?;
    let path = Path::new("/var/lib/fw/bundles").join(rel);
    fs::read_to_string(&path)
}

