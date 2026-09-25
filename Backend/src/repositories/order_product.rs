use sea_orm::{DatabaseConnection, DbErr, DeleteResult};
use uuid::Uuid;

use crate::models::order_product;

pub struct OrderProductRepo<'a> {
    db: &'a DatabaseConnection,
}

impl<'a> OrderProductRepo<'a> {
    pub fn new(db: &'a DatabaseConnection) -> Self {
        Self { db: db }
    }

    pub fn is(&self, id: Uuid) -> Option<bool> {
        todo!()
    }
}
