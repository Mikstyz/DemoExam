use sea_orm::{DatabaseConnection, DbErr, DeleteResult};
use uuid::Uuid;

use crate::models::user;

pub struct UserRepo<'a> {
    db: &'a DatabaseConnection,
}

impl<'a> UserRepo<'a> {
    pub fn new(db: &'a DatabaseConnection) -> Self {
        Self { db: db }
    }

    pub fn is(&self, id: Uuid) -> Option<bool> {
        todo!()
    }

    pub fn add(&self, login: &str, password: &str) -> Option<bool> {
        todo!()
    }

    pub fn authentication(&self, login: &str, password: &str) -> Option<bool> {
        todo!()
    }

    pub fn select(&self, id: Uuid, fields: Vec<String>) -> Option<bool> {
        todo!()
    }

    pub fn update(&self, id: Uuid) -> Option<bool> {
        todo!()
    }

    pub fn remove(&self, id: Uuid) -> Option<bool> {
        todo!()
    } 
}
