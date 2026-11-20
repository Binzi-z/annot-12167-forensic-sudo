//! Composition root. The asset resolver is chosen at start-up from the
//! deployment profile and used through a trait object, so the concrete
//! implementation is not visible to a purely syntactic call graph.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};

use fw_rpc::Request;

pub trait AssetSource {
    fn resolve(&self, key: &str) -> String;
}

pub struct FsSource {
    root: PathBuf,
}

pub struct CdnSource {
    base: String,
}

impl AssetSource for FsSource {
    fn resolve(&self, key: &str) -> String {
        format!("{}/{}", self.root.display(), key)
    }
}

impl AssetSource for CdnSource {
    fn resolve(&self, key: &str) -> String {
        format!("{}/{}", self.base, key)
    }
}

fn resolve_and_open_profile(source: &dyn AssetSource, req: &Request) -> io::Result<String> {
    let key = req.query("asset")?;
    let path = source.resolve(&key);
    fs::read_to_string(&path)
}

fn resolve_and_open_theme(source: &dyn AssetSource, req: &Request) -> io::Result<String> {
    let key = req.query("theme")?;
    let path = source.resolve(&key);
    fs::read_to_string(&path)
}

fn resolve_and_open_locale(source: &dyn AssetSource, req: &Request) -> io::Result<String> {
    let key = req.query("locale")?;
    let path = source.resolve(&key);
    fs::read_to_string(&path)
}


fn read_version() -> io::Result<String> {
    fs::read_to_string("/etc/fw/version")
}

fn read_boot_config() -> io::Result<String> {
    fs::read_to_string("/boot/fw.cfg")
}

fn main() -> io::Result<()> {
    let root = Path::new("/srv/assets");
    let source = FsSource { root: root.to_path_buf() };
    let req = Request::default();
    let _profile = resolve_and_open_profile(&source, &req)?;
    let _version = read_version()?;
    Ok(())
}

