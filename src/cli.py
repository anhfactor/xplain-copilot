"""
xplain CLI - AI-powered code & command explainer

A CLI tool powered by GitHub Models API to explain code, commands,
and errors in multiple languages.
"""

import typer
import subprocess
from typing import Optional
from typing_extensions import Annotated

from .config import config, LANGUAGE_NAMES
from .core import (
    print_banner,
    print_info,
    print_success,
    print_error,
    print_warning,
    check_copilot_installed,
    get_backend,
    set_model,
    set_tldr_mode,
    BackendNotAvailableError,
    format_language_flag,
    set_output_file,
    console,
)
from .config import AVAILABLE_MODELS
from .commands import cmd, error_cmd, code_cmd, chat, pipe_cmd, diff_cmd, history_cmd, wtf_cmd

# Create main app
app = typer.Typer(
    name="xplain",
    help="\U0001f680 AI-powered CLI tool to explain code, commands, and errors",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

@app.callback()
def main_callback(
    output: Annotated[
        Optional[str],
        typer.Option("--output", "-o", help="Save explanation to file (.md, .json, or .txt)")
    ] = None,
    no_color: Annotated[
        bool,
        typer.Option("--no-color", help="Disable colored output")
    ] = False,
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="AI model to use (e.g. openai/gpt-4.1, deepseek/DeepSeek-R1)")
    ] = None,
    tldr: Annotated[
        bool,
        typer.Option("--tldr", help="Get a one-line TL;DR explanation instead of detailed output")
    ] = False,
):
    """Global options applied before any subcommand."""
    if output:
        set_output_file(output)
    if no_color:
        from .core.formatter import console as fmt_console
        fmt_console.no_color = True
    if model:
        set_model(model)
    if tldr:
        set_tldr_mode(True)


# Register subcommands
app.command(name="cmd", help="Explain shell commands")(cmd)
app.command(name="error", help="Explain errors and suggest fixes")(error_cmd)
app.command(name="code", help="Explain code files or snippets")(code_cmd)
app.command(name="chat", help="Interactive chat mode")(chat)
app.command(name="pipe", help="Auto-detect and explain piped input")(pipe_cmd)
app.command(name="diff", help="Explain git diffs")(diff_cmd)
app.command(name="history", help="Browse explanation history")(history_cmd)
app.command(name="wtf", help="Explain the last failed command from shell history")(wtf_cmd)


@app.command()
def version():
    """Show version information."""
    from importlib.metadata import version as pkg_version, PackageNotFoundError

    try:
        ver = pkg_version("xplain")
    except PackageNotFoundError:
        ver = "0.1.0 (dev)"

    console.print(f"[bold cyan]xplain[/] version [green]{ver}[/]")
    console.print(f"Python: {__import__('sys').version.split()[0]}")

    # Check backend status
    try:
        backend = get_backend()
        print_success(f"AI Backend: {backend.name} ✓")
    except BackendNotAvailableError:
        print_warning("AI Backend: Not configured")
        print_info("Run: xplain check")
    console.print(f"Model:  {config.model}")


@app.command()
def check():
    """Check if all dependencies are properly configured."""
    print_banner()

    console.print("\n[bold]Checking dependencies...[/]\n")

    all_ok = True

    # Check GitHub CLI
    if check_copilot_installed():
        print_success("GitHub CLI (gh) is installed")

        # Check if authenticated
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print_success("GitHub CLI is authenticated")
        else:
            print_error("GitHub CLI is not authenticated")
            print_info("Run: gh auth login")
            all_ok = False
    else:
        print_warning("GitHub CLI (gh) is not installed (optional but recommended)")
        print_info("Install: brew install gh  (macOS) | sudo apt install gh  (Linux)")

    # Check AI backend
    console.print(f"  Model: [yellow]{config.model}[/]")
    try:
        backend = get_backend()
        print_success(f"AI Backend available: {backend.name}")
    except BackendNotAvailableError:
        print_error("No AI backend available")
        print_info(
            "Options:\n"
            "  1. Install & authenticate GitHub CLI:\n"
            "     brew install gh && gh auth login && gh auth refresh -s copilot\n"
            "  2. Set GH_TOKEN or GITHUB_TOKEN environment variable"
        )
        all_ok = False

    # Check git
    import shutil
    if shutil.which("git"):
        print_success("git is installed (needed for 'diff' command)")
    else:
        print_warning("git is not installed (needed for 'diff' command)")

    if all_ok:
        console.print("\n[bold green]✓ All checks passed! You're ready to use xplain.[/]")
    else:
        console.print("\n[bold yellow]⚠ Some checks failed. See above for details.[/]")


