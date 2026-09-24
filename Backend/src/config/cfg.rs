use log::info;
use serde::Deserialize;
use std::fs;
use std::path::Path;

#[derive(Deserialize, Debug)]
pub struct Cfg {
    // Settings
    pub host: String,
    pub port: usize,
    pub dbdir: String,
    pub storage_dir: String,
}

impl Cfg {
    pub fn load(dir: &str) -> Result<Self, Box<dyn std::error::Error>> {
        info!("load config");
        let dir = Path::new(dir);
        let content = fs::read_to_string(dir)?;

        let cfg: Cfg = toml::from_str(&content)?;

        Ok(cfg)
    }
}
