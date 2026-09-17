use rusqlite::{Connection, OptionalExtension, Result, params};
use std::{sync::Arc, vec};

pub struct ProductRepo {
    db: Arc<Connection>,
}

impl ProductRepo {
    pub fn new(db: Arc<Connection>) -> Self {
        Self { db: db }
    }

    pub fn is(&self, id: u128) -> Option<bool> {
        let request = "";
        None
    }

    pub fn add(&self) -> Option<bool> {
        let request = "";
        None
    }

    pub fn select(&self, id: u128) -> Option<bool> {
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

    pub fn search(&self, filters: Vec<String>) -> Option<bool> {
        let request = "";
        None
    }
}
