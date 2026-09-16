use rusqlite::{Connection, OptionalExtension, Result, params};

pub mod product;
pub mod user;

//Initialization user repositories
pub struct UserRepo {}

impl UserRepo {
    pub fn create_tables() -> Option<()> {
        None
    }
}

//Initialization product repositories
pub struct ProductRepo {}

impl ProductRepo {
    pub fn create_tables() -> Option<()> {
        None
    }
}
