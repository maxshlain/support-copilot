#!/usr/bin/env python3
"""
Area Screenshot Tool

This GUI application provides visual area selection for taking periodic screenshots.
Features include:
- Visual area selection with mouse drag
- Multiple monitor support
- Configurable screenshot interval
- Maximum screenshot count limit
- Automatic cleanup of old screenshots
- Latest.png file for most recent screenshot
- Error handling with consecutive error tracking
- Command line argument support

The app combines the visual selection capabilities with all the features
from the command-line main.py tool.
"""

import argparse
import os
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

import mss
import mss.tools
from PIL import Image, ImageTk


class ScreenshotTool:
    def __init__(self, args=None):
        self.root = tk.Tk()
        self.root.title("Area Screenshot Tool")
        self.root.geometry("500x400")

        # Store command line arguments
        self.args = args or self.get_default_args()

        self.screenshot_thread = None
        self.stop_screenshots = False
        self.selected_area = None
        self.monitor_info = None
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5

        # Get monitor information
        with mss.mss() as sct:
            self.monitors = sct.monitors

        self.setup_ui()

    def get_default_args(self):
        """Return default arguments when running in GUI mode."""

        class DefaultArgs:
            def __init__(self):
                self.max_count = None
                self.interval = 5.0
                self.keep = 100

        return DefaultArgs()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # Interval setting
        ttk.Label(config_frame, text="Interval (seconds):").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.interval_var = tk.DoubleVar(value=self.args.interval)
        interval_spinbox = ttk.Spinbox(
            config_frame,
            from_=0.1,
            to=3600,
            textvariable=self.interval_var,
            width=10,
            increment=0.5,
        )
        interval_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))

        # Max count setting
        ttk.Label(config_frame, text="Max screenshots:").grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.max_count_var = tk.StringVar(
            value=str(self.args.max_count) if self.args.max_count else "infinite"
        )
        max_count_entry = ttk.Entry(
            config_frame, textvariable=self.max_count_var, width=10
        )
        max_count_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))

        # Keep count setting
        ttk.Label(config_frame, text="Keep screenshots:").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.keep_var = tk.IntVar(value=self.args.keep)
        keep_spinbox = ttk.Spinbox(
            config_frame, from_=1, to=10000, textvariable=self.keep_var, width=10
        )
        keep_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))

        # Monitor selection
        monitor_frame = ttk.LabelFrame(
            main_frame, text="Monitor Selection", padding="10"
        )
        monitor_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        ttk.Label(monitor_frame, text="Select Monitor:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        self.monitor_var = tk.StringVar()
        monitor_combo = ttk.Combobox(
            monitor_frame, textvariable=self.monitor_var, state="readonly"
        )

        # Populate monitor options
        monitor_options = ["All Monitors (Virtual)"]
        for i, monitor in enumerate(
            self.monitors[1:], 1
        ):  # Skip the first "All Monitors" entry
            monitor_options.append(
                f"Monitor {i} ({monitor['width']}x{monitor['height']})"
            )

        monitor_combo["values"] = monitor_options
        monitor_combo.set(monitor_options[0])
        monitor_combo.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # Area selection
        area_frame = ttk.LabelFrame(main_frame, text="Area Selection", padding="10")
        area_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        ttk.Label(area_frame, text="Selected Area:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.area_label = ttk.Label(
            area_frame, text="No area selected", foreground="gray"
        )
        self.area_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Buttons
        select_btn = ttk.Button(
            area_frame, text="Select Area", command=self.select_area
        )
        select_btn.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        self.start_btn = ttk.Button(
            area_frame,
            text="Start Screenshots",
            command=self.start_screenshots,
            state="disabled",
        )
        self.start_btn.grid(row=2, column=1, sticky=(tk.W, tk.E))

        self.stop_btn = ttk.Button(
            main_frame,
            text="Stop Screenshots",
            command=self.stop_screenshots_func,
            state="disabled",
        )
        self.stop_btn.grid(
            row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(
            row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        # Status
        self.status_label = ttk.Label(status_frame, text="Ready to select area")
        self.status_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))

        # Screenshot count
        self.count_label = ttk.Label(status_frame, text="Screenshots taken: 0")
        self.count_label.grid(row=1, column=0, columnspan=2, pady=(0, 5))

        # Error count
        self.error_label = ttk.Label(status_frame, text="", foreground="red")
        self.error_label.grid(row=2, column=0, columnspan=2)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(1, weight=1)
        monitor_frame.columnconfigure(1, weight=1)
        area_frame.columnconfigure(0, weight=1)
        area_frame.columnconfigure(1, weight=1)
        status_frame.columnconfigure(0, weight=1)

        self.screenshot_count = 0

    def cleanup_old_screenshots(self, screenshots_dir, max_files):
        """Remove old screenshots, keeping only the most recent max_files."""
        try:
            screenshot_files = list(Path(screenshots_dir).glob("screenshot_*.png"))

            if len(screenshot_files) > max_files:
                # Sort by modification time (newest first)
                screenshot_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

                # Remove files beyond the limit
                files_to_remove = screenshot_files[max_files:]
                for file_path in files_to_remove:
                    try:
                        file_path.unlink()
                        print(f"Removed old screenshot: {file_path.name}")
                    except OSError as e:
                        print(f"Warning: Error removing {file_path.name}: {e}")
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")

    def validate_settings(self):
        """Validate user input settings."""
        try:
            interval = self.interval_var.get()
            if interval <= 0:
                messagebox.showerror("Error", "Interval must be positive")
                return False

            max_count_str = self.max_count_var.get().strip().lower()
            max_count = None
            if max_count_str not in ["infinite", ""]:
                try:
                    max_count = int(max_count_str)
                    if max_count <= 0:
                        messagebox.showerror("Error", "Max count must be positive")
                        return False
                except ValueError:
                    messagebox.showerror(
                        "Error", "Max count must be a positive number or 'infinite'"
                    )
                    return False

            keep = self.keep_var.get()
            if keep <= 0:
                messagebox.showerror("Error", "Keep count must be positive")
                return False

            return True, interval, max_count, keep
        except Exception as e:
            messagebox.showerror("Error", f"Invalid settings: {e}")
            return False

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
        self.selection_window.attributes("-topmost", True)
        self.selection_window.configure(bg="black")
        self.selection_window.overrideredirect(True)  # Remove window decorations

        # Position window on the selected monitor
        if monitor_index.startswith("All Monitors"):
            # Use virtual screen dimensions
            geometry = f"{monitor['width']}x{monitor['height']}+{monitor['left']}+{monitor['top']}"
        else:
            geometry = f"{monitor['width']}x{monitor['height']}+{monitor['left']}+{monitor['top']}"

        self.selection_window.geometry(geometry)
        self.selection_window.attributes("-alpha", 0.3)  # Set alpha after geometry

        self.selection_window.bind("<Button-1>", self.start_selection)
        self.selection_window.bind("<B1-Motion>", self.update_selection)
        self.selection_window.bind("<ButtonRelease-1>", self.end_selection)
        self.selection_window.bind("<Escape>", self.cancel_selection)
        self.selection_window.focus_set()  # Ensure window gets focus

        # Create canvas for drawing rectangle
        self.canvas = tk.Canvas(self.selection_window, highlightthickness=0, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Update the window to ensure proper sizing before creating text
        self.selection_window.update_idletasks()

        # Instructions - use actual window width
        instruction_text = "Click and drag to select area. Press ESC to cancel."
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:  # Fallback if width not available yet
            canvas_width = monitor["width"]

        self.canvas.create_text(
            canvas_width // 2,
            50,
            text=instruction_text,
            fill="white",
            font=("Arial", 14),
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
            self.start_x, self.start_y, event.x, event.y, outline="red", width=2
        )

    def end_selection(self, event):
        # Calculate absolute coordinates
        monitor_index = self.monitor_var.get()
        if monitor_index.startswith("All Monitors"):
            offset_x = offset_y = 0
        else:
            monitor_num = int(monitor_index.split()[1])
            monitor = self.monitors[monitor_num]
            offset_x = monitor["left"]
            offset_y = monitor["top"]

        # Store selected area (ensure positive width/height)
        x1 = min(self.start_x, event.x) + offset_x
        y1 = min(self.start_y, event.y) + offset_y
        x2 = max(self.start_x, event.x) + offset_x
        y2 = max(self.start_y, event.y) + offset_y

        width = x2 - x1
        height = y2 - y1

        if width > 10 and height > 10:  # Minimum size check
            self.selected_area = {
                "left": x1,
                "top": y1,
                "width": width,
                "height": height,
            }
            self.area_label.config(text=f"Area: {width}x{height} at ({x1}, {y1})")
            self.start_btn.config(state="normal")
            self.status_label.config(text="Area selected! Ready to start screenshots.")
        else:
            messagebox.showwarning(
                "Invalid Selection",
                "Selected area is too small. Please select a larger area.",
            )

        self.close_selection_window()

    def cancel_selection(self, event):
        self.close_selection_window()

    def close_selection_window(self):
        if hasattr(self, "selection_window") and self.selection_window:
            self.selection_window.destroy()
        self.root.deiconify()  # Show main window again
        self.root.lift()  # Bring window to front
        self.root.focus_set()  # Give focus back to main window

    def start_screenshots(self):
        if not self.selected_area:
            messagebox.showerror("Error", "Please select an area first.")
            return

        # Validate settings
        validation = self.validate_settings()
        if not validation:
            return

        _, interval, max_count, keep = validation

        # Create screenshots directory in the root repository folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(
            script_dir
        )  # Go up one level from src2 to repo root
        self.screenshots_dir = os.path.join(repo_root, "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)

        # Store settings for the screenshot loop
        self.current_interval = interval
        self.current_max_count = max_count
        self.current_keep = keep

        self.stop_screenshots = False
        self.screenshot_count = 0
        self.consecutive_errors = 0
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        status_text = f"Taking screenshots every {interval} seconds..."
        if max_count:
            status_text += f" (max: {max_count})"
        self.status_label.config(text=status_text)
        self.error_label.config(text="")

        print("Starting screenshot capture...")
        print(f"Screenshots will be saved to: {self.screenshots_dir}")
        print(f"Screenshots to keep: {keep}")
        print(f"Interval: {interval} seconds")
        if max_count:
            print(f"Maximum screenshots: {max_count}")
        else:
            print("Maximum screenshots: infinite")
        print(
            "💡 Tip: Check 'latest.png' for the most recent screenshot - it's usually all you need!"
        )

        # Start screenshot thread
        self.screenshot_thread = threading.Thread(
            target=self.screenshot_loop, daemon=True
        )
        self.screenshot_thread.start()

    def screenshot_loop(self):
        with mss.mss() as sct:
            while not self.stop_screenshots:
                # Check if we've reached the maximum count
                if (
                    self.current_max_count
                    and self.screenshot_count >= self.current_max_count
                ):
                    self.root.after(
                        0,
                        lambda: self.stop_screenshots_func(
                            reason="Maximum screenshots reached"
                        ),
                    )
                    break

                try:
                    # Take screenshot of selected area
                    screenshot = sct.grab(self.selected_area)

                    # Generate filename with timestamp (same format as main.py)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_{timestamp}.png"
                    filepath = os.path.join(self.screenshots_dir, filename)
                    latest_filepath = os.path.join(self.screenshots_dir, "latest.png")

                    # Save screenshot to both timestamp file and latest.png
                    mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
                    mss.tools.to_png(
                        screenshot.rgb, screenshot.size, output=latest_filepath
                    )

                    self.screenshot_count += 1
                    self.consecutive_errors = 0

                    print(f"Screenshot {self.screenshot_count} saved: {filename}")

                    # Clean up old screenshots
                    self.cleanup_old_screenshots(
                        self.screenshots_dir, max_files=self.current_keep
                    )

                    # Update UI in main thread
                    self.root.after(0, self.update_ui)

                except Exception as e:
                    self.consecutive_errors += 1
                    error_msg = f"Error taking screenshot: {str(e)}"
                    print(error_msg)

                    if self.consecutive_errors >= self.max_consecutive_errors:
                        self.root.after(
                            0,
                            lambda: self.stop_screenshots_func(
                                reason=f"Too many consecutive errors ({self.consecutive_errors}). Stopping."
                            ),
                        )
                        break

                    # Update error display in main thread
                    self.root.after(
                        0,
                        lambda: self.error_label.config(
                            text=f"Errors: {self.consecutive_errors}/{self.max_consecutive_errors}"
                        ),
                    )

                # Wait for the specified interval, checking stop flag regularly
                interval_steps = int(
                    self.current_interval * 10
                )  # Check every 0.1 seconds
                for _ in range(interval_steps):
                    if self.stop_screenshots:
                        break
                    time.sleep(0.1)

    def update_ui(self):
        self.count_label.config(text=f"Screenshots taken: {self.screenshot_count}")
        if self.consecutive_errors > 0:
            self.error_label.config(
                text=f"Errors: {self.consecutive_errors}/{self.max_consecutive_errors}"
            )
        else:
            self.error_label.config(text="")

    def stop_screenshots_func(self, reason=None):
        self.stop_screenshots = True
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        folder_path = getattr(self, "screenshots_dir", "screenshots")

        if reason:
            status_text = f"{reason} {self.screenshot_count} screenshots saved in '{folder_path}' folder."
        else:
            status_text = f"Stopped. {self.screenshot_count} screenshots saved in '{folder_path}' folder."

        self.status_label.config(text=status_text)
        self.error_label.config(text="")

        print(
            f"\nScreenshot capture stopped. Total screenshots taken: {self.screenshot_count}"
        )

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        if self.screenshot_thread and self.screenshot_thread.is_alive():
            self.stop_screenshots = True
            self.screenshot_thread.join(timeout=1)
        self.root.destroy()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Area Screenshot Tool - Visual area selection with periodic screenshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                            # Run with GUI (default settings)
  python app.py --max-count 20             # GUI with max 20 screenshots
  python app.py --interval 10              # GUI with 10 second intervals
  python app.py --keep 5                   # GUI keeping only 5 screenshots
  python app.py --max-count 50 --interval 3 --keep 15  # GUI with custom settings
        """,
    )

    parser.add_argument(
        "--max-count",
        "-n",
        type=int,
        default=None,
        help="Maximum number of screenshots to take (default: infinite)",
    )

    parser.add_argument(
        "--interval",
        "-i",
        type=float,
        default=5.0,
        help="Interval between screenshots in seconds (default: 5)",
    )

    parser.add_argument(
        "--keep",
        "-k",
        type=int,
        default=100,
        help="Number of screenshots to keep (default: 100)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()

    # Validate arguments
    if args.interval <= 0:
        print("Error: Interval must be positive")
        sys.exit(1)

    if args.keep <= 0:
        print("Error: Keep count must be positive")
        sys.exit(1)

    if args.max_count is not None and args.max_count <= 0:
        print("Error: Max count must be positive")
        sys.exit(1)

    # Check if required packages are available
    try:
        import mss
        import mss.tools
        from PIL import Image, ImageTk
    except ImportError:
        print("Required packages not found. Please install them using:")
        print("pip install mss pillow")
        print("Or if using uv: uv add mss pillow")
        sys.exit(1)

    app = ScreenshotTool(args)
    app.run()
