//config
pub mod config {
    pub mod cfg;
}
use crate::config::cfg::Cfg;

pub mod db;

pub mod dto;
pub mod models;

pub mod handlers;
pub mod router;

pub mod repositories;
pub mod services;

//constants
const CONFIG_DIR: &str = "config.toml";
const DB: &str = "db";

#[tokio::main]
async fn main() {
    let config = Cfg::load(CONFIG_DIR);
}
