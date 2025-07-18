#!/usr/bin/env python3
"""
Screenshot App

This app runs in infinite loop and takes a screenshot of the screen 
once every 5 seconds. Every screenshot file has a name with the 
current timestamp. Only keeps the last 10 screenshots.
"""

import os
import time
import datetime
from pathlib import Path
try:
    import pyautogui
except ImportError:
    print("pyautogui not found. Installing...")
    os.system("uv add pyautogui")
    import pyautogui

def cleanup_old_screenshots(screenshots_dir, max_files=10):
    """Remove old screenshots, keeping only the most recent max_files."""
    screenshot_files = list(screenshots_dir.glob("screenshot_*.png"))
    
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
                print(f"Error removing {file_path.name}: {e}")

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.parent
    screenshots_dir = script_dir / "screenshots"
    
    # Create screenshots directory if it doesn't exist
    screenshots_dir.mkdir(exist_ok=True)
    
    print(f"Starting screenshot capture...")
    print(f"Screenshots will be saved to: {screenshots_dir}")
    print("Only the last 10 screenshots will be kept")
    print("💡 Tip: Check 'latest.png' for the most recent screenshot - it's usually all you need!")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Generate timestamp for filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = screenshots_dir / filename
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            # Also save as latest.png
            latest_filepath = screenshots_dir / "latest.png"
            screenshot.save(latest_filepath)
            
            print(f"Screenshot saved: {filename}")
            print(f"Also saved as: latest.png")
            
            # Clean up old screenshots to keep only the last 10
            cleanup_old_screenshots(screenshots_dir, max_files=10)
            
            # Wait 5 seconds before next screenshot
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nScreenshot capture stopped.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()