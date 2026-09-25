use chrono::{DateTime, Utc};
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Clone, Debug, PartialEq, Eq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "products")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = false)]
    pub id: Uuid,
    pub owner_id: Uuid,
    pub category_id: Uuid,
    pub created: DateTime<Utc>,

    pub name: String,
    pub description: Option<String>,

    pub reviews_count: i64,
    pub reviews_sum: i64,

    pub sales: String,
    pub count: i64,
    pub price: i64,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::user::Entity",
        from = "Column::OwnerId",
        to = "super::user::Column::Id",
        on_update = "Cascade",
        on_delete = "Restrict"
    )]
    User,

    #[sea_orm(
        belongs_to = "super::category::Entity",
        from = "Column::CategoryId",
        to = "super::category::Column::Id",

        //связь с котегориями
        on_update = "Cascade",
        on_delete = "Restrict" // Запрет на удаление категории, если в ней есть товары
    )]
    Category,

    #[sea_orm(has_many = "super::order_product::Entity")]
    OrderProduct,

    #[sea_orm(has_many = "super::product_images::Entity")]
    ProductImages,
}

impl Related<super::user::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::User.def()
    }
}

impl Related<super::category::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Category.def()
    }
}

impl Related<super::order_product::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::OrderProduct.def()
    }
}

impl Related<super::product_images::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::ProductImages.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
