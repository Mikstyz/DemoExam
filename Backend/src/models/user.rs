use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Clone, Debug, PartialEq, Eq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "users")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = false)]
    pub id: Uuid,
    pub login: String,
    pub password_hash: String,

    pub first_name: String, // Имя
    pub last_name: String,  // Фамилия
    pub surname: String,    // Отчество
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(has_many = "super::order::Entity")]
    Order,

    #[sea_orm(has_many = "super::shop::Entity")]
    Shop,

    #[sea_orm(has_one = "super::user_avatar::Entity")]
    Avatar,
}

impl Related<super::order::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Order.def()
    }
}

// ДОБАВЛЕНО: Реализация связи с магазинами
impl Related<super::shop::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Shop.def()
    }
}

impl Related<super::user_avatar::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Avatar.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
