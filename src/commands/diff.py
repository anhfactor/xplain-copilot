"""Diff command — explain git diffs."""

import subprocess
import typer
from typing import Optional
from typing_extensions import Annotated

from ..core import (
    explain_diff,
    print_explanation,
    print_error,
    print_info,
    LoadingSpinner,
    format_language_flag,
    CopilotCLIError,
)
from ..core.history_store import history as history_store
from ..config import config, LANGUAGE_NAMES

def _get_git_diff(ref: Optional[str] = None, staged: bool = False) -> tuple[str, str]:
    """
    Get git diff output.

    Returns:
        Tuple of (diff_text, description)
    """
    cmd = ["git", "diff"]
    description = "unstaged changes"

    if staged:
        cmd.append("--staged")
        description = "staged changes"
    elif ref:
        cmd.append(ref)
        description = f"changes from {ref}"

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        error_msg = result.stderr.strip() or "Failed to run git diff"
        raise RuntimeError(error_msg)

    return result.stdout.strip(), description


def diff_cmd(
    ref: Annotated[
        Optional[str],
        typer.Argument(help="Git ref to diff against (e.g., HEAD~1, main, abc1234)")
    ] = None,
    staged: Annotated[
        bool,
        typer.Option("--staged", "-s", help="Show staged changes (git diff --staged)")
    ] = False,
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
    Explain git diff output.

    Examples:
        xplain diff                  # Explain unstaged changes
        xplain diff --staged         # Explain staged changes
        xplain diff HEAD~1           # Explain last commit's changes
        xplain diff main             # Explain diff from main branch
        xplain diff HEAD~3 --lang vi # Explain in Vietnamese
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

    # Get the diff
    try:
        diff_text, description = _get_git_diff(ref, staged)
    except FileNotFoundError:
        print_error("git is not installed or not in PATH")
        raise typer.Exit(1)
    except RuntimeError as e:
        print_error(f"Git error: {e}")
        raise typer.Exit(1)

    if not diff_text:
        print_info("No changes found. The diff is empty.")
        raise typer.Exit(0)

    # Show diff stats
    files_changed = diff_text.count("diff --git")
    additions = sum(1 for line in diff_text.splitlines() if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff_text.splitlines() if line.startswith("-") and not line.startswith("---"))

    print_info(
        f"Analyzing {description}: "
        f"[bold]{files_changed}[/] file(s), "
        f"[green]+{additions}[/] additions, "
        f"[red]-{deletions}[/] deletions"
    )

    # Truncate very large diffs to avoid token limits
    max_chars = 8000
    if len(diff_text) > max_chars:
        print_info(f"[yellow]Diff is large ({len(diff_text)} chars), truncating to {max_chars} chars[/]")
        diff_text = diff_text[:max_chars] + "\n\n... (truncated)"

    # Get explanation
    try:
        with LoadingSpinner(f"Analyzing diff {format_language_flag(output_lang)}..."):
            explanation = explain_diff(
                diff_text,
                ref=ref or ("--staged" if staged else "working tree"),
                language=LANGUAGE_NAMES[output_lang],
            )

        print_explanation(
            explanation,
            title="Diff Explanation",
            subtitle=f"{format_language_flag(output_lang)} {LANGUAGE_NAMES[output_lang]}"
        )

        # Save to history
        query = ref or ("--staged" if staged else "working tree")
        history_store.add("diff", f"git diff {query}", explanation, language=output_lang)

    except CopilotCLIError as e:
        print_error(str(e), title="Backend Error")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}", title="Error")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)
