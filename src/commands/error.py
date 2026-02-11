"""Error explanation module."""

import typer
from typing import Optional
from typing_extensions import Annotated
from pathlib import Path

from ..core import (
    explain_error,
    print_explanation,
    print_error,
    print_info,
    LoadingSpinner,
    format_language_flag,
    CopilotCLIError,
)
from ..core.history_store import history
from ..config import config, LANGUAGE_NAMES

def error_cmd(
    message: Annotated[
        str,
        typer.Argument(help="The error message to explain")
    ],
    context: Annotated[
        Optional[str],
        typer.Option("--context", "-c", help="Additional context (code snippet, environment info)")
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option("--file", "-f", help="File containing additional context")
    ] = None,
    lang: Annotated[
        Optional[str],
        typer.Option("--lang", "-l", help="Output language (en, vi, zh, ja, ko, es, fr, de, pt, ru)")
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show verbose output")
    ] = False,
):
    """
    Explain an error message and suggest solutions.
    
    Examples:
        xplain error "TypeError: Cannot read property 'map' of undefined"
        xplain error "ModuleNotFoundError: No module named 'pandas'" --lang vi
        xplain error "ECONNREFUSED 127.0.0.1:5432" -c "Trying to connect to PostgreSQL"
        xplain error "Segmentation fault" -f ./crash_log.txt
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
    
    # Build context from various sources
    full_context = context or ""
    
    if file:
        if not file.exists():
            print_error(f"Context file not found: {file}")
            raise typer.Exit(1)
        try:
            file_content = file.read_text()
            full_context += f"\n\nFrom file {file.name}:\n{file_content}"
        except Exception as e:
            print_error(f"Error reading file: {e}")
            raise typer.Exit(1)
    
    # Show the error being analyzed
    print_info(f"Analyzing error: [bold red]{message}[/]")
    
    # Get explanation from Copilot
    try:
        with LoadingSpinner(f"Diagnosing error {format_language_flag(output_lang)}..."):
            explanation = explain_error(
                message, 
                full_context if full_context else None,
                LANGUAGE_NAMES[output_lang]
            )
        
        print_explanation(
            explanation,
            title="Error Analysis & Solutions",
            subtitle=f"{format_language_flag(output_lang)} {LANGUAGE_NAMES[output_lang]}"
        )
        
        # Save to history
        history.add("error", message, explanation, language=output_lang)
        
    except CopilotCLIError as e:
        print_error(str(e), title="Copilot Error")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}", title="Error")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)
