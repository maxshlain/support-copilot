import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
from datetime import datetime
import os
from PIL import Image, ImageTk
import mss
import mss.tools

class ScreenshotTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Area Screenshot Tool")
        self.root.geometry("400x300")
        
        self.screenshot_thread = None
        self.stop_screenshots = False
        self.selected_area = None
        self.monitor_info = None
        
        # Get monitor information
        with mss.mss() as sct:
            self.monitors = sct.monitors
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Monitor selection
        ttk.Label(main_frame, text="Select Monitor:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.monitor_var = tk.StringVar()
        monitor_combo = ttk.Combobox(main_frame, textvariable=self.monitor_var, state="readonly")
        
        # Populate monitor options
        monitor_options = ["All Monitors (Virtual)"]
        for i, monitor in enumerate(self.monitors[1:], 1):  # Skip the first "All Monitors" entry
            monitor_options.append(f"Monitor {i} ({monitor['width']}x{monitor['height']})")
        
        monitor_combo['values'] = monitor_options
        monitor_combo.set(monitor_options[0])
        monitor_combo.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Area selection
        ttk.Label(main_frame, text="Selected Area:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.area_label = ttk.Label(main_frame, text="No area selected", foreground="gray")
        self.area_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Buttons
        select_btn = ttk.Button(main_frame, text="Select Area", command=self.select_area)
        select_btn.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.start_btn = ttk.Button(main_frame, text="Start Screenshots", command=self.start_screenshots, state="disabled")
        self.start_btn.grid(row=4, column=1, sticky=(tk.W, tk.E))
        
        self.stop_btn = ttk.Button(main_frame, text="Stop Screenshots", command=self.stop_screenshots_func, state="disabled")
        self.stop_btn.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Ready to select area")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        # Screenshot count
        self.count_label = ttk.Label(main_frame, text="Screenshots taken: 0")
        self.count_label.grid(row=7, column=0, columnspan=2, pady=(5, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        self.screenshot_count = 0
        
    def select_area(self):
        """Create a transparent overlay for area selection"""
        self.root.withdraw()  # Hide main window
        
        # Get the selected monitor
        monitor_index = self.monitor_var.get()
        if monitor_index.startswith("All Monitors"):
            monitor = self.monitors[0]  # Virtual screen (all monitors)
        else:
            # Extract monitor number from selection
            monitor_num = int(monitor_index.split()[1]) 
            monitor = self.monitors[monitor_num]
        
        # Create selection window
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes('-topmost', True)
        self.selection_window.configure(bg='black')
        self.selection_window.overrideredirect(True)  # Remove window decorations
        
        # Position window on the selected monitor
        if monitor_index.startswith("All Monitors"):
            # Use virtual screen dimensions
            geometry = f"{monitor['width']}x{monitor['height']}+{monitor['left']}+{monitor['top']}"
        else:
            geometry = f"{monitor['width']}x{monitor['height']}+{monitor['left']}+{monitor['top']}"
        
        self.selection_window.geometry(geometry)
        self.selection_window.attributes('-alpha', 0.3)  # Set alpha after geometry
        
        self.selection_window.bind('<Button-1>', self.start_selection)
        self.selection_window.bind('<B1-Motion>', self.update_selection)
        self.selection_window.bind('<ButtonRelease-1>', self.end_selection)
        self.selection_window.bind('<Escape>', self.cancel_selection)
        self.selection_window.focus_set()  # Ensure window gets focus
        
        # Create canvas for drawing rectangle
        self.canvas = tk.Canvas(self.selection_window, highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Update the window to ensure proper sizing before creating text
        self.selection_window.update_idletasks()
        
        # Instructions - use actual window width
        instruction_text = "Click and drag to select area. Press ESC to cancel."
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:  # Fallback if width not available yet
            canvas_width = monitor['width']
        
        self.canvas.create_text(
            canvas_width // 2, 50, 
            text=instruction_text, 
            fill='white', 
            font=('Arial', 14)
        )
        
        self.start_x = self.start_y = 0
        self.rect_id = None
        
    def start_selection(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
    
    def update_selection(self, event):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=2
        )
    
    def end_selection(self, event):
        # Calculate absolute coordinates
        monitor_index = self.monitor_var.get()
        if monitor_index.startswith("All Monitors"):
            offset_x = offset_y = 0
        else:
            monitor_num = int(monitor_index.split()[1])
            monitor = self.monitors[monitor_num]
            offset_x = monitor['left']
            offset_y = monitor['top']
        
        # Store selected area (ensure positive width/height)
        x1 = min(self.start_x, event.x) + offset_x
        y1 = min(self.start_y, event.y) + offset_y
        x2 = max(self.start_x, event.x) + offset_x
        y2 = max(self.start_y, event.y) + offset_y
        
        width = x2 - x1
        height = y2 - y1
        
        if width > 10 and height > 10:  # Minimum size check
            self.selected_area = {'left': x1, 'top': y1, 'width': width, 'height': height}
            self.area_label.config(text=f"Area: {width}x{height} at ({x1}, {y1})")
            self.start_btn.config(state="normal")
            self.status_label.config(text="Area selected! Ready to start screenshots.")
        else:
            messagebox.showwarning("Invalid Selection", "Selected area is too small. Please select a larger area.")
        
        self.close_selection_window()
    
    def cancel_selection(self, event):
        self.close_selection_window()
    
    def close_selection_window(self):
        if hasattr(self, 'selection_window') and self.selection_window:
            self.selection_window.destroy()
        self.root.deiconify()  # Show main window again
        self.root.lift()  # Bring window to front
        self.root.focus_set()  # Give focus back to main window
    
    def start_screenshots(self):
        if not self.selected_area:
            messagebox.showerror("Error", "Please select an area first.")
            return
        
        # Create screenshots directory in the root repository folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(script_dir)  # Go up one level from src2 to repo root
        self.screenshots_dir = os.path.join(repo_root, "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        self.stop_screenshots = False
        self.screenshot_count = 0
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Taking screenshots every 5 seconds...")
        
        # Start screenshot thread
        self.screenshot_thread = threading.Thread(target=self.screenshot_loop, daemon=True)
        self.screenshot_thread.start()
    
    def screenshot_loop(self):
        with mss.mss() as sct:
            while not self.stop_screenshots:
                try:
                    # Take screenshot of selected area
                    screenshot = sct.grab(self.selected_area)
                    
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(self.screenshots_dir, f"screenshot_{timestamp}_{self.screenshot_count + 1:04d}.png")
                    
                    # Save screenshot
                    mss.tools.to_png(screenshot.rgb, screenshot.size, output=filename)
                    
                    self.screenshot_count += 1
                    
                    # Update UI in main thread
                    self.root.after(0, self.update_ui)
                    
                    # Wait 5 seconds
                    for _ in range(50):  # Check stop flag every 0.1 seconds
                        if self.stop_screenshots:
                            break
                        time.sleep(0.1)
                        
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Screenshot Error", f"Error taking screenshot: {str(e)}"))
                    break
    
    def update_ui(self):
        self.count_label.config(text=f"Screenshots taken: {self.screenshot_count}")
    
    def stop_screenshots_func(self):
        self.stop_screenshots = True
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        folder_path = getattr(self, 'screenshots_dir', 'screenshots')
        self.status_label.config(text=f"Stopped. {self.screenshot_count} screenshots saved in '{folder_path}' folder.")
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        if self.screenshot_thread and self.screenshot_thread.is_alive():
            self.stop_screenshots = True
            self.screenshot_thread.join(timeout=1)
        self.root.destroy()

if __name__ == "__main__":
    # Check if required packages are available
    try:
        import mss
        import mss.tools
        from PIL import Image, ImageTk
    except ImportError as e:
        print("Required packages not found. Please install them using:")
        print("pip install mss pillow")
        exit(1)
    
    app = ScreenshotTool()
    app.run()