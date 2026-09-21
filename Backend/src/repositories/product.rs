use sea_orm::{DatabaseConnection, DbErr, DeleteResult};
use uuid::Uuid;

use crate::models::product;

pub struct ProductRepo<'a> {
    db: &'a DatabaseConnection,
}

impl<'a> ProductRepo<'a> {
    pub fn new(db: &'a DatabaseConnection) -> Self {
        Self { db }
    }

    pub async fn find_by_id(&self, id: Uuid) -> Result<Option<product::Model>, DbErr> {
        todo!()
    }

    pub async fn find_all(&self) -> Result<Vec<product::Model>, DbErr> {
        todo!()
    }

    pub async fn find_by_owner(&self, owner_id: Uuid) -> Result<Vec<product::Model>, DbErr> {
        todo!()
    }

    pub async fn create(&self, product: product::ActiveModel) -> Result<product::Model, DbErr> {
        todo!()
    }

    pub async fn update(&self, product: product::ActiveModel) -> Result<product::Model, DbErr> {
        todo!()
    }

    pub async fn delete(&self, id: Uuid) -> Result<DeleteResult, DbErr> {
        todo!()
    }
}
