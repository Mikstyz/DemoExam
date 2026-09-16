use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Clone, Debug, PartialEq, Eq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "products")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = false)]
    pub id: Uuid,
    pub owner_id: Uuid,
    pub name: String,
    pub count: i64,
    pub price: i64,
    pub description: Option<String>,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::user::Entity",
        from = "Column::OwnerId",
        to = "super::user::Column::Id"
    )]
    User,

    #[sea_orm(has_many = "super::order_product::Entity")]
    OrderProduct,
}

impl Related<super::user::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::User.def()
    }
}

impl Related<super::order_product::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::OrderProduct.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
