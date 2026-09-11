use crate::db::Db;
use crate::models::product::Product;
use rusqlite::{Connection, OptionalExtension, Result, params};
use std::sync::Arc;

pub struct ProductRepo {
    db: Arc<Db>,
}

impl ProductRepo {
    pub fn new(db: Arc<Db>) -> Self {
        Self { db: db }
    }

    pub fn is(&self) -> Option<bool> {
        None
    }
    pub fn add(&self) -> Option<bool> {
        None
    }
    pub fn select(&self) -> Option<bool> {
        None
    }

    pub fn update(&self) -> Option<bool> {
        None
    }

    pub fn remove(&self) -> Option<bool> {
        None
    }
}
