use tauri::command;
use crate::scanner::{scan_directory, FileNode};
use std::collections::HashMap;
use std::sync::Mutex;
use std::time::{SystemTime, Duration};
use lazy_static::lazy_static;

struct CacheEntry {
    node: FileNode,
    timestamp: SystemTime,
}

lazy_static! {
    static ref SCAN_CACHE: Mutex<HashMap<String, CacheEntry>> = Mutex::new(HashMap::new());
}

// 1 hour cache TTL, maybe configurable?
const CACHE_TTL: u64 = 60 * 60; 

#[command]
pub async fn scan_dir(path: String) -> Result<FileNode, String> {
    scan_dir_internal(path, false).await
}

#[command]
pub async fn refresh_scan(path: String) -> Result<FileNode, String> {
    scan_dir_internal(path, true).await
}

async fn scan_dir_internal(path: String, force_refresh: bool) -> Result<FileNode, String> {
    // Check cache first
    if !force_refresh {
        let cache = SCAN_CACHE.lock().map_err(|e| e.to_string())?;
        if let Some(entry) = cache.get(&path) {
            if let Ok(elapsed) = entry.timestamp.elapsed() {
                if elapsed.as_secs() < CACHE_TTL {
                    return Ok(entry.node.clone());
                }
            }
        }
    }

    // Run in blocking thread to avoid blocking the async runtime
    let path_clone = path.clone();
    let result = tauri::async_runtime::spawn_blocking(move || {
        scan_directory(&path_clone)
    }).await.map_err(|e| e.to_string())??;

    // Update cache
    let mut cache = SCAN_CACHE.lock().map_err(|e| e.to_string())?;
    cache.insert(path, CacheEntry {
        node: result.clone(),
        timestamp: SystemTime::now(),
    });

    Ok(result)
}

#[command]
pub fn clear_cache() {
    if let Ok(mut cache) = SCAN_CACHE.lock() {
        cache.clear();
    }
}

#[command]
pub fn open_in_explorer(path: String) {
    #[cfg(target_os = "windows")]
    {
        use std::process::Command;
        Command::new("explorer")
            .arg(&path)
            .spawn()
            .unwrap();
    }
    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        Command::new("open")
            .arg(&path)
            .spawn()
            .unwrap();
    }
    #[cfg(target_os = "linux")]
    {
        use std::process::Command;
        Command::new("xdg-open")
            .arg(&path)
            .spawn()
            .unwrap();
    }
}
