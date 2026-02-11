"""Code explanation module."""

import typer
import sys
from typing import Optional
from typing_extensions import Annotated
from pathlib import Path

from ..core import (
    explain_code,
    print_code,
    print_explanation,
    print_error,
    print_info,
    LoadingSpinner,
    format_language_flag,
    detect_code_language,
    CopilotCLIError,
)
from ..core.history_store import history
from ..config import config, LANGUAGE_NAMES

def code_cmd(
    source: Annotated[
        Optional[str],
        typer.Argument(help="File path or code snippet (use '-' for stdin)")
    ] = None,
    lang: Annotated[
        Optional[str],
        typer.Option("--lang", "-l", help="Output language (en, vi, zh, ja, ko, es, fr, de, pt, ru)")
    ] = None,
    code_lang: Annotated[
        Optional[str],
        typer.Option("--code-lang", "-c", help="Programming language (auto-detected from file extension)")
    ] = None,
    lines: Annotated[
        Optional[str],
        typer.Option("--lines", help="Line range to explain (e.g., '10-20')")
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show verbose output")
    ] = False,
):
    """
    Explain code from a file or snippet.
    
    Examples:
        xplain code ./utils.py
        xplain code ./app.js --lang vi
        xplain code ./main.go --lines 50-100
        echo "print('hello')" | xplain code -
        xplain code "const x = arr.reduce((a,b) => a+b, 0)" -c javascript
    """
    # Use provided language or fall back to config
    output_lang = lang or config.language
    
    # Validate language
    if output_lang not in LANGUAGE_NAMES:
        print_error(
            f"Unsupported language: {output_lang}\n"
            f"Supported: {', '.join(LANGUAGE_NAMES.keys())}"
        )
        raise typer.Exit(1)
    
    # Get code from various sources
    code_content = ""
    filename = None
    programming_lang = code_lang or "text"
    
    if source is None:
        # No argument provided - check if there's stdin
        if not sys.stdin.isatty():
            code_content = sys.stdin.read()
        else:
            print_error("Please provide a file path, code snippet, or pipe code via stdin")
            print_info("Examples:")
            print_info("  xplain code ./myfile.py")
            print_info("  xplain code \"print('hello')\"")
            print_info("  cat myfile.py | xplain code -")
            raise typer.Exit(1)
    
    elif source == "-":
        # Read from stdin
        code_content = sys.stdin.read()
    
    elif Path(source).exists():
        # Read from file
        filepath = Path(source)
        filename = filepath.name
        programming_lang = code_lang or detect_code_language(filename)
        
        try:
            code_content = filepath.read_text()
        except Exception as e:
            print_error(f"Error reading file: {e}")
            raise typer.Exit(1)
        
        # Handle line range if specified
        if lines:
            try:
                start, end = map(int, lines.split("-"))
                code_lines = code_content.splitlines()
                code_content = "\n".join(code_lines[start-1:end])
                filename = f"{filename} (lines {start}-{end})"
            except ValueError:
                print_error("Invalid line range format. Use: --lines START-END (e.g., --lines 10-20)")
                raise typer.Exit(1)
    
    else:
        # Treat as inline code snippet
        code_content = source
    
    if not code_content.strip():
        print_error("No code content provided")
        raise typer.Exit(1)
    
    # Truncate very long code for display (but send full to Copilot)
    display_code = code_content
    if len(code_content.splitlines()) > 50:
        display_lines = code_content.splitlines()
        display_code = "\n".join(display_lines[:25]) + "\n\n... (truncated for display) ...\n\n" + "\n".join(display_lines[-10:])
    
    # Show the code being analyzed
    print_code(display_code, programming_lang, filename)
    
    # Get explanation from Copilot
    try:
        with LoadingSpinner(f"Analyzing code {format_language_flag(output_lang)}..."):
            explanation = explain_code(
                code_content,
                filename,
                LANGUAGE_NAMES[output_lang]
            )
        
        print_explanation(
            explanation,
            title="Code Explanation",
            subtitle=f"{format_language_flag(output_lang)} {LANGUAGE_NAMES[output_lang]}"
        )
        
        # Save to history
        query = filename or source or "stdin"
        history.add("code", query, explanation, language=output_lang)
        
    except CopilotCLIError as e:
        print_error(str(e), title="Copilot Error")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}", title="Error")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)
