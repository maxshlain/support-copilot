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
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.parent
    screenshots_dir = script_dir / "screenshots"
    
    # Create screenshots directory if it doesn't exist
    screenshots_dir.mkdir(exist_ok=True)
    
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
    
    try:
        while True:
            # Check if we've reached the maximum count
            if args.max_count and screenshot_count >= args.max_count:
                print(f"\nReached maximum count of {args.max_count} screenshots. Stopping.")
                break
                
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
            
            screenshot_count += 1
            print(f"Screenshot {screenshot_count} saved: {filename}")
            print(f"Also saved as: latest.png")
            
            # Clean up old screenshots to keep only the specified number
            cleanup_old_screenshots(screenshots_dir, max_files=args.keep)
            
            # Check if we've reached the maximum count after taking the screenshot
            if args.max_count and screenshot_count >= args.max_count:
                print(f"\nReached maximum count of {args.max_count} screenshots. Stopping.")
                break
            
            # Wait for the specified interval before next screenshot
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\nScreenshot capture stopped.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()