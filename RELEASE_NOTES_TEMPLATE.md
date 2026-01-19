# ChatList v1.0.0

## 🎉 Release Highlights

ChatList is a powerful application for sending prompts to multiple AI models simultaneously and comparing their responses.

## ✨ Features

- ✅ Send one prompt to multiple AI models at once
- ✅ Compare responses side-by-side
- ✅ Save prompts and results to database
- ✅ Tag and categorize prompts
- ✅ Export results to Markdown and JSON
- ✅ Manage multiple AI models through GUI
- ✅ Search and filter prompts and results
- ✅ Comprehensive logging

## 📦 Installation

### Windows Installer (Recommended)

1. Download `ChatList-Setup-v1.0.0.exe`
2. Run the installer
3. Follow the installation wizard
4. Launch ChatList from Start Menu or Desktop shortcut

### Standalone Executable

1. Download `ChatList-v1.0.0.exe`
2. Run directly (no installation required)
3. Note: Database and logs will be created in the same folder

## 🔧 Configuration

After installation, create a `.env` file in the application directory with your API keys:

```env
OPENAI_API_KEY=sk-your-key-here
OPENROUTER_API_KEY=sk-or-v1-your-key-here
DEEPSEEK_API_KEY=sk-your-key-here
GROQ_API_KEY=gsk_your-key-here
```

See README.md for full configuration options.

## 🚀 Quick Start

1. Launch ChatList
2. Configure your API keys in `.env` file
3. Add models through "Models" → "Manage Models..."
4. Enter a prompt and click "Send Request"
5. Compare responses from different models

## 📋 Supported Models

- OpenAI (GPT-4, GPT-3.5-turbo)
- DeepSeek
- Groq
- OpenRouter (supports many models)
- Custom models via OpenAI-compatible API

## 🐛 Bug Fixes

- Fixed issue with [describe bug fix]
- Improved [describe improvement]

## 📝 Changes

- Added [new feature]
- Updated [updated feature]
- Removed [removed feature]

## 🔗 Links

- [Documentation](https://github.com/YOUR_USERNAME/chatList/blob/main/README.md)
- [Report Issues](https://github.com/YOUR_USERNAME/chatList/issues)
- [Source Code](https://github.com/YOUR_USERNAME/chatList)

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Credits

Developed with ❤️ using PyQt5

---

**Full Changelog:** [v0.9.0...v1.0.0](https://github.com/YOUR_USERNAME/chatList/compare/v0.9.0...v1.0.0)

