#!/usr/bin/env python3
"""
Screenshot App

This app runs in infinite loop and takes a screenshot of the screen 
once every 5 seconds. Every screenshot file has a name with the 
current timestamp.
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

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.parent
    screenshots_dir = script_dir / "screenshots"
    
    # Create screenshots directory if it doesn't exist
    screenshots_dir.mkdir(exist_ok=True)
    
    print(f"Starting screenshot capture...")
    print(f"Screenshots will be saved to: {screenshots_dir}")
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
            
            print(f"Screenshot saved: {filename}")
            
            # Wait 5 seconds before next screenshot
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nScreenshot capture stopped.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()