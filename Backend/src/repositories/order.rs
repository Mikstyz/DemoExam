use rusqlite::{Connection, OptionalExtension, Result, params};
use std::{sync::Arc, vec};

pub struct OrderRepo {
    db: Arc<Connection>,
}

impl OrderRepo {
    pub fn new(db: Arc<Connection>) -> Self {
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

    pub fn select(&self, id: u128, fields: Vec<String>) -> Option<bool> {
        let request = "";
        None
    }

    pub fn update(&self, id: u128) -> Option<bool> {
        let request = "";
        None
    }
}
