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
import argparse
import sys
from pathlib import Path

try:
    import pyautogui
except ImportError:
    print("ERROR: pyautogui is required but not installed.")
    print("Please install it with: pip install pyautogui")
    print("Or if using uv: uv add pyautogui")
    sys.exit(1)

def cleanup_old_screenshots(screenshots_dir, max_files=10):
    """Remove old screenshots, keeping only the most recent max_files."""
    try:
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
                    print(f"Warning: Error removing {file_path.name}: {e}")
    except Exception as e:
        print(f"Warning: Error during cleanup: {e}")

def take_screenshot(filepath, latest_filepath):
    """Take a screenshot and save it to both timestamp and latest files."""
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        screenshot.save(latest_filepath)
        return True
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Screenshot App - Takes periodic screenshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Run with default settings (infinite screenshots, 5s interval)
  python main.py --max-count 20            # Take only 20 screenshots
  python main.py --interval 10             # Take screenshots every 10 seconds
  python main.py --keep 5                  # Keep only 5 screenshots
  python main.py --max-count 50 --interval 3 --keep 15  # Custom settings
        """
    )
    
    parser.add_argument(
        "--max-count", "-n",
        type=int,
        default=None,
        help="Maximum number of screenshots to take (default: infinite)"
    )
    
    parser.add_argument(
        "--interval", "-i",
        type=float,
        default=5.0,
        help="Interval between screenshots in seconds (default: 5)"
    )
    
    parser.add_argument(
        "--keep", "-k",
        type=int,
        default=10,
        help="Number of screenshots to keep (default: 10)"
    )
    
    return parser.parse_args()

def main():
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
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.parent
    screenshots_dir = script_dir / "screenshots"
    
    # Create screenshots directory if it doesn't exist
    try:
        screenshots_dir.mkdir(exist_ok=True)
    except Exception as e:
        print(f"Error creating screenshots directory: {e}")
        sys.exit(1)
    
    print(f"Starting screenshot capture...")
    print(f"Screenshots will be saved to: {screenshots_dir}")
    print(f"Screenshots to keep: {args.keep}")
    print(f"Interval: {args.interval} seconds")
    if args.max_count:
        print(f"Maximum screenshots: {args.max_count}")
    else:
        print("Maximum screenshots: infinite")
    print("💡 Tip: Check 'latest.png' for the most recent screenshot - it's usually all you need!")
    print("Press Ctrl+C to stop")
    
    screenshot_count = 0
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    try:
        while args.max_count is None or screenshot_count < args.max_count:
            # Generate timestamp for filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = screenshots_dir / filename
            latest_filepath = screenshots_dir / "latest.png"
            
            # Take screenshot
            if take_screenshot(filepath, latest_filepath):
                screenshot_count += 1
                consecutive_errors = 0
                print(f"Screenshot {screenshot_count} saved: {filename}")
                print(f"Also saved as: latest.png")
                
                # Clean up old screenshots to keep only the specified number
                cleanup_old_screenshots(screenshots_dir, max_files=args.keep)
            else:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    print(f"Too many consecutive errors ({consecutive_errors}). Stopping.")
                    break
                print(f"Retrying in {args.interval} seconds...")
            
            # Wait for the specified interval before next screenshot
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print(f"\nScreenshot capture stopped. Total screenshots taken: {screenshot_count}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()