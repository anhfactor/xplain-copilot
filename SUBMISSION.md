---
title: xplain — AI-Powered CLI to Explain Code, Commands & Errors
published: false
tags: devchallenge, githubchallenge, cli, githubcopilot
---

*This is a submission for the [GitHub Copilot CLI Challenge](https://dev.to/challenges/github-2026-01-21)*

## What I Built

**xplain** is a developer-focused CLI tool that uses the GitHub Models API to explain code, shell commands, error messages, and git diffs — in 10+ languages.

As developers, we constantly encounter unfamiliar commands, cryptic errors, and complex diffs. xplain brings AI-powered explanations directly into your terminal workflow:

- **`xplain cmd "git rebase -i HEAD~3 --autosquash"`** — breaks down every flag and argument
- **`xplain error "TypeError: Cannot read property 'map' of undefined"`** — diagnoses the error and suggests fixes
- **`xplain code ./utils.py`** — explains code files step by step
- **`xplain diff HEAD~1`** — summarizes what changed in your last commit
- **`python app.py 2>&1 | xplain pipe`** — auto-detects if piped input is an error, code, or logs
- **`xplain chat`** — interactive chat for any dev question
- **`xplain history`** — browse and search past explanations
- **`xplain wtf`** — 🤯 explain the last failed command from your shell history
- **`xplain --tldr cmd "..."`** — ⚡ one-line TL;DR explanations

All commands support `--lang` for multilingual output (English, Vietnamese, Chinese, Japanese, Korean, Spanish, French, German, Portuguese, Russian), `--model` to choose any AI model from the GitHub Models Marketplace (GPT-4o, GPT-4.1, Llama 4, DeepSeek R1, etc.), and `--output` to export explanations to `.md`, `.json`, or `.txt` files.

### Key Features

- **WTF Mode** — `xplain wtf` reads your shell history, re-runs the last command, captures the error, and explains what went wrong with a fix. Fun, memorable, and solves a real pain point.
- **TL;DR Mode** — `xplain --tldr` for ultra-short one-line explanations across all commands
- **Model Selection** — choose any model from the GitHub Models Marketplace (`--model openai/gpt-4.1`, `--model deepseek/DeepSeek-R1`, etc.)
- **Smart Pipe Detection** — automatically classifies piped input as error, code, or general output using heuristic pattern matching
- **Git Diff Explanations** — understands unstaged, staged, or ref-based diffs with file stats
- **Shell Integration** — `source shell/xplain.zsh` for aliases (`wtf`, `xc`, `xe`, `xd`), tab completion, and auto command-not-found handler
- **Persistent History** — JSON-based local storage of all explanations, searchable and filterable
- **Export** — save any explanation to markdown, JSON, or plain text
- **Beautiful Terminal UI** — Rich-powered panels, syntax highlighting, loading spinners, and language flags

## Demo

![xplain cover](assets/cover.png)

### Feature Walkthrough

![xplain demo](assets/demo.gif)

The demo shows xplain in action:
1. **Explain commands** — `xplain cmd "git rebase -i HEAD~3" --lang vi` with Vietnamese output
2. **Diagnose errors** — `xplain error "TypeError: ..."` with fix suggestions
3. **Smart pipe** — `npm run build 2>&1 | xplain pipe` auto-detects error output
4. **Model selection** — `xplain --model deepseek/DeepSeek-R1 diff HEAD~1`
5. **WTF mode** — `xplain wtf` explains the last failed command
6. **TL;DR mode** — `xplain --tldr cmd "..."` for one-line answers
7. **Shell integration** — aliases, tab completion, auto-explain on failure

## My Experience with GitHub Copilot CLI

GitHub Copilot CLI was instrumental throughout the development of xplain:

### Architecture & Design
I used Copilot CLI to explore different approaches for integrating with the GitHub Models API. When the initial `gh api` approach failed with 401 errors (because `gh api` doesn't forward tokens to non-github.com hosts), Copilot helped me quickly iterate on the solution — extracting the token via `gh auth token` and making direct HTTP calls with `httpx`.

### Code Generation
Copilot CLI accelerated the implementation of:
- The **dual-backend architecture** with abstract base classes and automatic fallback
- **Content type detection** heuristics for the `pipe` command (error patterns, code indicators)
- **Git diff parsing** with file stats (additions, deletions, files changed)
- **Rich terminal formatting** with panels, syntax highlighting, and spinners
- The **history store** with JSON persistence, search, and pagination

### Debugging & Problem Solving
When I hit the GitHub Models API authentication issue, Copilot CLI helped me understand the difference between `gh api` (scoped to api.github.com) and direct API calls to `models.github.ai`. It suggested the `gh auth refresh -s copilot` fix and the `curl`-then-`httpx` migration path.

### Testing
Copilot CLI helped generate comprehensive tests covering:
- CLI command registration and help output
- History store CRUD operations
- Pipe content type detection (error, code, auto, empty)
- Backend class hierarchy and availability checks
- Export functionality (markdown, JSON, plain text)

The result: **42 tests, all passing**, with good coverage of the core functionality.

### What Made It Special
The most impactful aspect was the **speed of iteration**. What would normally take hours of reading docs and Stack Overflow took minutes with Copilot CLI suggesting the right patterns, API calls, and error handling. It felt like pair programming with someone who knows every library.

---

Built with Python, Typer, Rich, and the GitHub Models API.

