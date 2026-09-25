use sea_orm::{DatabaseConnection, DbErr, DeleteResult};
use uuid::Uuid;

use crate::models::shop;

pub struct ShopRepo<'a> {
    db: &'a DatabaseConnection,
}

impl<'a> ShopRepo<'a> {
    pub fn new(db: &'a DatabaseConnection) -> Self {
        Self { db }
    }
}
