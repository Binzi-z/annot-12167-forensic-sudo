//! Minimal request envelope used by the prototype. The real gateway
//! fills these fields from query strings, form bodies and multipart
//! uploads; nothing in here validates them.

use std::collections::HashMap;
use std::io;

#[derive(Default)]
pub struct Request {
    query: HashMap<String, String>,
    body: HashMap<String, String>,
    upload: Option<String>,
}

impl Request {
    pub fn query(&self, key: &str) -> io::Result<String> {
        self.query
            .get(key)
            .cloned()
            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "missing query"))
    }

    pub fn body_field(&self, key: &str) -> io::Result<String> {
        self.body
            .get(key)
            .cloned()
            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "missing body"))
    }

    pub fn upload_name(&self) -> io::Result<String> {
        self.upload
            .clone()
            .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "missing file"))
    }
}

