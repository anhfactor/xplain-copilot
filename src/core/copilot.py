"""GitHub Copilot integration module.

Uses the GitHub Models API (models.github.ai) for AI-powered explanations.
Token is obtained from `gh auth token` (if gh CLI is installed) or from
GH_TOKEN / GITHUB_TOKEN environment variables.
"""

import subprocess
import shutil
import os
from typing import Optional
from abc import ABC, abstractmethod

import httpx


class CopilotCLIError(Exception):
    """Exception raised when Copilot CLI encounters an error."""
    pass


class CopilotNotFoundError(CopilotCLIError):
    """Exception raised when Copilot CLI is not installed."""
    pass


class BackendNotAvailableError(CopilotCLIError):
    """Exception raised when no AI backend is available."""
    pass


# ---------------------------------------------------------------------------
# Backend ABC
# ---------------------------------------------------------------------------

class AIBackend(ABC):
    """Abstract base class for AI backends."""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available."""
        ...
    
    @abstractmethod
    def ask(self, prompt: str, system_prompt: str = "", timeout: int = 120) -> str:
        """Send a prompt and return the response text."""
        ...

    def ask_messages(self, messages: list[dict], timeout: int = 120) -> str:
        """Send a list of messages and return the response text."""
        # Default: extract last user message and call ask()
        user_msg = messages[-1]["content"] if messages else ""
        system_msg = ""
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
                break
        return self.ask(user_msg, system_prompt=system_msg, timeout=timeout)
    
    @property
    @abstractmethod
    def name(self) -> str:
        ...


# ---------------------------------------------------------------------------
# GitHub Models API backend (httpx)
# ---------------------------------------------------------------------------

_cached_token: Optional[str] = None


def _get_github_token() -> Optional[str]:
    """Get GitHub token from environment or gh CLI (cached after first call)."""
    global _cached_token
    if _cached_token is not None:
        return _cached_token

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        _cached_token = token
        return token
    # Try to get from gh auth
    if shutil.which("gh"):
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                _cached_token = result.stdout.strip()
                return _cached_token
        except Exception:
            pass
    return None


class GitHubModelsBackend(AIBackend):
    """Use GitHub Models API via httpx with a GitHub token."""
    
    API_URL = "https://models.github.ai/inference/chat/completions"
    
    def __init__(self, model: Optional[str] = None):
        if model:
            self._model = model
        else:
            self._model = os.environ.get("XPLAIN_MODEL", "openai/gpt-4o-mini")
    
    @property
    def model(self) -> str:
        return self._model
    
    @model.setter
    def model(self, value: str):
        self._model = value
    
    @property
    def name(self) -> str:
        return f"GitHub Models API ({self._model})"
    
    def is_available(self) -> bool:
        return _get_github_token() is not None
    
    def ask(self, prompt: str, system_prompt: str = "", timeout: int = 120) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self.ask_messages(messages, timeout=timeout)

    def ask_messages(self, messages: list[dict], timeout: int = 120) -> str:
        token = _get_github_token()
        if not token:
            raise BackendNotAvailableError("No GitHub token available")
        
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "messages": messages,
                    "model": self._model,
                    "temperature": 0.4,
                    "max_tokens": 2048,
                },
            )
        
        if resp.status_code != 200:
            raise CopilotCLIError(f"GitHub Models API HTTP {resp.status_code}: {resp.text[:300]}")
        
        try:
            data = resp.json()
            if "error" in data:
                raise CopilotCLIError(
                    f"GitHub Models API error: {data['error'].get('message', data['error'])}"
                )
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise CopilotCLIError(f"Failed to parse API response: {exc}")


# Keep old names as aliases for backward compatibility in tests
GhModelsBackend = GitHubModelsBackend
HttpxModelsBackend = GitHubModelsBackend


# ---------------------------------------------------------------------------
# Backend selection
# ---------------------------------------------------------------------------

_backend_instance: Optional[AIBackend] = None


_selected_model: Optional[str] = None


def set_model(model: str):
    """Set the model to use. Called by --model CLI flag."""
    global _selected_model, _backend_instance
    _selected_model = model
    # Reset cached backend so it picks up the new model
    if _backend_instance is not None:
        _backend_instance = None


def _select_backend() -> AIBackend:
    """Select the best available backend."""
    global _backend_instance
    if _backend_instance is not None:
        return _backend_instance
    
    backend = GitHubModelsBackend(model=_selected_model)
    if backend.is_available():
        _backend_instance = backend
        return backend
    
    raise BackendNotAvailableError(
        "No AI backend available. Please either:\n"
        "  1. Install GitHub CLI and authenticate:\n"
        "     brew install gh && gh auth login && gh auth refresh -s copilot\n"
        "  2. Set a GH_TOKEN or GITHUB_TOKEN environment variable\n"
        "You also need an active GitHub Copilot subscription."
    )


def get_backend() -> AIBackend:
    """Get the current AI backend."""
    return _select_backend()


def check_copilot_installed() -> bool:
    """Check if GitHub CLI is installed and available."""
    return shutil.which("gh") is not None


def ensure_copilot_available():
    """Ensure an AI backend is available, raise error if not."""
    _select_backend()


# ---------------------------------------------------------------------------
# High-level helpers (used by commands)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are xplain, an expert developer assistant. "
    "You provide clear, structured, and accurate explanations. "
    "Use markdown formatting in your responses."
)

SYSTEM_PROMPT_TLDR = (
    "You are xplain, an expert developer assistant. "
    "Respond with ONLY a single short sentence (max 15 words). "
    "No markdown, no bullet points, no extra explanation. Just one line."
)

_tldr_mode: bool = False


def set_tldr_mode(enabled: bool):
    """Enable or disable TL;DR mode for ultra-short responses."""
    global _tldr_mode
    _tldr_mode = enabled


def is_tldr_mode() -> bool:
    """Check if TL;DR mode is active."""
    return _tldr_mode


def ask_copilot(prompt: str, verbose: bool = False) -> str:
    """Send a prompt and get the response from the best available backend."""
    backend = _select_backend()
    system = SYSTEM_PROMPT_TLDR if _tldr_mode else SYSTEM_PROMPT
    return backend.ask(prompt, system_prompt=system)


def explain_command(command: str, language: str = "en") -> str:
    """Explain a shell command using AI."""
    prompt = f"""Explain this shell command in detail, step by step.
