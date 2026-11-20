//! Thin wrappers used by the ingest side. They take a path that has
//! already been assembled by the caller and do not validate it.

use std::fs;
use std::io;
use std::path::Path;

pub fn read_text(path: &Path) -> io::Result<String> {
    fs::read_to_string(path)
}

pub fn read_bytes(path: &Path) -> io::Result<Vec<u8>> {
    fs::read(path)
}

pub fn write_text(path: &Path, body: &str) -> io::Result<()> {
    fs::write(path, body)
}

pub fn write_bytes(path: &Path, body: &[u8]) -> io::Result<()> {
    fs::write(path, body)
}

