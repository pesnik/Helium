export interface FileNode {
    name: string;
    path: string;
    size: number;
    is_dir: boolean;
    children?: FileNode[];
    last_modified: number;
    file_count: number;
}
