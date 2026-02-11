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

**GitHub Repository:** [github.com/anhfactor/xplain-copilot](https://github.com/anhfactor/xplain-copilot)

## Demo

![xplain cover](assets/cover.png)

### Video Walkthrough

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

I used [GitHub Copilot CLI](https://github.com/github/copilot-cli) (`copilot`) throughout the development of xplain. Here are specific examples of how it shaped the project:

### Building the WTF Command

I launched `copilot` in my project directory and asked:

> *"Add a wtf command that reads zsh and bash shell history, re-runs the last failed command to capture stderr, and explains the failure with a fix."*

Copilot CLI scaffolded the entire `src/commands/wtf.py` module — including the zsh extended history format parser (`: timestamp:0;command`), the bash fallback, subprocess re-execution with timeout, and the AI prompt for diagnosing failures. I iterated on the error output formatting and added the "command succeeded this time" happy path.

<!-- Replace with your actual screenshot: -->
<!-- ![Copilot CLI building wtf command](assets/copilot-wtf-session.png) -->

### Solving the GitHub Models API Authentication

My initial approach used `gh api` to call the Models API, but it returned 401 errors. I asked Copilot CLI:

> *"Why does gh api return 401 when calling models.github.ai? How do I authenticate with the GitHub Models API?"*

It explained that `gh api` only forwards tokens to `api.github.com`, not third-party hosts. It suggested extracting the token via `gh auth token` and making direct HTTP calls with `httpx`. This became the core of `src/core/copilot.py`.

### TL;DR Mode Architecture

I asked Copilot CLI to help design the `--tldr` flag as a global option that affects all commands:

> *"Add a global --tldr flag that switches the AI system prompt to return only a single short sentence instead of detailed explanations."*

It suggested the dual system prompt approach (`SYSTEM_PROMPT` vs `SYSTEM_PROMPT_TLDR`) with a global `_tldr_mode` flag, which was cleaner than modifying every command individually.

### Test Generation

Copilot CLI generated comprehensive tests for the new features:

> *"Write tests for the wtf command's zsh and bash history parsing, the tldr mode toggle, and the shell integration files."*

It created the `TestWTFCommand`, `TestTLDRMode`, and `TestShellIntegration` test classes with proper temp file handling and environment variable cleanup.

The result: **42 tests, all passing**, with good coverage of the core functionality.

### What Made It Special

The most impactful aspect was **agentic iteration**. Instead of context-switching between docs, Stack Overflow, and my editor, I stayed in the terminal and had Copilot CLI plan and execute complex tasks — from scaffolding new commands to debugging API authentication to writing tests. It felt like pair programming with someone who knows every library and can actually edit the files.

---

Built with Python, Typer, Rich, and the GitHub Models API.  
**GitHub Repository:** [github.com/anhfactor/xplain-copilot](https://github.com/anhfactor/xplain-copilot)

