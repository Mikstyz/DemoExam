pub mod config {
    pub mod cfg;
}

pub mod dto;
pub mod handlers;
pub mod models;
pub mod router;
pub mod services;

const CONFIG_DIR: &str = "config.toml";
const DB: &str = "db";

#[tokio::main]
async fn main() {}