@app.command(name="config")
def config_cmd(
    show: Annotated[
        bool,
        typer.Option("--show", "-s", help="Show current configuration")
    ] = False,
    set_lang: Annotated[
        Optional[str],
        typer.Option("--lang", "-l", help="Set default language")
    ] = None,
):
    """View or modify configuration."""
    if set_lang:
        if set_lang not in LANGUAGE_NAMES:
            print_error(f"Unsupported language: {set_lang}")
            print_info(f"Available: {', '.join(LANGUAGE_NAMES.keys())}")
            raise typer.Exit(1)

        # Update environment variable hint
        print_success(f"To set default language to {format_language_flag(set_lang)} {LANGUAGE_NAMES[set_lang]}:")
        console.print(f"\n  [yellow]export XPLAIN_LANG={set_lang}[/]")
        console.print("\n  Add this to your ~/.bashrc or ~/.zshrc")
        return

    # Show current config
    console.print("\n[bold cyan]Current Configuration:[/]\n")
    console.print(f"  Language: {format_language_flag(config.language)} {config.language_name}")
    console.print(f"  Model:    {config.model}")
    console.print(f"  Verbose:  {config.verbose}")
    console.print(f"  Config:   {config.config_dir}")
    console.print(f"  Cache:    {config.cache_dir}")

    # Show backend info
    try:
        backend = get_backend()
        console.print(f"  Backend:  {backend.name}")
    except BackendNotAvailableError:
        console.print("  Backend:  [red]Not available[/]")

    console.print("\n[bold cyan]Available Languages:[/]\n")
    for lang_code, name in LANGUAGE_NAMES.items():
        flag = format_language_flag(lang_code)
        marker = " [green]← current[/]" if lang_code == config.language else ""
        console.print(f"  {flag} {lang_code}: {name}{marker}")


@app.command()
def models():
    """List available AI models."""
    console.print("\n[bold cyan]Available AI Models:[/]\n")

    current = config.model
    for model_id, description in AVAILABLE_MODELS.items():
        marker = " [green]← current[/]" if model_id == current else ""
        console.print(f"  [yellow]{model_id}[/]  {description}{marker}")

    console.print("\n[dim]Use --model/-m option with any command, or set XPLAIN_MODEL env var[/]")
    console.print("[dim]Any model from https://github.com/marketplace/models is supported[/]")


@app.command()
def langs():
    """List all supported languages."""
    console.print("\n[bold cyan]Supported Languages:[/]\n")
    for lang_code, name in LANGUAGE_NAMES.items():
        flag = format_language_flag(lang_code)
        console.print(f"  {flag} [yellow]{lang_code}[/]: {name}")
    console.print("\n[dim]Use --lang/-l option with any command to set output language[/]")


# Aliases for convenience
@app.command(name="c", hidden=True)
def cmd_alias(
    command: str,
    lang: Optional[str] = None,
):
    """Alias for 'cmd' command."""
    cmd(command, lang)


@app.command(name="e", hidden=True)
def error_alias(
    message: str,
    context: Optional[str] = None,
    lang: Optional[str] = None,
):
    """Alias for 'error' command."""
    error_cmd(message, context=context, lang=lang)


@app.command(name="d", hidden=True)
def diff_alias(
    ref: Optional[str] = None,
    staged: bool = False,
    lang: Optional[str] = None,
    verbose: bool = False,
):
    """Alias for 'diff' command."""
    diff_cmd(ref, staged=staged, lang=lang, verbose=verbose)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
