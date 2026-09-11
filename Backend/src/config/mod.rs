use serde::Deserialize;
use std::fs;
use std::path::Path;

#[derive(Deserialize, Debug)]
pub struct Cfg {}

use log::info;
use serde::Deserialize;
use std::fs;
use std::path::Path;

#[derive(Deserialize, Debug)]
pub struct Cfg {
    //Settings
    pub host: String,
    pub port: usize,
    pub worker_concurrency: usize,

    //User setting
    pub user_timeout: usize,
    pub user_health_interval: usize,
    pub user_health_failures: usize,

    //Backend setting
    pub backend_timeout: usize,
    pub backend_health_interval: usize,
    pub backend_health_failures: usize,

    //Backends
    pub backends: Vec<i32>, //ent_backend::Backend>,
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
