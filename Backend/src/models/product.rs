use chrono::{DateTime, Utc};
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Clone, Debug, PartialEq, Eq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "products")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = false)]
    pub id: Uuid,
    pub shop_id: Uuid,
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
        belongs_to = "super::shop::Entity",
        from = "Column::ShopId",
        to = "super::shop::Column::Id",
        on_update = "Cascade",
        on_delete = "Cascade" // Если магазин удален — удаляются и все его товары
    )]
    Shop,

    #[sea_orm(
        belongs_to = "super::category::Entity",
        from = "Column::CategoryId",
        to = "super::category::Column::Id",
        on_update = "Cascade",
        on_delete = "Restrict" // Запрет на удаление категории, если в ней есть товары
    )]
    Category,

    #[sea_orm(has_many = "super::order_product::Entity")]
    OrderProduct,

    #[sea_orm(has_many = "super::product_images::Entity")]
    ProductImages,
}

// привязка к магазину
impl Related<super::shop::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Shop.def()
    }
}

// привязка продукта к категории
impl Related<super::category::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Category.def()
    }
}

// привязка продукта к заказу
impl Related<super::order_product::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::OrderProduct.def()
    }
}

// привязка картинок товара к продукту
impl Related<super::product_images::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::ProductImages.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
