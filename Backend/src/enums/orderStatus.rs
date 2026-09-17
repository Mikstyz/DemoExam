use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize}; // Импортируем типы SeaORM

#[derive(
    Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize, DeriveActiveEnum, EnumIter,
)]
#[sea_orm(
    rs_type = "String",          // В Rust это будет String (на уровне драйвера)
    db_type = "String(StringLen::N(20))" // В БД это будет VARCHAR(20) / TEXT
)]
#[serde(rename_all = "snake_case")]
pub enum OrderStatus {
    #[sea_orm(string_value = "created")]
    Created,
    #[sea_orm(string_value = "pending")]
    Pending,
    #[sea_orm(string_value = "assembling")]
    Assembling,
    #[sea_orm(string_value = "assembled")]
    Assembled,
    #[sea_orm(string_value = "in_transit")]
    InTransit,
    #[sea_orm(string_value = "arrived")]
    Arrived,
    #[sea_orm(string_value = "delivered")]
    Delivered,
    #[sea_orm(string_value = "cancelled")]
    Cancelled,
    #[sea_orm(string_value = "refunded")]
    Refunded,
}
