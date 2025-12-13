use jwalk::WalkDir;
use serde::{Deserialize, Serialize};
use std::time::SystemTime;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct FileNode {
    pub name: String,
    pub path: String,
    pub size: u64,
    pub is_dir: bool,
    pub children: Option<Vec<FileNode>>,
    pub last_modified: u64,
    pub file_count: u64,
}

pub fn scan_directory(path: &str) -> Result<FileNode, String> {
    let root_path = std::path::Path::new(path);
    if !root_path.exists() {
        return Err("Directory does not exist".to_string());
    }

    // Use jwalk for parallel scanning
    // sort: true ensures consistent output, though slightly slower. fast_sort is better.
    let walk = WalkDir::new(path)
        .skip_hidden(false)
        .sort(true)
        .parallelism(jwalk::Parallelism::RayonNewPool(4)); // Safe default

    let mut total_size = 0;
    let mut file_count = 0;


    // Note: jwalk is great for deep stats, but for a file explorer view we often just want:
    // 1. Current dir stats
    // 2. Immediate children list
    // 3. Stats for immediate children (recursive)
    
    // However, calculating recursive size for ALL children can be slow if we iterate everything.
    // The Python version did a specialized "scan direct subdirs and calculate their sizes in parallel".
    // We can replicate that logic or use jwalk's custom state to aggregate up.
    
    // For "Enterprise Grade" speed, we should probably:
    // 1. Iterate immediate children.
    // 2. For each child directory, spawn a parallel task to calculate its size (deep walk).
    
    // But jwalk does this automatically if we configure it right?
    // Actually jwalk iterates the whole tree.
    
    // Let's implement the "shallow list + deep stat" approach manually with Rayon for max control.
    // This perfectly mimics the Python App's logic but in Rust (faster).
    
    use rayon::prelude::*;
    
    // Get immediate children first
    let read_dir = std::fs::read_dir(path).map_err(|e| e.to_string())?;
    
    let entries: Vec<_> = read_dir.filter_map(|e| e.ok()).collect();
    
    // Partition into files and dirs
    let mut files = Vec::new();
    let mut dirs = Vec::new();
    
    for entry in entries {
        let metadata = entry.metadata().map_err(|e| e.to_string())?;
        if metadata.is_dir() {
            dirs.push(entry);
        } else {
            files.push((entry, metadata));
        }
    }
    
    // Process files in current dir
    for (_entry, meta) in &files {
        total_size += meta.len();
        file_count += 1;
    }
    
    // Process subdirectories in parallel
    let dir_results: Vec<FileNode> = dirs.par_iter_mut().map(|entry| {
        let path = entry.path();
        let path_str = path.to_string_lossy().to_string();
        let name = entry.file_name().to_string_lossy().to_string();
        
        // Deep scan this subdirectory to get total size
        // We use jwalk here for the deep scan of this specific subdir
        let (size, count) = get_dir_stats(&path);
        
        let metadata = entry.metadata().unwrap();
        let modified = metadata.modified().unwrap_or(SystemTime::UNIX_EPOCH)
            .duration_since(SystemTime::UNIX_EPOCH).unwrap_or_default().as_secs();

        FileNode {
            name,
            path: path_str,
            size,
            is_dir: true,
            children: None, // We don't return grandchild details to frontend, only direct children
            last_modified: modified,
            file_count: count,
        }
    }).collect();
    
    // Add dirs to total stats
    for dir in &dir_results {
        total_size += dir.size;
        file_count += dir.file_count;
    }
    
    // Construct children list for the response (files + folder summaries)
    // Files first? Or mixed? Usually folders first.
    let mut children_nodes = dir_results;
    children_nodes.sort_by(|a, b| b.size.cmp(&a.size)); // Sort by size desc
    
    // Add files as nodes if needed? 
    // The Python app showed folders. Files were grouped? 
    // "files_entry" was a virtual entry.
    // Let's just return folders in the children list for now, or match Python behavior.
    // We'll mimic the structure: folders list is what matters most for space analysis.
    
    Ok(FileNode {
        name: root_path.file_name().unwrap_or_default().to_string_lossy().to_string(),
        path: path.to_string(),
        size: total_size,
        is_dir: true,
        children: Some(children_nodes),
        last_modified: 0,
        file_count,
    })
}

fn get_dir_stats(path: &std::path::Path) -> (u64, u64) {
    let mut size = 0;
    let mut count = 0;
    
    // jwalk is very fast for just summing up
    for entry in WalkDir::new(path).skip_hidden(false) {
        if let Ok(entry) = entry {
            if entry.file_type().is_file() {
                size += entry.metadata().map(|m| m.len()).unwrap_or(0);
                count += 1;
            }
        }
    }
    
    (size, count)
}
