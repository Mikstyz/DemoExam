use std::io::{Error, ErrorKind, Result};
use std::path::{Path, PathBuf};
use tokio::fs;

pub struct FileStorage {
    dir: PathBuf,
}

impl FileStorage {
    pub fn new(dir: PathBuf) -> Self {
        Self { dir }
    }

    pub async fn exists(&self, path: impl AsRef<Path>) -> bool {
        fs::try_exists(self.dir.join(path)).await.unwrap_or(false)
    }

    pub async fn select(&self, path: impl AsRef<Path>) -> Result<Vec<u8>> {
        fs::read(self.dir.join(path)).await
    }

    pub async fn save(&self, path: impl AsRef<Path>, data: &[u8]) -> Result<PathBuf> {
        let path = self.dir.join(path);

        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent).await?;
        }

        fs::write(&path, data).await?;

        Ok(path)
    }

    pub async fn update(&self, path: impl AsRef<Path>, data: &[u8]) -> Result<PathBuf> {
        let path = self.dir.join(path);

        if !fs::try_exists(&path).await? {
            return Err(Error::new(ErrorKind::NotFound, "file does not exist"));
        }

        fs::write(&path, data).await?;

        Ok(path)
    }

    pub async fn delete(&self, path: impl AsRef<Path>) -> Result<()> {
        fs::remove_file(self.dir.join(path)).await
    }
}
