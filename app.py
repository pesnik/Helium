import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import time
from pathlib import Path
import subprocess
import platform
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple

class StorageManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Helium v2.1")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Configure style
        self.setup_styles()
        
        # Variables
        self.current_path = tk.StringVar(value="D:\\Laboratory")
        self.scan_progress = tk.DoubleVar()
        self.status_text = tk.StringVar(value="Ready")
        self.total_size = tk.StringVar(value="Total: 0 GB")
        self.scanning = False
        self.scan_thread = None
        self.cancel_scan = False

        # Navigation history
        self.navigation_history = ["D:\\Laboratory"]
        self.history_index = 0
        self.max_history = 50

        # Data storage
        self.folder_data = []

        # Detailed progress tracking
        self.current_scan_folder = tk.StringVar(value="")
        self.scan_stats = tk.StringVar(value="")
        self.show_detailed_progress = tk.BooleanVar(value=True)

        # Persistent cache configuration
        self.cache_dir = Path.home() / ".helium_cache"
        self.cache_file = self.cache_dir / "scan_cache.json"
        self.scan_cache = {}  # path -> {folders: [], timestamp: float, total_size: int, subdirs_count: int}
        self.cache_ttl = 3600  # Cache validity: 1 hour (in seconds)
        self.cache_enabled = True  # Toggle for cache usage
        self.max_workers = 4  # Number of parallel threads for scanning

        # Load cache and settings
        self.load_settings()
        self.load_cache_from_disk()
        
        self.create_widgets()
        self.center_window()
        
    def setup_styles(self):
        """Configure modern dark theme styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure dark theme colors
        self.style.configure('Treeview', 
                           background='#3c3c3c',
                           foreground='white',
                           fieldbackground='#3c3c3c',
                           borderwidth=0,
                           font=('Segoe UI', 10))
        
        self.style.configure('Treeview.Heading',
                           background='#4a4a4a',
                           foreground='white',
                           relief='flat',
                           font=('Segoe UI', 10, 'bold'))
        
        self.style.configure('TButton',
                           background='#0078d4',
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 9))
        
        self.style.map('TButton',
                      background=[('active', '#106ebe'),
                                ('pressed', '#005a9e')])
        
        self.style.configure('TFrame', background='#2b2b2b')
        self.style.configure('TLabel', background='#2b2b2b', foreground='white', font=('Segoe UI', 9))
        self.style.configure('TProgressbar', troughcolor='#3c3c3c', background='#0078d4')
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Create the main interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        self.create_toolbar(main_frame)
        
        # Path selection frame
        self.create_path_frame(main_frame)
        
        # Main content area with paned window
        self.create_main_content(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_toolbar(self, parent):
        """Create toolbar with action buttons"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons (left side)
        nav_frame = ttk.Frame(toolbar)
        nav_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.back_btn = ttk.Button(nav_frame, text="◀ Back", 
                                  command=self.navigate_back, width=8, state='disabled')
        self.back_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        self.forward_btn = ttk.Button(nav_frame, text="Forward ▶", 
                                     command=self.navigate_forward, width=10, state='disabled')
        self.forward_btn.pack(side=tk.LEFT, padx=2)
        
        self.up_btn = ttk.Button(nav_frame, text="⬆ Up", 
                                command=self.navigate_up, width=6)
        self.up_btn.pack(side=tk.LEFT, padx=2)
        
        self.home_btn = ttk.Button(nav_frame, text="🏠 Home", 
                                  command=self.navigate_home, width=8)
        self.home_btn.pack(side=tk.LEFT, padx=2)
        
        # Action buttons (middle)
        action_frame = ttk.Frame(toolbar)
        action_frame.pack(side=tk.LEFT, padx=10)

        ttk.Button(action_frame, text="🔍 Scan",
                  command=self.start_scan, width=8).pack(side=tk.LEFT, padx=(0, 2))

        self.cancel_btn = ttk.Button(action_frame, text="⏹ Cancel",
                  command=self.cancel_scan_action, width=8, state='disabled')
        self.cancel_btn.pack(side=tk.LEFT, padx=2)

        ttk.Button(action_frame, text="🔄 Refresh",
                  command=self.refresh_scan, width=8).pack(side=tk.LEFT, padx=2)

        ttk.Button(action_frame, text="🧹 Clear Cache",
                  command=self.clear_cache, width=12).pack(side=tk.LEFT, padx=2)

        ttk.Button(action_frame, text="⚙️ Settings",
                  command=self.show_settings, width=10).pack(side=tk.LEFT, padx=2)

        ttk.Button(action_frame, text="📁 Explorer",
                  command=self.open_in_explorer, width=10).pack(side=tk.LEFT, padx=2)

        ttk.Button(action_frame, text="📊 Export",
                  command=self.export_report, width=8).pack(side=tk.LEFT, padx=2)
        
        # Right side info
        info_frame = ttk.Frame(toolbar)
        info_frame.pack(side=tk.RIGHT)

        # Cache info
        self.cache_info = tk.StringVar(value="Cache: 0")
        ttk.Label(info_frame, textvariable=self.cache_info,
                 font=('Segoe UI', 9), foreground='#888888').pack(side=tk.RIGHT, padx=(0, 15))

        ttk.Label(info_frame, textvariable=self.total_size,
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.RIGHT)
        
    def create_path_frame(self, parent):
        """Create path selection frame with breadcrumb navigation"""
        path_frame = ttk.Frame(parent)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Breadcrumb frame
        breadcrumb_frame = ttk.Frame(path_frame)
        breadcrumb_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(breadcrumb_frame, text="Location:", 
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        # Breadcrumb container with scrollable canvas
        self.breadcrumb_container = ttk.Frame(breadcrumb_frame)
        self.breadcrumb_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Path input frame
        input_frame = ttk.Frame(path_frame)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="Path:", 
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.path_entry = ttk.Entry(input_frame, textvariable=self.current_path, 
                                   font=('Segoe UI', 10), width=50)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.path_entry.bind('<Return>', lambda e: self.navigate_to_path())
        
        ttk.Button(input_frame, text="Browse...", 
                  command=self.browse_directory, width=12).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(input_frame, text="Go", 
                  command=self.navigate_to_path, width=6).pack(side=tk.RIGHT)
        
        # Initialize breadcrumb
        self.update_breadcrumb()
        
    def create_main_content(self, parent):
        """Create main content area with treeview and details"""
        # Paned window for resizable sections
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left panel - Directory tree
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=3)
        
        # Treeview with scrollbars
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('Size (GB)', 'Size (MB)', 'Files', 'Modified', 'Path')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=20)
        
        # Configure columns
        self.tree.heading('#0', text='Folder Name', anchor='w')
        self.tree.column('#0', width=200, minwidth=150)
        
        self.tree.heading('Size (GB)', text='Size (GB)', anchor='e')
        self.tree.column('Size (GB)', width=100, minwidth=80, anchor='e')
        
        self.tree.heading('Size (MB)', text='Size (MB)', anchor='e')
        self.tree.column('Size (MB)', width=100, minwidth=80, anchor='e')
        
        self.tree.heading('Files', text='Files', anchor='e')
        self.tree.column('Files', width=80, minwidth=60, anchor='e')
        
        self.tree.heading('Modified', text='Modified', anchor='center')
        self.tree.column('Modified', width=120, minwidth=100, anchor='center')
        
        self.tree.heading('Path', text='Full Path', anchor='w')
        self.tree.column('Path', width=300, minwidth=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Right panel - Details and charts
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        self.create_details_panel(right_frame)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
    def create_details_panel(self, parent):
        """Create details panel"""
        # Details label
        ttk.Label(parent, text="Folder Details", 
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Details frame
        details_frame = ttk.Frame(parent)
        details_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Storage details
        self.details_text = tk.Text(details_frame, height=15, width=40, 
                                   bg='#3c3c3c', fg='white', 
                                   font=('Consolas', 9), wrap=tk.WORD)
        
        details_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, 
                                      command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="🔺 Go Up", 
                  command=self.navigate_up, width=15).pack(pady=2, fill=tk.X)
        
        ttk.Button(action_frame, text="📂 Open Folder", 
                  command=self.open_selected_folder, width=15).pack(pady=2, fill=tk.X)
        
        ttk.Button(action_frame, text="➡️ Navigate To", 
                  command=self.navigate_to_selected, width=15).pack(pady=2, fill=tk.X)
        
        ttk.Button(action_frame, text="🗑️ Delete", 
                  command=self.delete_selected, width=15).pack(pady=2, fill=tk.X)
        
        ttk.Button(action_frame, text="ℹ️ Properties", 
                  command=self.show_properties, width=15).pack(pady=2, fill=tk.X)
        
    def create_status_bar(self, parent):
        """Create status bar with detailed progress panel"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Main status bar
        main_status = ttk.Frame(status_frame)
        main_status.pack(fill=tk.X)

        # Progress bar
        self.progress = ttk.Progressbar(main_status, variable=self.scan_progress,
                                       mode='determinate', length=300)
        self.progress.pack(side=tk.LEFT, padx=(0, 10))

        # Status label
        ttk.Label(main_status, textvariable=self.status_text).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Toggle button for detailed progress
        self.detail_toggle_btn = ttk.Button(main_status, text="▼ Show Details",
                                           command=self.toggle_detailed_progress, width=15)
        self.detail_toggle_btn.pack(side=tk.RIGHT, padx=5)

        # Detailed progress panel (collapsible)
        self.detail_panel = ttk.Frame(status_frame, relief='sunken', borderwidth=1)

        detail_content = ttk.Frame(self.detail_panel, padding="5")
        detail_content.pack(fill=tk.BOTH, expand=True)

        # Current folder being scanned
        folder_frame = ttk.Frame(detail_content)
        folder_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(folder_frame, text="Scanning:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        ttk.Label(folder_frame, textvariable=self.current_scan_folder,
                 font=('Segoe UI', 9), foreground='#0078d4').pack(side=tk.LEFT, padx=(5, 0))

        # Statistics
        ttk.Label(detail_content, textvariable=self.scan_stats,
                 font=('Consolas', 8), foreground='#888888').pack(fill=tk.X)

        # Show/hide based on initial state
        if self.show_detailed_progress.get():
            self.detail_panel.pack(fill=tk.X, pady=(5, 0))
            self.detail_toggle_btn.config(text="▲ Hide Details")
        
    def browse_directory(self):
        """Open directory browser"""
        directory = filedialog.askdirectory(initialdir=self.current_path.get())
        if directory:
            self.navigate_to(directory)
    
    def navigate_to(self, path):
        """Navigate to a specific path and update history"""
        if os.path.exists(path):
            # Clean up history if we're not at the end
            if self.history_index < len(self.navigation_history) - 1:
                self.navigation_history = self.navigation_history[:self.history_index + 1]
            
            # Add new path to history (avoid duplicates)
            if path != self.current_path.get():
                self.navigation_history.append(path)
                if len(self.navigation_history) > self.max_history:
                    self.navigation_history.pop(0)
                self.history_index = len(self.navigation_history) - 1
            
            self.current_path.set(path)
            self.update_breadcrumb()
            self.update_navigation_buttons()
            self.start_scan()
        else:
            messagebox.showerror("Error", "Directory does not exist!")
    
    def navigate_to_path(self):
        """Navigate to the path entered in the text field"""
        path = self.current_path.get().strip()
        if path:
            self.navigate_to(path)
    
    def navigate_back(self):
        """Navigate to previous directory in history"""
        if self.history_index > 0:
            self.history_index -= 1
            path = self.navigation_history[self.history_index]
            self.current_path.set(path)
            self.update_breadcrumb()
            self.update_navigation_buttons()
            self.start_scan()
    
    def navigate_forward(self):
        """Navigate to next directory in history"""
        if self.history_index < len(self.navigation_history) - 1:
            self.history_index += 1
            path = self.navigation_history[self.history_index]
            self.current_path.set(path)
            self.update_breadcrumb()
            self.update_navigation_buttons()
            self.start_scan()
    
    def navigate_up(self):
        """Navigate to parent directory"""
        current = Path(self.current_path.get())
        if current.parent != current:  # Not at root
            self.navigate_to(str(current.parent))
    
    def navigate_home(self):
        """Navigate to home/user directory"""
        home_dir = str(Path.home())
        self.navigate_to(home_dir)
    
    def update_breadcrumb(self):
        """Update breadcrumb navigation"""
        # Clear existing breadcrumb
        for widget in self.breadcrumb_container.winfo_children():
            widget.destroy()
        
        current_path = Path(self.current_path.get())
        parts = list(current_path.parts)
        
        # Create breadcrumb buttons
        for i, part in enumerate(parts):
            if i > 0:
                # Add separator
                ttk.Label(self.breadcrumb_container, text=" > ", 
                         foreground='#888888').pack(side=tk.LEFT)
            
            # Create clickable part
            part_path = str(Path(*parts[:i+1]))
            btn = ttk.Button(self.breadcrumb_container, text=part, 
                           command=lambda p=part_path: self.navigate_to(p),
                           style='Breadcrumb.TButton')
            btn.pack(side=tk.LEFT)
        
        # Style breadcrumb buttons
        self.style.configure('Breadcrumb.TButton',
                           background='#2b2b2b',
                           foreground='#0078d4',
                           borderwidth=0,
                           relief='flat',
                           font=('Segoe UI', 9))
        
        self.style.map('Breadcrumb.TButton',
                      background=[('active', '#3c3c3c'),
                                ('pressed', '#1f1f1f')],
                      foreground=[('active', '#4da6ff')])
    
    def update_navigation_buttons(self):
        """Update navigation button states"""
        # Back button
        self.back_btn.configure(state='normal' if self.history_index > 0 else 'disabled')
        
        # Forward button
        self.forward_btn.configure(state='normal' if self.history_index < len(self.navigation_history) - 1 else 'disabled')
        
        # Up button
        current = Path(self.current_path.get())
        self.up_btn.configure(state='normal' if current.parent != current else 'disabled')
            
    def is_cache_valid(self, path):
        """Check if cache exists and is still valid for given path"""
        if path not in self.scan_cache:
            return False

        cache_entry = self.scan_cache[path]
        cache_age = time.time() - cache_entry['timestamp']

        return cache_age < self.cache_ttl

    def load_from_cache(self, path):
        """Load scan results from cache"""
        cache_entry = self.scan_cache[path]
        self.folder_data = cache_entry['folders']

        # Update UI
        self.clear_tree()
        self.populate_tree()

        total_gb = round(cache_entry['total_size'] / (1024**3), 2)
        total_mb = round(cache_entry['total_size'] / (1024**2), 2)

        # Display with appropriate unit
        if total_gb >= 1:
            size_str = f"{total_gb} GB"
        else:
            size_str = f"{total_mb} MB"

        self.total_size.set(f"Total: {size_str}")

        cache_age_minutes = int((time.time() - cache_entry['timestamp']) / 60)
        if cache_age_minutes < 1:
            age_str = "just scanned"
        elif cache_age_minutes < 60:
            age_str = f"cached {cache_age_minutes}m ago"
        else:
            cache_age_hours = cache_age_minutes // 60
            age_str = f"cached {cache_age_hours}h ago"

        # Show subfolder count
        num_folders = len(self.folder_data)
        self.status_text.set(f"⚡ Instant load from cache - {num_folders} subfolders ({age_str})")
        self.scan_stats.set(f"Cache hit! Loaded {num_folders} subfolders instantly | Total: {size_str} | Cached size: {cache_entry['total_size']:,} bytes")
        self.update_cache_info()

    def start_scan(self, force_refresh=False):
        """Start directory scan in separate thread"""
        if self.scanning:
            messagebox.showinfo("Scan in Progress", "A scan is already in progress. Please wait.")
            return

        path = self.current_path.get()
        if not os.path.exists(path):
            messagebox.showerror("Error", "Directory does not exist!")
            return

        # Update navigation buttons
        self.update_navigation_buttons()

        # Check cache first (unless force refresh)
        if not force_refresh and self.cache_enabled and self.is_cache_valid(path):
            self.load_from_cache(path)
            return

        self.scanning = True
        self.scan_thread = threading.Thread(target=self.scan_directory, args=(path,))
        self.scan_thread.daemon = True
        self.scan_thread.start()

    def scan_directory(self, path):
        """Scan directory with parallel processing for better performance"""
        try:
            self.status_text.set("Initializing scan...")
            self.scan_progress.set(0)
            self.cancel_scan = False

            # Enable cancel button
            self.root.after(0, lambda: self.cancel_btn.config(state='normal'))

            # Clear existing data
            self.root.after(0, self.clear_tree)

            # Get subdirectories
            subdirs = [d for d in Path(path).iterdir() if d.is_dir()]
            total_dirs = len(subdirs)

            if total_dirs == 0:
                self.root.after(0, lambda: self.status_text.set("No subdirectories found"))
                self.scanning = False
                self.root.after(0, lambda: self.cancel_btn.config(state='disabled'))
                return

            self.folder_data = []
            total_size_bytes = 0
            completed = 0
            start_time = time.time()

            self.root.after(0, lambda: self.status_text.set(f"Scanning {total_dirs} folders..."))

            # Parallel scanning with ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all folder scan tasks
                future_to_folder = {
                    executor.submit(self.scan_single_folder, subdir, i, total_dirs): subdir
                    for i, subdir in enumerate(subdirs)
                }

                # Process completed scans as they finish
                for future in as_completed(future_to_folder):
                    if self.cancel_scan:
                        # Cancel remaining tasks
                        for f in future_to_folder:
                            f.cancel()
                        self.root.after(0, lambda: self.status_text.set("⏹ Scan cancelled"))
                        break

                    folder_info = future.result()
                    if folder_info:
                        self.folder_data.append(folder_info)
                        total_size_bytes += folder_info['size_bytes']

                    completed += 1

                    # Update progress
                    progress = (completed / total_dirs) * 100
                    self.root.after(0, lambda p=progress: self.scan_progress.set(p))

                    # Calculate stats
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    eta = (total_dirs - completed) / rate if rate > 0 else 0

                    stats = (f"Progress: {completed}/{total_dirs} | "
                            f"Speed: {rate:.1f} folders/sec | "
                            f"ETA: {int(eta)}s | "
                            f"Total: {total_size_bytes/(1024**3):.2f} GB")

                    self.root.after(0, lambda s=stats: self.scan_stats.set(s))
                    self.root.after(0, lambda c=completed, t=total_dirs:
                                   self.status_text.set(f"Scanning... {c}/{t}"))

            if not self.cancel_scan:
                # Sort by size (descending)
                self.folder_data.sort(key=lambda x: x['size_bytes'], reverse=True)

                # Store in cache
                self.scan_cache[path] = {
                    'folders': self.folder_data.copy(),
                    'timestamp': time.time(),
                    'total_size': total_size_bytes,
                    'subdirs_count': len(self.folder_data)
                }

                # Save cache to disk
                self.save_cache_to_disk()

                # Update UI
                total_gb = round(total_size_bytes / (1024**3), 2)
                elapsed_time = time.time() - start_time
                self.root.after(0, lambda: self.total_size.set(f"Total: {total_gb} GB"))
                self.root.after(0, self.populate_tree)
                self.root.after(0, lambda: self.status_text.set(
                    f"✓ Scan complete - {len(self.folder_data)} folders in {elapsed_time:.1f}s"))
                self.root.after(0, self.update_cache_info)
                self.root.after(0, lambda: self.scan_stats.set(
                    f"Completed: {len(self.folder_data)} folders | Total: {total_gb} GB | Time: {elapsed_time:.1f}s"))

        except Exception as e:
            self.root.after(0, lambda e=e: messagebox.showerror("Error", f"Scan failed: {str(e)}"))
        finally:
            self.scanning = False
            self.cancel_scan = False
            self.root.after(0, lambda: self.scan_progress.set(0))
            self.root.after(0, lambda: self.cancel_btn.config(state='disabled'))
            self.root.after(0, lambda: self.current_scan_folder.set(""))
    
    def get_folder_size_and_count(self, folder_path: Path) -> Tuple[int, int]:
        """
        Optimized: Calculate total size and file count in single pass using os.scandir
        Includes hidden files and folders
        Returns: (total_size_bytes, file_count)
        """
        total_size = 0
        file_count = 0

        try:
            # Use os.scandir for better performance than rglob
            # Note: os.scandir includes hidden files/folders by default
            def scan_recursive(path):
                nonlocal total_size, file_count
                try:
                    with os.scandir(path) as entries:
                        for entry in entries:
                            try:
                                # Skip . and .. but include hidden files (starting with .)
                                if entry.name in ('.', '..'):
                                    continue

                                if entry.is_file(follow_symlinks=False):
                                    total_size += entry.stat(follow_symlinks=False).st_size
                                    file_count += 1
                                elif entry.is_dir(follow_symlinks=False):
                                    scan_recursive(entry.path)
                            except (OSError, PermissionError):
                                continue
                except (OSError, PermissionError):
                    pass

            scan_recursive(str(folder_path))
        except (OSError, PermissionError):
            pass

        return total_size, file_count

    def get_folder_info_with_subdirs(self, folder_path: Path) -> Tuple[int, int, List[Dict]]:
        """
        Enhanced: Calculate size, count AND collect info about direct subdirectories
        This enables instant drill-down by pre-caching nested folder info
        Returns: (total_size_bytes, file_count, subdirs_info_list)
        """
        total_size = 0
        file_count = 0
        subdirs_info = []

        try:
            # First, scan direct subdirectories and collect their info
            direct_subdirs = []
            try:
                with os.scandir(str(folder_path)) as entries:
                    for entry in entries:
                        try:
                            if entry.is_dir(follow_symlinks=False):
                                direct_subdirs.append(Path(entry.path))
                        except (OSError, PermissionError):
                            continue
            except (OSError, PermissionError):
                pass

            # Now calculate size for each subdirectory
            for subdir in direct_subdirs:
                try:
                    subdir_size, subdir_files = self.get_folder_size_and_count(subdir)
                    modified_time = subdir.stat().st_mtime

                    subdir_info = {
                        'name': subdir.name,
                        'size_gb': round(subdir_size / (1024**3), 3),
                        'size_mb': round(subdir_size / (1024**2), 1),
                        'files': subdir_files,
                        'modified': time.strftime('%Y-%m-%d %H:%M', time.localtime(modified_time)),
                        'path': str(subdir),
                        'size_bytes': subdir_size
                    }

                    subdirs_info.append(subdir_info)
                    total_size += subdir_size
                    file_count += subdir_files
                except (OSError, PermissionError):
                    continue

            # Also count files in the root of this folder
            try:
                with os.scandir(str(folder_path)) as entries:
                    for entry in entries:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                total_size += entry.stat(follow_symlinks=False).st_size
                                file_count += 1
                        except (OSError, PermissionError):
                            continue
            except (OSError, PermissionError):
                pass

            # Sort subdirs by size
            subdirs_info.sort(key=lambda x: x['size_bytes'], reverse=True)

        except (OSError, PermissionError):
            pass

        return total_size, file_count, subdirs_info

    def scan_single_folder(self, subdir: Path, index: int, total: int) -> Dict:
        """
        Scan a single folder and return its info
        This is designed to be called in parallel
        Also caches nested subdirectories for instant drill-down
        """
        try:
            # Update progress in UI
            folder_name = subdir.name
            self.root.after(0, lambda: self.current_scan_folder.set(f"{folder_name} ({index+1}/{total})"))

            # Calculate size and count, AND collect subdirectory info
            size_bytes, file_count, nested_folders = self.get_folder_info_with_subdirs(subdir)
            modified_time = subdir.stat().st_mtime

            folder_info = {
                'name': subdir.name,
                'size_gb': round(size_bytes / (1024**3), 3),
                'size_mb': round(size_bytes / (1024**2), 1),
                'files': file_count,
                'modified': time.strftime('%Y-%m-%d %H:%M', time.localtime(modified_time)),
                'path': str(subdir),
                'size_bytes': size_bytes
            }

            # Cache the nested subdirectories so drill-down is instant!
            # ALWAYS cache, even if no subfolders (could have files only)
            subdir_path = str(subdir)
            self.scan_cache[subdir_path] = {
                'folders': nested_folders,  # Can be empty list if no subdirs
                'timestamp': time.time(),
                'total_size': size_bytes,  # Total size of THIS folder (all files recursively)
                'subdirs_count': len(nested_folders)
            }

            return folder_info

        except (PermissionError, OSError):
            return None
    
    def clear_tree(self):
        """Clear tree view"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def populate_tree(self):
        """Populate tree with scan results, including virtual files entry if needed"""
        # Calculate total size of all subfolders
        subfolders_total = sum(folder['size_bytes'] for folder in self.folder_data)

        # Get total size from cache if available, otherwise use subfolders total
        path = self.current_path.get()
        total_size = subfolders_total
        if path in self.scan_cache:
            total_size = self.scan_cache[path].get('total_size', subfolders_total)

        # Calculate size of files in root (not in subfolders)
        files_size = total_size - subfolders_total

        # If there are files in root, add virtual entry at the top
        if files_size > 0:
            files_gb = round(files_size / (1024**3), 3)
            files_mb = round(files_size / (1024**2), 1)

            # Insert virtual entry with special styling
            self.tree.insert('', 0, text='📄 (Files in this folder)',
                           values=(files_gb, files_mb, '-', '-', path),
                           tags=('files_entry',))

        # Insert all actual folders
        for folder in self.folder_data:
            self.tree.insert('', tk.END, text=folder['name'],
                           values=(folder['size_gb'], folder['size_mb'],
                                 folder['files'], folder['modified'], folder['path']))

        # Configure tag for virtual files entry (gray, italic)
        self.tree.tag_configure('files_entry', foreground='#888888', font=('Segoe UI', 10, 'italic'))
    
    def refresh_scan(self):
        """Refresh the current scan (force re-scan, ignoring cache)"""
        if not self.scanning:
            path = self.current_path.get()
            # Remove this path from cache to force fresh scan
            if path in self.scan_cache:
                del self.scan_cache[path]
            self.start_scan(force_refresh=True)

    def clear_cache(self):
        """Clear the entire scan cache"""
        cache_count = len(self.scan_cache)
        self.scan_cache.clear()
        messagebox.showinfo("Cache Cleared", f"Cleared cache containing {cache_count} scanned locations.")
        self.status_text.set("Cache cleared")
        self.update_cache_info()

    def update_cache_info(self):
        """Update cache information display"""
        cache_count = len(self.scan_cache)
        if cache_count == 0:
            self.cache_info.set("Cache: Empty")
        else:
            # Calculate total cached data size
            total_cached_gb = sum(entry['total_size'] for entry in self.scan_cache.values()) / (1024**3)
            self.cache_info.set(f"💾 Cache: {cache_count} locations ({total_cached_gb:.1f} GB)")
    
    def on_item_select(self, event):
        """Handle item selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)
            folder_name = values['text']
            folder_values = values['values']
            
            if folder_values:
                path_components = chr(10).join(f"  • {part}" for part in Path(folder_values[4]).parts)
                details = f"""Selected Folder: {folder_name}

Size: {folder_values[0]} GB ({folder_values[1]} MB)
Files: {folder_values[2]:,}
Last Modified: {folder_values[3]}
Full Path: {folder_values[4]}

Storage Breakdown:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Size in bytes: {folder_values[1] * 1024 * 1024:,.0f}
Average file size: {(folder_values[1] * 1024 * 1024) / max(folder_values[2], 1):,.0f} bytes

Path Components:
{path_components}
"""
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(1.0, details)
    
    def on_item_double_click(self, event):
        """Handle double-click to drill down"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)['values']
            if values:
                folder_path = values[4]
                self.navigate_to(folder_path)
    
    def open_in_explorer(self):
        """Open current directory in file explorer"""
        path = self.current_path.get()
        if os.path.exists(path):
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
    
    def navigate_to_selected(self):
        """Navigate to the selected folder"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)['values']
            if values:
                folder_path = values[4]
                self.navigate_to(folder_path)
        else:
            messagebox.showwarning("Warning", "Please select a folder to navigate to.")
    
    def open_selected_folder(self):
        """Open selected folder in explorer"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)['values']
            if values:
                folder_path = values[4]
                if platform.system() == "Windows":
                    os.startfile(folder_path)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", folder_path])
                else:
                    subprocess.run(["xdg-open", folder_path])
    
    def delete_selected(self):
        """Delete selected folder (with confirmation)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a folder to delete.")
            return
            
        item = selection[0]
        values = self.tree.item(item)
        folder_name = values['text']
        folder_path = values['values'][4] if values['values'] else ""
        
        result = messagebox.askyesno("Confirm Deletion", 
                                   f"Are you sure you want to delete '{folder_name}'?\n\n"
                                   f"Path: {folder_path}\n\n"
                                   f"This action cannot be undone!")
        
        if result:
            try:
                import shutil
                shutil.rmtree(folder_path)
                messagebox.showinfo("Success", f"Folder '{folder_name}' has been deleted.")
                self.refresh_scan()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete folder: {str(e)}")
    
    def show_properties(self):
        """Show detailed properties of selected folder"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a folder.")
            return
            
        item = selection[0]
        values = self.tree.item(item)
        if values['values']:
            folder_path = values['values'][4]
            # For Windows, show properties dialog
            if platform.system() == "Windows":
                subprocess.run(f'powershell -command "& {{Get-ItemProperty \'{folder_path}\' | Out-GridView}}"', shell=True)
    
    def export_report(self):
        """Export scan results to CSV"""
        if not self.folder_data:
            messagebox.showwarning("Warning", "No data to export. Please scan a directory first.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Storage Report"
        )

        if filename:
            try:
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Folder Name', 'Size (GB)', 'Size (MB)', 'Files', 'Modified', 'Full Path']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for folder in self.folder_data:
                        writer.writerow({
                            'Folder Name': folder['name'],
                            'Size (GB)': folder['size_gb'],
                            'Size (MB)': folder['size_mb'],
                            'Files': folder['files'],
                            'Modified': folder['modified'],
                            'Full Path': folder['path']
                        })

                messagebox.showinfo("Success", f"Report exported to: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")

    def load_settings(self):
        """Load application settings from disk"""
        settings_file = self.cache_dir / "settings.json"
        try:
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.cache_dir = Path(settings.get('cache_dir', self.cache_dir))
                    self.cache_file = self.cache_dir / "scan_cache.json"
                    self.cache_ttl = settings.get('cache_ttl', 3600)
                    self.cache_enabled = settings.get('cache_enabled', True)
                    self.max_workers = settings.get('max_workers', 4)
        except Exception:
            pass  # Use defaults if loading fails

    def save_settings(self):
        """Save application settings to disk"""
        settings_file = self.cache_dir / "settings.json"
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            settings = {
                'cache_dir': str(self.cache_dir),
                'cache_ttl': self.cache_ttl,
                'cache_enabled': self.cache_enabled,
                'max_workers': self.max_workers
            }
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def load_cache_from_disk(self):
        """Load scan cache from persistent storage"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # Convert back to proper format
                    for path, data in cache_data.items():
                        self.scan_cache[path] = data
                self.update_cache_info()
        except Exception:
            pass  # Start with empty cache if loading fails

    def save_cache_to_disk(self):
        """Save scan cache to persistent storage"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.scan_cache, f, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")

    def cancel_scan_action(self):
        """Cancel the current scan operation"""
        if self.scanning:
            self.cancel_scan = True
            self.status_text.set("Cancelling scan...")

    def toggle_detailed_progress(self):
        """Toggle the detailed progress panel visibility"""
        if self.show_detailed_progress.get():
            # Hide details
            self.detail_panel.pack_forget()
            self.detail_toggle_btn.config(text="▼ Show Details")
            self.show_detailed_progress.set(False)
        else:
            # Show details
            self.detail_panel.pack(fill=tk.X, pady=(5, 0))
            self.detail_toggle_btn.config(text="▲ Hide Details")
            self.show_detailed_progress.set(True)

    def show_settings(self):
        """Show settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Helium Settings")
        dialog.geometry("500x400")
        dialog.configure(bg='#2b2b2b')
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Application Settings",
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))

        # Cache Directory
        cache_frame = ttk.LabelFrame(main_frame, text="Cache Settings", padding="10")
        cache_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(cache_frame, text="Cache Location:").pack(anchor='w')
        cache_path_frame = ttk.Frame(cache_frame)
        cache_path_frame.pack(fill=tk.X, pady=(5, 10))

        cache_path_var = tk.StringVar(value=str(self.cache_dir))
        cache_entry = ttk.Entry(cache_path_frame, textvariable=cache_path_var, width=40)
        cache_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def browse_cache_dir():
            directory = filedialog.askdirectory(initialdir=self.cache_dir)
            if directory:
                cache_path_var.set(directory)

        ttk.Button(cache_path_frame, text="Browse...",
                  command=browse_cache_dir, width=10).pack(side=tk.RIGHT)

        # Cache TTL
        ttl_frame = ttk.Frame(cache_frame)
        ttl_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(ttl_frame, text="Cache Validity (minutes):").pack(side=tk.LEFT, padx=(0, 10))
        ttl_var = tk.IntVar(value=self.cache_ttl // 60)
        ttl_spinbox = ttk.Spinbox(ttl_frame, from_=1, to=1440, textvariable=ttl_var, width=10)
        ttl_spinbox.pack(side=tk.LEFT)

        # Cache enabled
        cache_enabled_var = tk.BooleanVar(value=self.cache_enabled)
        ttk.Checkbutton(cache_frame, text="Enable cache",
                       variable=cache_enabled_var).pack(anchor='w')

        # Performance Settings
        perf_frame = ttk.LabelFrame(main_frame, text="Performance Settings", padding="10")
        perf_frame.pack(fill=tk.X, pady=(0, 15))

        workers_frame = ttk.Frame(perf_frame)
        workers_frame.pack(fill=tk.X)
        ttk.Label(workers_frame, text="Parallel Scan Threads:").pack(side=tk.LEFT, padx=(0, 10))
        workers_var = tk.IntVar(value=self.max_workers)
        workers_spinbox = ttk.Spinbox(workers_frame, from_=1, to=16, textvariable=workers_var, width=10)
        workers_spinbox.pack(side=tk.LEFT)
        ttk.Label(workers_frame, text="(1-16, recommended: 4-8)",
                 font=('Segoe UI', 8), foreground='#888888').pack(side=tk.LEFT, padx=(10, 0))

        # Cache Info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))

        cache_count = len(self.scan_cache)
        cache_size_mb = 0
        if self.cache_file.exists():
            cache_size_mb = self.cache_file.stat().st_size / (1024 * 1024)

        info_text = f"Current cache: {cache_count} locations, {cache_size_mb:.2f} MB on disk"
        ttk.Label(info_frame, text=info_text,
                 font=('Segoe UI', 9), foreground='#888888').pack(anchor='w')

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, pady=(20, 0))

        def save_and_close():
            self.cache_dir = Path(cache_path_var.get())
            self.cache_file = self.cache_dir / "scan_cache.json"
            self.cache_ttl = ttl_var.get() * 60
            self.cache_enabled = cache_enabled_var.get()
            self.max_workers = workers_var.get()
            self.save_settings()
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
            dialog.destroy()

        ttk.Button(button_frame, text="Save", command=save_and_close, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=5)

def main():
    root = tk.Tk()
    app = StorageManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
