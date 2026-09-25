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

    pub fn is(&self, id: Uuid) -> Option<bool> {
        todo!()
    }
}
