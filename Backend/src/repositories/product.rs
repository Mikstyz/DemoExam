use sea_orm::{DatabaseConnection, DbErr, DeleteResult};
use uuid::Uuid;

use crate::models::product;

pub struct ProductRepo<'a> {
    db: &'a DatabaseConnection,
}

impl<'a> ProductRepo<'a> {
    pub fn new(db: &'a DatabaseConnection) -> Self {
        Self { db: db }
    }

    pub fn is(&self, id: Uuid) -> Option<bool> {
        todo!()
    }
}
