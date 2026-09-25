use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, Eq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "product_images")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: Uuid,
    pub product_id: Uuid,
    pub file_path: String,
    pub is_main: bool,   // is preview
    pub sort_order: i32, // 0, 1, 2...)
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        fk_name = "fk_product_images_product",
        belongs_to = "super::product::Entity",
        from = "Column::ProductId",
        to = "super::product::Column::Id",
        on_update = "Cascade",
        on_delete = "Cascade" // if product remove to remove images
    )]
    Product,
}

impl Related<super::product::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Product.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
