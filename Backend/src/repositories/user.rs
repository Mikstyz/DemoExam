use crate::db::Db;
use rusqlite::{Connection, OptionalExtension, Result, params};
use std::sync::Arc;

pub struct UserRepo {
    db: Arc<Db>,
}

impl UserRepo {
    pub fn new(db: Arc<Db>) -> Self {
        Self { db: db }
    }

    pub fn is(&self, id: u128) -> Option<bool> {
        let request = "";
        None
    }

    pub fn add(&self, login: &str, password: &str) -> Option<bool> {
        let request = "";
        None
    }

    pub fn authentication(&self, login: &str, password: &str) -> Option<bool> {
        let request = "";
        None
    }

    pub fn select(&self, id: u128, fields: Vec<String>) -> Option<bool> {
        let request = "";
        None
    }

    pub fn update(&self, id: u128) -> Option<bool> {
        let request = "";
        None
    }

    pub fn remove(&self, id: u128) -> Option<bool> {
        let request = "";
        None
    }
}
