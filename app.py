import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import time
from pathlib import Path
import subprocess
import platform

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
        
        # Navigation history
        self.navigation_history = ["D:\\Laboratory"]
        self.history_index = 0
        self.max_history = 50
        
        # Data storage
        self.folder_data = []
        
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
        
        ttk.Button(action_frame, text="🔄 Refresh", 
                  command=self.refresh_scan, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(action_frame, text="📁 Explorer", 
                  command=self.open_in_explorer, width=10).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(action_frame, text="📊 Export", 
                  command=self.export_report, width=8).pack(side=tk.LEFT, padx=2)
        
        # Right side info
        info_frame = ttk.Frame(toolbar)
        info_frame.pack(side=tk.RIGHT)
        
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
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, variable=self.scan_progress, 
                                       mode='determinate', length=300)
        self.progress.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        ttk.Label(status_frame, textvariable=self.status_text).pack(side=tk.LEFT)
        
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
            
    def start_scan(self):
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
            
        self.scanning = True
        self.scan_thread = threading.Thread(target=self.scan_directory, args=(path,))
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
    def scan_directory(self, path):
        """Scan directory and populate tree"""
        try:
            self.status_text.set("Scanning directory...")
            self.scan_progress.set(0)
            
            # Clear existing data
            self.root.after(0, self.clear_tree)
            
            # Get subdirectories
            subdirs = [d for d in Path(path).iterdir() if d.is_dir()]
            total_dirs = len(subdirs)
            
            if total_dirs == 0:
                self.root.after(0, lambda: self.status_text.set("No subdirectories found"))
                self.scanning = False
                return
            
            self.folder_data = []
            total_size_bytes = 0
            
            for i, subdir in enumerate(subdirs):
                if not self.scanning:  # Check if scan was cancelled
                    break
                    
                try:
                    # Calculate folder size
                    size_bytes = self.get_folder_size(subdir)
                    file_count = self.get_file_count(subdir)
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
                    
                    self.folder_data.append(folder_info)
                    total_size_bytes += size_bytes
                    
                    # Update progress
                    progress = ((i + 1) / total_dirs) * 100
                    self.root.after(0, lambda p=progress: self.scan_progress.set(p))
                    self.root.after(0, lambda: self.status_text.set(f"Scanning... {i+1}/{total_dirs}"))
                    
                except (PermissionError, OSError) as e:
                    # Skip inaccessible folders
                    continue
            
            # Sort by size (descending)
            self.folder_data.sort(key=lambda x: x['size_bytes'], reverse=True)
            
            # Update UI
            total_gb = round(total_size_bytes / (1024**3), 2)
            self.root.after(0, lambda: self.total_size.set(f"Total: {total_gb} GB"))
            self.root.after(0, self.populate_tree)
            self.root.after(0, lambda: self.status_text.set(f"Scan complete - {len(self.folder_data)} folders found"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {str(e)}"))
        finally:
            self.scanning = False
            self.root.after(0, lambda: self.scan_progress.set(0))
    
    def get_folder_size(self, folder_path):
        """Calculate total size of folder"""
        total_size = 0
        try:
            for entry in folder_path.rglob('*'):
                if entry.is_file():
                    try:
                        total_size += entry.stat().st_size
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
        return total_size
    
    def get_file_count(self, folder_path):
        """Count files in folder"""
        count = 0
        try:
            for entry in folder_path.rglob('*'):
                if entry.is_file():
                    count += 1
        except (OSError, PermissionError):
            pass
        return count
    
    def clear_tree(self):
        """Clear tree view"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def populate_tree(self):
        """Populate tree with scan results"""
        for folder in self.folder_data:
            self.tree.insert('', tk.END, text=folder['name'],
                           values=(folder['size_gb'], folder['size_mb'], 
                                 folder['files'], folder['modified'], folder['path']))
    
    def refresh_scan(self):
        """Refresh the current scan"""
        if not self.scanning:
            self.start_scan()
    
    def on_item_select(self, event):
        """Handle item selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)
            folder_name = values['text']
            folder_values = values['values']
            
            if folder_values:
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
{chr(10).join(f"  • {part}" for part in Path(folder_values[4]).parts)}
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

def main():
    root = tk.Tk()
    app = StorageManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
