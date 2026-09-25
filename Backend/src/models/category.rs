use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Clone, Debug, PartialEq, Eq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "category")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = false)]
    pub id: Uuid,
    pub parent_id: Option<Uuid>,

    pub name: String,
    pub slug: String,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(has_many = "super::product::Entity")]
    Product,

    // Связь «У этой категории есть много подкатегорий»
    #[sea_orm(has_many = "Entity")]
    Subcategories,

    // Связь «Эта подкатегория принадлежит родительской категории»
    #[sea_orm(
        belongs_to = "Entity",
        from = "Column::ParentId",
        to = "Column::Id",
        on_update = "Cascade",
        on_delete = "Cascade"
    )]
    ParentCategory,
}

impl Related<super::product::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Product.def()
    }
}

// связь на саму себя для получения подкатегорий
impl Related<Entity> for Entity {
    fn to() -> RelationDef {
        // связь на саму себя для получения под категорий
        Relation::Subcategories.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
