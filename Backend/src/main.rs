use log::{self, info};

//config
pub mod config {
    pub mod cfg;
}
use crate::config::cfg::Cfg;

pub mod enums;

pub mod db;

pub mod dto;
pub mod models;

pub mod handlers;
pub mod router;

pub mod repositories;
pub mod services;

//constants
const CONFIG_DIR: &str = "config.toml";

#[tokio::main]
async fn main() -> std::result::Result<(), Box<dyn std::error::Error>> {
    env_logger::init();
    let cfg = Cfg::load(CONFIG_DIR)?;

    let db_conn = db::Db::initialization(&cfg.dbdir);

    //
    Ok(())
}
