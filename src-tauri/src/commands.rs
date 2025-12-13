use tauri::command;
use crate::scanner::{scan_directory, FileNode};

#[command]
pub async fn scan_dir(path: String) -> Result<FileNode, String> {
    // Run in blocking thread to avoid blocking the async runtime
    tauri::async_runtime::spawn_blocking(move || {
        scan_directory(&path)
    }).await.map_err(|e| e.to_string())?
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
