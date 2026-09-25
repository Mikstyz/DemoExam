use crate::enums::filters;

pub mod order;
pub mod order_product;
pub mod product;
pub mod shop;
pub mod user;

pub struct SearchQuery {
    pub filters: Vec<filters::Filter>,
    pub sort: Option<filters::SortBy>,
}

//Initialization user repositories
pub struct UserRepo {}

impl UserRepo {
    pub fn is_table() -> Option<()> {
        None
    }

    pub fn create_tables() -> Option<()> {
        None
    }
}

//Initialization product repositories
pub struct ProductRepo {}

impl ProductRepo {
    pub fn is_table() -> Option<()> {
        None
    }

    pub fn create_tables() -> Option<()> {
        None
    }
}
