# support-copilot

How many times you have been stuck on a technical issue, unable to find a solution online? This project aims to provide a support copilot that can analyze your current state and propose a solution.

How it works:
1. You run an app that captures your screen once every 5 seconds.
2. You ask copilot for help.
3. Copilot analyzes the latest screenshots in the screenshots folder and provides a solution.
PROFIT!

## Quick Usage

**For immediate help:** Simply check the `latest.png` file in the screenshots folder - it always contains the most recent screenshot and is usually sufficient for troubleshooting.

The app also maintains an archive of the last 10 timestamped screenshots for reference if needed.

## Important Notes

- You do not stream your screen - copilot will only analyze screenshots after your request.
- Only the main screen is captured, so if you have multiple monitors, make sure the one with the issue is the main one.
- Screenshots are saved every 5 seconds and only the last 10 are kept (plus the latest.png file).