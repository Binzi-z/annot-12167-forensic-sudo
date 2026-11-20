//! Update-bundle extraction. The zip reader is a small in-tree stub so the
//! corpus does not depend on an external crate; entry semantics match the
//! real one (by_name / entries / name).

use std::fs::{self, File};
use std::io::{self, Write};
use std::path::Path;

use fw_rpc::Request;

pub struct ZipFile {
    name: String,
    data: Vec<u8>,
}

impl ZipFile {
    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn data(&self) -> &[u8] {
        &self.data
    }

    pub fn enclosed_name(&self) -> Option<String> {
        let mut parts = Vec::new();
        for part in self.name.split('/') {
            if part == ".." {
                return None;
            }
            if !part.is_empty() && part != "." {
                parts.push(part);
            }
        }
        Some(parts.join("/"))
    }
}

pub struct ZipArchive<R> {
    entries: Vec<ZipFile>,
    _reader: R,
}

impl<R> ZipArchive<R> {
    pub fn by_name(&mut self, name: &str) -> io::Result<ZipFile> {
        for entry in &self.entries {
            if entry.name == name {
                return Ok(ZipFile { name: entry.name.clone(), data: entry.data.clone() });
            }
        }
        Err(io::Error::new(io::ErrorKind::NotFound, "entry"))
    }

    pub fn entries(&mut self) -> Vec<ZipFile> {
        self.entries
            .iter()
            .map(|e| ZipFile { name: e.name.clone(), data: e.data.clone() })
            .collect()
    }
}

pub fn extract_update(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {
    let mut entry = archive.by_name(&name)?;
    let out = dest.join(entry.name());
    let mut file = File::create(&out)?;
    file.write_all(entry.data())?;
    Ok(())
}

pub fn extract_theme(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {
    let mut entry = archive.by_name(&name)?;
    let out = dest.join(entry.name());
    let mut file = File::create(&out)?;
    file.write_all(entry.data())?;
    Ok(())
}

pub fn extract_plugin(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {
    let mut entry = archive.by_name(&name)?;
    let out = dest.join(entry.name());
    let mut file = File::create(&out)?;
    file.write_all(entry.data())?;
    Ok(())
}

pub fn extract_locale(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {
    let mut entry = archive.by_name(&name)?;
    let out = dest.join(entry.name());
    let mut file = File::create(&out)?;
    file.write_all(entry.data())?;
    Ok(())
}

pub fn extract_ca_bundle(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {
    let mut entry = archive.by_name(&name)?;
    let out = dest.join(entry.name());
    let mut file = File::create(&out)?;
    file.write_all(entry.data())?;
    Ok(())
}

pub fn extract_doc(archive: &mut ZipArchive<File>, dest: &Path, cfg: &fw_config::Config) -> io::Result<()> {
    let mut entry = archive.by_name(&name)?;
    let out = dest.join(entry.name());
    let mut file = File::create(&out)?;
    file.write_all(entry.data())?;
    Ok(())
}

pub fn extract_font(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {
    let mut entry = archive.by_name(&name)?;
    let out = dest.join(entry.name());
    let mut file = File::create(&out)?;
    file.write_all(entry.data())?;
    Ok(())
}

pub fn unpack_all(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {
    let prefix = req.query("dir")?;
    for entry in archive.entries() {
        let out = dest.join(prefix.as_str()).join(entry.name());
        fs::write(&out, entry.data())?;
    }
    Ok(())
}

pub fn unpack_assets(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {
    let prefix = req.upload_name()?;
    for entry in archive.entries() {
        let out = dest.join(prefix.as_str()).join(entry.name());
        fs::write(&out, entry.data())?;
    }
    Ok(())
}

pub fn unpack_modules(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {
    let prefix = req.query("target")?;
    for entry in archive.entries() {
        let out = dest.join(prefix.as_str()).join(entry.name());
        fs::write(&out, entry.data())?;
    }
    Ok(())
}

pub fn unpack_samples(archive: &mut ZipArchive<File>, dest: &Path, req: &Request) -> io::Result<()> {
    let prefix = req.body_field("stage")?;
    for entry in archive.entries() {
        let out = dest.join(prefix.as_str()).join(entry.name());
        fs::write(&out, entry.data())?;
    }
    Ok(())
}

pub fn unpack_static(archive: &mut ZipArchive<File>, dest: &Path, cfg: &fw_config::Config) -> io::Result<()> {
    let prefix = cfg.get("extract.dir")?;
    for entry in archive.entries() {
        let out = dest.join(prefix.as_str()).join(entry.name());
        fs::write(&out, entry.data())?;
    }
    Ok(())
}


// ---- benign: fixed output path and an enclosed_name-guarded loop ----

pub fn write_unpack_log(body: &str) -> io::Result<()> {
    fs::write("/var/log/fw-unpack.log", body)
}

pub fn create_marker() -> io::Result<File> {
    File::create("/var/lib/fw/unpacked")
}

pub fn extract_checked(archive: &mut ZipArchive<File>, dest: &Path) -> io::Result<()> {
    for entry in archive.entries() {
        let Some(safe) = entry.enclosed_name() else {
            continue;
        };
        let out = dest.join(safe);
        fs::write(&out, entry.data())?;
    }
    Ok(())
}

