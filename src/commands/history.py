"""History command — browse and search past explanations."""

import typer
from typing import Optional
from typing_extensions import Annotated
from rich.table import Table

from ..core import (
    console,
    print_explanation,
    print_error,
    print_info,
    print_success,
    format_language_flag,
)
from ..core.history_store import history as history_store

def history_cmd(
    search: Annotated[
        Optional[str],
        typer.Option("--search", "-s", help="Search history by keyword")
    ] = None,
    show: Annotated[
        Optional[int],
        typer.Option("--show", help="Show full details of entry N (1 = most recent)")
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", "-n", help="Number of entries to show")
    ] = 20,
    type_filter: Annotated[
        Optional[str],
        typer.Option("--type", "-t", help="Filter by type: cmd, error, code, diff, pipe, chat")
    ] = None,
    clear: Annotated[
        bool,
        typer.Option("--clear", help="Clear all history")
    ] = False,
):
    """
    Browse and search past explanations.

    Examples:
        xplain history                    # List recent explanations
        xplain history --search "docker"  # Search for docker-related
        xplain history --show 1           # Show most recent in full
        xplain history --type cmd         # Filter by command type
        xplain history --clear            # Clear all history
    """
    if clear:
        count = history_store.count()
        history_store.clear()
        print_success(f"Cleared {count} history entries")
        return

    if show is not None:
        entry = history_store.get(show)
        if entry is None:
            print_error(f"No history entry at position {show}")
            raise typer.Exit(1)

        console.print(f"\n[bold cyan]History Entry #{show}[/]")
        console.print(f"  [dim]Time:[/]     {entry.time_str}")
        console.print(f"  [dim]Type:[/]     {entry.command_type}")
        console.print(f"  [dim]Language:[/] {format_language_flag(entry.language)} {entry.language}")
        console.print(f"  [dim]Query:[/]    {entry.query[:200]}")

        print_explanation(
            entry.explanation,
            title=f"Explanation ({entry.command_type})",
            subtitle=entry.time_str,
        )
        return

    # List or search entries
    if search:
        entries = history_store.search(search, limit=limit)
        title = f"Search results for '{search}'"
    else:
        entries = history_store.list_entries(limit=limit, command_type=type_filter)
        title = "Recent Explanations"

    if not entries:
        print_info("No history entries found.")
        if search:
            print_info("Try a different search term or remove the filter.")
        return

    # Build table
    table = Table(title=title, show_lines=False, padding=(0, 1))
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Time", style="dim", width=19)
    table.add_column("Type", style="yellow", width=6)
    table.add_column("Lang", width=4)
    table.add_column("Query", style="white", max_width=60)

    total = history_store.count()
    for i, entry in enumerate(reversed(entries)):
        idx = i + 1
        table.add_row(
            str(idx),
            entry.time_str,
            entry.command_type,
            format_language_flag(entry.language),
            entry.short_query,
        )

    console.print()
    console.print(table)
    console.print(f"\n[dim]Showing {len(entries)} of {total} total entries[/]")
    console.print("[dim]Use --show N to view full details of an entry[/]")
