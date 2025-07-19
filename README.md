# Support Copilot: AI-Powered Visual Support Assistant

## The Problem

Every developer and support engineer knows this scenario: you're on a support call, the customer shares their screen showing an issue, and you need help figuring it out. Traditionally, this meant:
- Taking screenshots manually
- Pasting them into chat tools
- Asking colleagues or AI for help
- Repeating the process multiple times

This screenshot-paste-ask-repeat cycle is inefficient and breaks your flow during critical support situations.

## The Solution

Support Copilot streamlines this workflow by:
- **Automatically capturing screenshots** every 5 seconds during support calls
- **Keeping screenshots local** until you choose to share them
- **Integrating with GitHub Copilot** for instant AI assistance
- **Maintaining context** across multiple queries in the same session

## How It Works

1. **Start a support call** - Customer shares their screen
2. **Launch Support Copilot** - Begin automatic screenshot capture
3. **When you need help** - Select a predefined prompt template
4. **Add context** - Include the latest screenshot and additional details
5. **Get AI assistance** - GitHub Copilot analyzes the visual context and provides guidance
6. **Iterate as needed** - Continue the conversation with maintained context

*Note: All screenshots remain on your local machine until you explicitly choose to include them in your AI queries.*

[🎥 Watch Demo Video](https://raw.githubusercontent.com/maxshlain/support-copilot/refs/heads/main/demo.mp4)

## Requirements

- **Python 3.10+** (currently tested on macOS only)
- **Visual Studio Code** (latest version)
- **GitHub Copilot** subscription with image-capable model
  - Claude Sonnet recommended for best results
  - Other vision-capable LLMs also supported

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/support-copilot.git
cd support-copilot

# Run the application
uv run src/main.py
```

## Features

- ✅ Automatic screenshot capture (configurable interval)
- ✅ Local storage with privacy controls
- ✅ Predefined prompt templates
- ✅ Context persistence across queries
- ✅ GitHub Copilot integration
- ✅ Cross-platform support (macOS tested)

## Contributing

We welcome contributions! Here's how to get started:

1. Fork this repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test them
4. Submit a pull request with a clear description

Let's build the future of AI-assisted support together! 🚀

## License

[Add your license here]

## Support

If you encounter issues or have questions:
- Open an issue on GitHub
- Check the documentation in `/docs`
- Review existing discussions

