"""Pipe command — auto-detect and explain stdin content."""

import sys
import typer
from typing import Optional
from typing_extensions import Annotated

from ..core import (
    explain_auto,
    explain_error,
    explain_code,
    print_explanation,
    print_error,
    print_info,
    LoadingSpinner,
    format_language_flag,
    CopilotCLIError,
)
from ..core.history_store import history as history_store
from ..config import config, LANGUAGE_NAMES

# Patterns that suggest the content is an error/traceback
ERROR_PATTERNS = [
    "Traceback (most recent call last)",
    "Error:",
    "Exception:",
    "error:",
    "FATAL",
    "FAIL",
    "panic:",
    "Segmentation fault",
    "ECONNREFUSED",
    "ENOENT",
    "EPERM",
    "errno",
    "SyntaxError",
    "TypeError",
    "ValueError",
    "KeyError",
    "IndexError",
    "AttributeError",
    "ImportError",
    "ModuleNotFoundError",
    "FileNotFoundError",
    "PermissionError",
    "RuntimeError",
    "NullPointerException",
    "ClassNotFoundException",
    "ArrayIndexOutOfBoundsException",
    "undefined is not a function",
    "Cannot read propert",
    "is not defined",
    "command not found",
    "No such file or directory",
    "Permission denied",
]


def _detect_content_type(content: str) -> str:
    """Heuristic to detect if content is an error, code, or general output."""
    lines = content.strip().splitlines()
    if not lines:
        return "unknown"

    error_score = 0
    for line in lines:
        for pattern in ERROR_PATTERNS:
            if pattern.lower() in line.lower():
                error_score += 1

    # If more than ~10% of lines match error patterns, treat as error
    if error_score > 0 and (error_score / len(lines)) > 0.05:
        return "error"

    # Check for code-like patterns
    code_indicators = [
        "def ", "class ", "import ", "from ",  # Python
        "function ", "const ", "let ", "var ",  # JS
        "func ", "package ",  # Go
        "public ", "private ", "static ",  # Java/C#
        "#include", "int main",  # C/C++
    ]
    code_score = sum(1 for line in lines for ind in code_indicators if ind in line)
    if code_score > 0 and (code_score / len(lines)) > 0.1:
        return "code"

    return "auto"


def pipe_cmd(
    lang: Annotated[
        Optional[str],
        typer.Option("--lang", "-l", help="Output language (en, vi, zh, ja, ko, es, fr, de, pt, ru)")
    ] = None,
    force_type: Annotated[
        Optional[str],
        typer.Option("--type", "-t", help="Force content type: error, code, or auto")
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show verbose output")
    ] = False,
):
    """
    Auto-detect and explain piped input from stdin.

    Examples:
        python app.py 2>&1 | xplain pipe
        cat error.log | xplain pipe --lang vi
        git log --oneline -5 | xplain pipe
        npm test 2>&1 | xplain pipe --type error
    """
    # Check if there's actually stdin data
    if sys.stdin.isatty():
        print_error(
            "No piped input detected.\n\n"
            "Usage: <command> | xplain pipe\n\n"
            "Examples:\n"
            "  python app.py 2>&1 | xplain pipe\n"
            "  cat error.log | xplain pipe\n"
            "  npm test 2>&1 | xplain pipe --type error"
        )
        raise typer.Exit(1)

    # Read stdin
    content = sys.stdin.read().strip()
    if not content:
        print_error("Received empty input from stdin")
        raise typer.Exit(1)

    # Use provided language or fall back to config
    output_lang = lang or config.language

    # Validate language
    if output_lang not in LANGUAGE_NAMES:
        print_error(
            f"Unsupported language: {output_lang}\n"
            f"Supported: {', '.join(LANGUAGE_NAMES.keys())}"
        )
        raise typer.Exit(1)

    # Detect content type
    content_type = force_type or _detect_content_type(content)

    # Show what we detected
    type_label = {"error": "Error/Traceback", "code": "Code", "auto": "General Output"}.get(
        content_type, "Unknown"
    )
    print_info(f"Detected content type: [bold]{type_label}[/]")

    # Truncate display for very long content
    lines = content.splitlines()
    if len(lines) > 30:
        preview = "\n".join(lines[:15]) + f"\n\n... ({len(lines)} lines total) ...\n\n" + "\n".join(lines[-5:])
    else:
        preview = content
    print_info(f"Input preview:\n[dim]{preview[:500]}[/]")

    # Get explanation
    try:
        with LoadingSpinner(f"Analyzing input {format_language_flag(output_lang)}..."):
            if content_type == "error":
                explanation = explain_error(content, language=LANGUAGE_NAMES[output_lang])
            elif content_type == "code":
                explanation = explain_code(content, language=LANGUAGE_NAMES[output_lang])
            else:
                explanation = explain_auto(content, content_type=content_type, language=LANGUAGE_NAMES[output_lang])

        print_explanation(
            explanation,
            title="Analysis",
            subtitle=f"{format_language_flag(output_lang)} {LANGUAGE_NAMES[output_lang]}"
        )

        # Save to history
        query_preview = content[:200] if len(content) > 200 else content
        history_store.add("pipe", query_preview, explanation, language=output_lang)

    except CopilotCLIError as e:
        print_error(str(e), title="Backend Error")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}", title="Error")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)
