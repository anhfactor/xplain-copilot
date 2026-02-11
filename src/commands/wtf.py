"""WTF command — explain the last failed command from shell history."""

import os
import subprocess
import typer
from typing import Optional
from typing_extensions import Annotated

from ..core import (
    explain_command,
    print_explanation,
    print_error,
    print_info,
    print_warning,
    LoadingSpinner,
    format_language_flag,
    CopilotCLIError,
    console,
    ask_copilot,
)
from ..core.history_store import history as history_store
from ..config import config, LANGUAGE_NAMES


def _get_last_command_zsh() -> Optional[str]:
    """Try to read the last command from zsh history file."""
    histfile = os.environ.get("HISTFILE", os.path.expanduser("~/.zsh_history"))
    try:
        # zsh history can have multi-byte encoding issues; read as bytes
        with open(histfile, "rb") as f:
            # Read last few KB to find the last command
            f.seek(0, 2)
            size = f.tell()
            read_size = min(size, 8192)
            f.seek(size - read_size)
            data = f.read()

        # Decode with error handling
        lines = data.decode("utf-8", errors="replace").strip().splitlines()

        # zsh extended history format: ": timestamp:0;command"
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            if line.startswith(": ") and ";" in line:
                return line.split(";", 1)[1].strip()
            return line
    except (FileNotFoundError, PermissionError, OSError):
        pass
    return None


def _get_last_command_bash() -> Optional[str]:
    """Try to read the last command from bash history file."""
    histfile = os.environ.get("HISTFILE", os.path.expanduser("~/.bash_history"))
    try:
        with open(histfile, "r", errors="replace") as f:
            lines = f.readlines()
        for line in reversed(lines):
            line = line.strip()
            if line:
                return line
    except (FileNotFoundError, PermissionError, OSError):
        pass
    return None


def _get_last_command() -> Optional[str]:
    """Get the last command from shell history."""
    shell = os.environ.get("SHELL", "")

    if "zsh" in shell:
        cmd = _get_last_command_zsh()
        if cmd:
            return cmd

    cmd = _get_last_command_bash()
    if cmd:
        return cmd

    # Fallback: try zsh even if SHELL isn't zsh
    return _get_last_command_zsh()


def wtf_cmd(
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
    Explain the last failed command from your shell history.

    Reads your shell history to find the most recent command and explains
    what went wrong and how to fix it. Works with zsh and bash.

    Examples:
        xplain wtf
        xplain wtf --lang vi
    """
    output_lang = lang or config.language

    if output_lang not in LANGUAGE_NAMES:
        print_error(
            f"Unsupported language: {output_lang}\n"
            f"Supported: {', '.join(LANGUAGE_NAMES.keys())}"
        )
        raise typer.Exit(1)

    # Get the last command from shell history
    last_cmd = _get_last_command()

    if not last_cmd:
        print_error(
            "Could not read your shell history.\n\n"
            "Make sure your shell saves history:\n"
            "  zsh:  HISTFILE=~/.zsh_history\n"
            "  bash: HISTFILE=~/.bash_history"
        )
        raise typer.Exit(1)

    # Skip if the last command is xplain itself
    if last_cmd.startswith("xplain"):
        print_warning("Last command in history is an xplain command itself.")
        print_info("Try running a command first, then use `xplain wtf`")
        raise typer.Exit(1)

    console.print(f"\n[bold yellow]🤔 Last command:[/] [dim]{last_cmd}[/]\n")

    # Try to re-run the command to capture the error output
    print_info("Re-running command to capture output...")
    try:
        result = subprocess.run(
            last_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        exit_code = result.returncode
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
    except subprocess.TimeoutExpired:
        exit_code = 1
        stderr = "(command timed out after 15s)"
        stdout = ""
    except Exception as e:
        exit_code = 1
        stderr = str(e)
        stdout = ""

    if exit_code == 0:
        console.print("[bold green]✓ The command succeeded this time![/]\n")
        print_info("Explaining what it does anyway...")
        # Explain the command itself
        try:
            with LoadingSpinner(f"Analyzing command {format_language_flag(output_lang)}..."):
                explanation = explain_command(last_cmd, LANGUAGE_NAMES[output_lang])

            print_explanation(
                explanation,
                title="Command Explanation",
                subtitle=f"{format_language_flag(output_lang)} {LANGUAGE_NAMES[output_lang]}"
            )
            history_store.add("wtf", last_cmd, explanation, language=output_lang)
        except CopilotCLIError as e:
            print_error(str(e), title="Backend Error")
            raise typer.Exit(1)
        return

    # Command failed — explain the error
    error_output = stderr or stdout or "(no output captured)"

    console.print(f"[bold red]✗ Exit code {exit_code}[/]")
    if stderr:
        console.print(f"[dim]{stderr[:300]}[/]\n")

    try:
        with LoadingSpinner(f"Diagnosing failure {format_language_flag(output_lang)}..."):
            prompt = f"""A developer ran this command and it failed. Explain what went wrong and how to fix it.

Command: {last_cmd}
Exit code: {exit_code}
Error output:
{error_output[:2000]}

Please provide:
1. What the command was trying to do
2. Why it failed
3. Step-by-step fix
4. The corrected command (if applicable)

Language: Respond in {LANGUAGE_NAMES[output_lang]}"""
            explanation = ask_copilot(prompt)

        print_explanation(
            explanation,
            title="WTF — What The Failure",
            subtitle=f"{format_language_flag(output_lang)} {LANGUAGE_NAMES[output_lang]}"
        )

        history_store.add("wtf", f"{last_cmd} (exit {exit_code})", explanation, language=output_lang)

    except CopilotCLIError as e:
        print_error(str(e), title="Backend Error")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}", title="Error")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)
