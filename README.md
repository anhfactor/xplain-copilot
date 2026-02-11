# 🚀 xplain

> AI-powered CLI tool to explain code, commands, errors, and git diffs in multiple languages — powered by GitHub Models API.

[![GitHub Copilot CLI Challenge](https://img.shields.io/badge/DEV-GitHub%20Copilot%20CLI%20Challenge-blue)](https://dev.to/challenges/github-2026-01-21)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🔍 **Explain Shell Commands** — Understand complex commands like `git rebase`, `find`, `awk`, etc.
- 🐛 **Diagnose Errors** — Get explanations and solutions for error messages
- 📖 **Understand Code** — Explain code files or snippets in detail
- 🔀 **Explain Git Diffs** — Understand what changed in your code with `xplain diff`
- 🔗 **Smart Pipe** — Pipe any output and auto-detect errors, code, or logs
- 💬 **Interactive Chat** — Have conversations about any dev topic
- 📜 **History** — Browse and search past explanations
- 🤖 **Model Selection** — Choose any AI model from the GitHub Models Marketplace
- 🌍 **Multilingual** — Output in 10+ languages (English, Vietnamese, Chinese, Japanese, etc.)
- 🤯 **WTF Mode** — `xplain wtf` explains the last failed command from your shell history
- ⚡ **TL;DR Mode** — `xplain --tldr cmd "..."` for one-line explanations
- 🐚 **Shell Integration** — Aliases, tab completion, and auto-explain on failure

## 🎬 Demo

```bash
# Explain a complex git command
$ xplain cmd "git rebase -i HEAD~3 --autosquash"

# Diagnose an error (in Vietnamese)
$ xplain error "TypeError: Cannot read property 'map' of undefined" --lang vi

# Understand a code file
$ xplain code ./utils.py

# Explain what changed in your last commit
$ xplain diff HEAD~1

# Pipe errors directly
$ python app.py 2>&1 | xplain pipe

# Start interactive chat
$ xplain chat --lang vi
```

## 📦 Installation

### Prerequisites

1. **Python 3.10+**
2. **GitHub CLI** (recommended):

```bash
# Install GitHub CLI
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Windows
winget install GitHub.cli

# Authenticate
gh auth login

# Add the copilot scope (required for GitHub Models API)
gh auth refresh -s copilot
```

> **Note:** You need an active [GitHub Copilot subscription](https://github.com/features/copilot) to use the GitHub Models API backend. The `copilot` scope is required — without it you'll get HTTP 401 errors.

### Install xplain

```bash
# Clone the repository
git clone https://github.com/xplain/xplain.git
cd xplain

# Install with pip
pip install -e .

# Or with uv (faster)
uv pip install -e .
```

## 🚀 Usage

### Explain Shell Commands

```bash
# Basic usage
xplain cmd "docker run -it --rm -v $(pwd):/app node:18"

# With specific language
xplain cmd "find . -name '*.py' -exec grep -l 'import' {} +" --lang vi

# Short form
xplain cmd "kubectl get pods -A"
```

### Diagnose Errors

```bash
# Basic error explanation
xplain error "ModuleNotFoundError: No module named 'pandas'"

# With additional context
xplain error "ECONNREFUSED 127.0.0.1:5432" -c "Trying to connect to PostgreSQL"

# With context from file
xplain error "Segmentation fault" -f ./crash_log.txt

# In different language
xplain error "NullPointerException" --lang ja
```

### Explain Code

```bash
# Explain a file
xplain code ./app.py

# Explain specific lines
xplain code ./main.go --lines 50-100

# Explain from stdin
cat utils.js | xplain code -

# Explain inline snippet
xplain code "arr.reduce((a,b) => a+b, 0)" -c javascript
```

### Explain Git Diffs

```bash
# Explain unstaged changes
xplain diff

# Explain staged changes
xplain diff --staged

# Explain last commit
xplain diff HEAD~1

# Explain diff from main branch (in Vietnamese)
xplain diff main --lang vi
```

### Smart Pipe

```bash
# Pipe error output — auto-detects errors vs code vs logs
python app.py 2>&1 | xplain pipe

# Pipe build output
npm run build 2>&1 | xplain pipe

# Force content type
cat error.log | xplain pipe --type error

# Pipe with language
cargo build 2>&1 | xplain pipe --lang ja
```

### Interactive Chat

```bash
# Start chat
xplain chat

# Chat in Vietnamese
xplain chat --lang vi

# Inside chat:
# /help  - Show commands
# /lang vi - Change language
# /clear - Clear history
# /exit  - Exit
```

### Explanation History

```bash
# List recent explanations
xplain history

# Search history
xplain history --search "docker"

# Show full details of most recent entry
xplain history --show 1

# Filter by command type
xplain history --type cmd

# Clear all history
xplain history --clear
```

### WTF — Explain Last Failed Command

```bash
# Something failed? Just type:
xplain wtf

# In Vietnamese
xplain wtf --lang vi
```

This reads your shell history, re-runs the last command, captures the error, and explains what went wrong with a fix.

### TL;DR Mode

```bash
# Get a one-line explanation instead of a detailed breakdown
xplain --tldr cmd "git rebase -i HEAD~3"
xplain --tldr error "ECONNREFUSED 127.0.0.1:5432"
xplain --tldr diff HEAD~1
```

### Export Output

```bash
# Save explanation to markdown
xplain cmd "git rebase -i HEAD~3" -o explanation.md

# Save as JSON
xplain error "TypeError: ..." -o error.json

# Save as plain text
xplain diff HEAD~1 -o changes.txt

# Disable colors (useful for piping)
xplain cmd "ls -la" --no-color
```

### Model Selection

```bash
# List available models
xplain models

# Use a specific model for one command
xplain --model openai/gpt-4.1 cmd "git rebase -i HEAD~3"

# Use DeepSeek R1 for reasoning
xplain -m deepseek/DeepSeek-R1 error "segfault in main.c"

# Set default model via environment variable
export XPLAIN_MODEL=openai/gpt-4.1  # Add to ~/.bashrc or ~/.zshrc
```

Supported models include `openai/gpt-4o-mini` (default), `openai/gpt-4o`, `openai/gpt-4.1`, `meta/llama-4-scout-17b-16e-instruct`, `deepseek/DeepSeek-R1`, and any model from the [GitHub Models Marketplace](https://github.com/marketplace/models).

### Other Commands

```bash
# Check setup and backend status
xplain check

# Show configuration
xplain config --show

# List available AI models
xplain models

# List supported languages
xplain langs

# Show version
xplain version
```

## 🌍 Supported Languages

| Code | Language | Flag |
|------|----------|------|
| `en` | English | 🇺🇸 |
| `vi` | Tiếng Việt | 🇻🇳 |
| `zh` | 中文 | 🇨🇳 |
| `ja` | 日本語 | 🇯🇵 |
| `ko` | 한국어 | 🇰🇷 |
| `es` | Español | 🇪🇸 |
| `fr` | Français | 🇫🇷 |
| `de` | Deutsch | 🇩🇪 |
| `pt` | Português | 🇧🇷 |
| `ru` | Русский | 🇷🇺 |

Set default language:
```bash
export XPLAIN_LANG=vi  # Add to ~/.bashrc or ~/.zshrc
```

## 🐚 Shell Integration

Enable shell aliases and auto-explain on command failure:

```bash
# zsh — add to ~/.zshrc
source /path/to/xplain/shell/xplain.zsh

# bash — add to ~/.bashrc
source /path/to/xplain/shell/xplain.bash
```

This gives you:
- **`wtf`** — alias for `xplain wtf` (explain last failed command)
- **`xc`**, **`xe`**, **`xd`**, **`xw`** — quick aliases for cmd, error, diff, wtf
- **Auto command-not-found handler** — suggests xplain when a command isn't found

### Shell Completion

```bash
# Install tab completion for your shell
xplain --install-completion

# Or generate completion script
xplain --show-completion
```

## ⚙️ Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `XPLAIN_LANG` | Default output language | `en` |
| `XPLAIN_MODEL` | Default AI model | `openai/gpt-4o-mini` |
| `XPLAIN_VERBOSE` | Enable verbose output | `false` |
| `GH_TOKEN` / `GITHUB_TOKEN` | GitHub token (alternative to `gh auth`) | — |

### AI Backend

xplain uses the **GitHub Models API** (`models.github.ai`) for AI-powered explanations via `httpx`. Token is auto-detected from:

1. **`gh auth token`** — Recommended. Uses your GitHub CLI session (requires `copilot` scope).
2. **`GH_TOKEN` / `GITHUB_TOKEN`** — Environment variable fallback.

Run `xplain check` to verify your setup.

## 🛠️ Development

```bash
# Clone repo
git clone https://github.com/xplain/xplain.git
cd xplain

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .
```

## 📁 Project Structure

```
xplain/
├── src/
│   ├── __init__.py
│   ├── cli.py              # Main CLI entry point
│   ├── config.py            # Configuration management
│   ├── commands/
│   │   ├── cmd.py           # Shell command explainer
│   │   ├── error.py         # Error message explainer
│   │   ├── code.py          # Code file explainer
│   │   ├── chat.py          # Interactive chat mode
│   │   ├── diff.py          # Git diff explainer
│   │   ├── pipe.py          # Smart stdin pipe handler
│   │   ├── history.py       # Explanation history browser
│   │   └── wtf.py           # WTF — explain last failed command
│   └── core/
│       ├── copilot.py       # AI backend (GitHub Models API)
│       ├── formatter.py     # Rich terminal formatting
│       └── history_store.py # JSON-based history storage
├── shell/
│   ├── xplain.zsh           # Zsh shell integration
│   └── xplain.bash          # Bash shell integration
├── tests/
├── pyproject.toml
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [GitHub Models API](https://github.com/marketplace/models) for the AI power
- [GitHub CLI](https://cli.github.com/) for seamless authentication
- [Typer](https://typer.tiangolo.com/) for the awesome CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output

---

<p align="center">
  Built with ❤️ for the <a href="https://dev.to/challenges/github-2026-01-21">GitHub Copilot CLI Challenge</a>
</p>
