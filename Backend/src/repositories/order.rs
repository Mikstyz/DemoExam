use sea_orm::{DatabaseConnection, DbErr, DeleteResult};
use uuid::Uuid;

use crate::models::order;

pub struct OrderRepo<'a> {
    db: &'a DatabaseConnection,
}

impl<'a> OrderRepo<'a> {
    pub fn new(db: &'a DatabaseConnection) -> Self {
        Self { db: db }
    }

    pub fn is(&self, id: u128) -> Option<bool> {
        todo!()
    }

    pub fn add(&self, login: &str, password: &str) -> Option<bool> {
        todo!()
    }

    pub fn select(&self, id: u128, fields: Vec<String>) -> Option<bool> {
        todo!()
    }

    pub fn update(&self, id: u128) -> Option<bool> {
        todo!()
    }
}
