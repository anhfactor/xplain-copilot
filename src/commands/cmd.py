"""Command explanation module."""

import typer
from typing import Optional
from typing_extensions import Annotated

from ..core import (
    explain_command,
    print_command,
    print_explanation,
    print_error,
    LoadingSpinner,
    format_language_flag,
    CopilotCLIError,
)
from ..core.history_store import history
from ..config import config, LANGUAGE_NAMES

def cmd(
    command: Annotated[
        str,
        typer.Argument(help="The shell command to explain")
    ],
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
    Explain a shell command in detail.
    
    Examples:
        xplain cmd "git rebase -i HEAD~3"
        xplain cmd "find . -name '*.py' -exec grep -l 'import' {} +" --lang vi
        xplain cmd "docker run -it --rm -v $(pwd):/app node:18" -l zh
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
    
    # Show the command being explained
    print_command(command)
    
    # Get explanation from Copilot
    try:
        with LoadingSpinner(f"Analyzing command {format_language_flag(output_lang)}..."):
            explanation = explain_command(command, LANGUAGE_NAMES[output_lang])
        
        print_explanation(
            explanation,
            title="Command Explanation",
            subtitle=f"{format_language_flag(output_lang)} {LANGUAGE_NAMES[output_lang]}"
        )
        
        # Save to history
        history.add("cmd", command, explanation, language=output_lang)
        
    except CopilotCLIError as e:
        print_error(str(e), title="Copilot Error")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}", title="Error")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)
