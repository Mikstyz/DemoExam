use log::{self, info};
use rusqlite::{Connection, OptionalExtension, Result, params};

//Initialization data base
pub struct Db {
    pub db_connection: Connection,
}

impl Db {
    pub fn initialization(db_path: &str) -> Result<Self> {
        let connection = Connection::open(db_path)?;

        info!("db initializations!");
        Ok(Self {
            db_connection: connection,
        })
    }
}
