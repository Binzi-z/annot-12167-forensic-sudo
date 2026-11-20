//! Template include. `TemplateEngine` is an in-tree stub: it keeps the
//! rendered bodies in memory, but `add_template_file` reads from disk.

use std::collections::HashMap;
use std::fs;
use std::io;

use fw_rpc::Request;

#[derive(Default)]
pub struct TemplateEngine {
    templates: HashMap<String, String>,
}

impl TemplateEngine {
    pub fn add_template_file(&mut self, path: &str) -> io::Result<()> {
        let body = fs::read_to_string(path)?;
        self.templates.insert(path.to_string(), body);
        Ok(())
    }

    pub fn render(&self, name: &str, _ctx: &[(&str, String)]) -> io::Result<String> {
        Ok(self.templates.get(name).cloned().unwrap_or_default())
    }
}

pub fn render_report(engine: &mut TemplateEngine, req: &Request) -> io::Result<String> {
    let name = req.query("template")?;
    let path = format!("templates/{}", name);
    engine.add_template_file(&path)?;
    engine.render("report", &[])
}

pub fn render_invoice(engine: &mut TemplateEngine, req: &Request) -> io::Result<String> {
    let name = req.query("invoice")?;
    let path = format!("templates/{}", name);
    engine.add_template_file(&path)?;
    engine.render("report", &[])
}

pub fn render_receipt(engine: &mut TemplateEngine, req: &Request) -> io::Result<String> {
    let name = req.body_field("receipt")?;
    let path = format!("templates/{}", name);
    engine.add_template_file(&path)?;
    engine.render("report", &[])
}

pub fn render_digest(req: &Request) -> io::Result<String> {
    let name = req.upload_name()?;
    let path = format!("templates/{}", name);
    fs::read_to_string(&path)
}

pub fn render_summary(req: &Request) -> io::Result<String> {
    let name = req.query("summary")?;
    let path = format!("templates/{}", name);
    fs::read_to_string(&path)
}

pub fn render_alert(cfg: &fw_config::Config) -> io::Result<String> {
    let name = cfg.get("templates.alert")?;
    let path = format!("templates/{}", name);
    fs::read_to_string(&path)
}


// ---- benign: fixed templates and an allowlisted name ----

pub fn render_base(engine: &mut TemplateEngine) -> io::Result<String> {
    engine.add_template_file("templates/base.hbs")?;
    engine.render("base", &[])
}

pub fn read_mail_template() -> io::Result<String> {
    fs::read_to_string("templates/mail.hbs")
}

pub fn read_report_template() -> io::Result<String> {
    fs::read_to_string("templates/report.hbs")
}

pub fn render_allowlisted(engine: &mut TemplateEngine, req: &Request) -> io::Result<String> {
    let name = req.query("template")?;
    let path = match name.as_str() {
        "base" => "templates/base.hbs",
        "mail" => "templates/mail.hbs",
        _ => return Err(io::Error::new(io::ErrorKind::InvalidInput, "unknown")),
    };
    engine.add_template_file(path)?;
    engine.render(&name, &[])
}

