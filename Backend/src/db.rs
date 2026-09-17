use crate::models;
use log::info;
use sea_orm::{ConnectionTrait, Database, DatabaseConnection, DbErr, Schema, Statement};

pub struct Db {
    pub db_connection: DatabaseConnection,
}

impl Db {
    pub async fn initialization(db_path: &str) -> Result<Self, DbErr> {
        let connection = Database::connect(format!("sqlite://{}?mode=rwc", db_path)).await?;

        info!("database initialized");

        Ok(Self {
            db_connection: connection,
        })
    }

    pub async fn create_tables(&self) -> Result<(), DbErr> {
        let backend = self.db_connection.get_database_backend();
        let schema = Schema::new(backend);

        let tables = [
            schema
                .create_table_from_entity(models::user::Entity)
                .if_not_exists()
                .to_owned(),
            schema
                .create_table_from_entity(models::product::Entity)
                .if_not_exists()
                .to_owned(),
            schema
                .create_table_from_entity(models::order::Entity)
                .if_not_exists()
                .to_owned(),
            schema
                .create_table_from_entity(models::order_product::Entity)
                .if_not_exists()
                .to_owned(),
        ];

        for statement in tables {
            self.db_connection
                .execute(backend.build(&statement))
                .await?;
        }

        info!("tables created");

        Ok(())
    }

    pub async fn print_schema(&self) -> Result<(), DbErr> {
        let backend = self.db_connection.get_database_backend();

        let tables = self
            .db_connection
            .query_all(Statement::from_string(
                backend,
                "SELECT name FROM sqlite_master \
                 WHERE type = 'table' \
                 AND name NOT LIKE 'sqlite_%' \
                 ORDER BY name"
                    .to_owned(),
            ))
            .await?;

        for table in tables {
            let table_name: String = table.try_get("", "name")?;

            println!("\nTABLE: {}", table_name);

            let columns = self
                .db_connection
                .query_all(Statement::from_string(
                    backend,
                    format!("PRAGMA table_info(\"{}\")", table_name),
                ))
                .await?;

            for column in columns {
                let name: String = column.try_get("", "name")?;
                let column_type: String = column.try_get("", "type")?;
                let not_null: i32 = column.try_get("", "notnull")?;
                let primary_key: i32 = column.try_get("", "pk")?;

                println!(
                    "  {} {}{}{}",
                    name,
                    column_type,
                    if not_null != 0 { " NOT NULL" } else { "" },
                    if primary_key != 0 { " PRIMARY KEY" } else { "" },
                );
            }

            let foreign_keys = self
                .db_connection
                .query_all(Statement::from_string(
                    backend,
                    format!("PRAGMA foreign_key_list(\"{}\")", table_name),
                ))
                .await?;

            for foreign_key in foreign_keys {
                let from: String = foreign_key.try_get("", "from")?;
                let target_table: String = foreign_key.try_get("", "table")?;
                let target_column: String = foreign_key.try_get("", "to")?;

                println!("  FK: {} -> {}.{}", from, target_table, target_column);
            }
        }

        Ok(())
    }
}