Command: {command}

Please explain:
1. What this command does overall
2. Break down each part/flag/argument
3. Common use cases
4. Any warnings or cautions

Language: Respond in {language}"""
    
    return ask_copilot(prompt)


def explain_error(error_message: str, context: Optional[str] = None, language: str = "en") -> str:
    """Explain an error message and suggest fixes."""
    context_part = f"\nContext:\n{context}" if context else ""
    
    prompt = f"""Explain this error message and suggest how to fix it.
Error: {error_message}
{context_part}

Please provide:
1. What this error means
2. Common causes
3. Step-by-step solutions
4. How to prevent it in the future

Language: Respond in {language}"""
    
    return ask_copilot(prompt)


def explain_code(code: str, filename: Optional[str] = None, language: str = "en") -> str:
    """Explain a piece of code."""
    file_context = f" (from {filename})" if filename else ""
    
    prompt = f"""Explain this code{file_context} in detail.

```
{code}
```

Please explain:
1. Overall purpose of this code
2. How it works step by step
3. Key concepts and patterns used
4. Potential improvements or issues

Language: Respond in {language}"""
    
    return ask_copilot(prompt)


def explain_diff(diff_text: str, ref: str = "", language: str = "en") -> str:
    """Explain a git diff."""
    ref_context = f" (ref: {ref})" if ref else ""
    
    prompt = f"""Explain this git diff{ref_context} in detail.

```diff
{diff_text}
```

Please explain:
1. Summary of all changes
2. What each changed file/section does
3. Potential impact or risks of these changes
4. Any suggestions for improvement

Language: Respond in {language}"""
    
    return ask_copilot(prompt)


def explain_auto(content: str, content_type: str = "unknown", language: str = "en") -> str:
    """Auto-detect content type and explain accordingly."""
    prompt = f"""Analyze and explain the following terminal/code output.
First determine what it is (error message, code, command output, log, etc.), then explain it.

```
{content}
```

Please provide:
1. What type of content this is
2. Detailed explanation
3. If it's an error: causes and solutions
4. If it's code: how it works and potential improvements
5. If it's output: what it means and any notable items

Language: Respond in {language}"""
    
    return ask_copilot(prompt)


def chat_with_copilot(message: str, history: list[dict] = None, language: str = "en") -> str:
    """Have a conversation with the AI backend using native messages array."""
    backend = _select_backend()

    messages: list[dict] = [
        {
            "role": "system",
            "content": (
                "You are xplain, a helpful developer assistant. "
                "Provide clear, structured, and accurate responses. "
                "Use markdown formatting. "
                f"Respond in {language}."
            ),
        }
    ]

    # Add conversation history (last 10 messages for context)
    if history:
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current user message
    messages.append({"role": "user", "content": message})

    return backend.ask_messages(messages)
