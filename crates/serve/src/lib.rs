//! Static asset service. `NamedFile` is an in-tree stub of the framework
//! type: it only records the path it was asked to open.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};

use fw_rpc::Request;

pub struct NamedFile {
    path: PathBuf,
}

impl NamedFile {
    pub fn open<P: AsRef<Path>>(path: P) -> io::Result<NamedFile> {
        let path = path.as_ref();
        if !path.exists() {
            return Err(io::Error::new(io::ErrorKind::NotFound, "asset"));
        }
        Ok(NamedFile { path: path.to_path_buf() })
    }

    pub fn path(&self) -> &Path {
        &self.path
    }
}

pub fn serve_asset(public: &Path, req: &Request) -> io::Result<NamedFile> {
    let rel = req.query("file")?;
    let path = public.join(rel);
    NamedFile::open(&path)
}

pub fn serve_download(public: &Path, req: &Request) -> io::Result<NamedFile> {
    let rel = req.query("download")?;
    let path = public.join(rel);
    NamedFile::open(&path)
}

pub fn serve_media(public: &Path, req: &Request) -> io::Result<NamedFile> {
    let rel = req.body_field("media")?;
    let path = public.join(rel);
    NamedFile::open(&path)
}

pub fn serve_font(public: &Path, req: &Request) -> io::Result<NamedFile> {
    let rel = req.query("font")?;
    let path = public.join(rel);
    NamedFile::open(&path)
}

pub fn serve_doc(public: &Path, req: &Request) -> io::Result<NamedFile> {
    let rel = req.upload_name()?;
    let path = public.join(rel);
    NamedFile::open(&path)
}

pub fn serve_report(public: &Path, req: &Request) -> io::Result<NamedFile> {
    let rel = req.query("report")?;
    let path = public.join(rel);
    NamedFile::open(&path)
}

pub fn serve_upload(public: &Path, req: &Request) -> io::Result<NamedFile> {
    let rel = req.upload_name()?;
    let path = public.join(rel);
    NamedFile::open(&path)
}


// ---- benign: fixed entry points and a guarded download ----

pub fn serve_index(public: &Path) -> io::Result<NamedFile> {
    NamedFile::open(public.join("index.html"))
}

pub fn serve_favicon(public: &Path) -> io::Result<NamedFile> {
    NamedFile::open(public.join("favicon.ico"))
}

pub fn serve_readme() -> io::Result<NamedFile> {
    NamedFile::open("/usr/share/doc/fw/README")
}

pub fn serve_guarded(public: &Path, req: &Request) -> io::Result<NamedFile> {
    let rel = req.query("file")?;
    let path = public.join(rel);
    if !fw_common::path_util::canonicalize_prefix_ok(public, &path) {
        return Err(io::Error::new(io::ErrorKind::PermissionDenied, "outside"));
    }
    NamedFile::open(&path)
}

