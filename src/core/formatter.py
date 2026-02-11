"""Rich terminal formatting utilities."""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.theme import Theme
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from typing import Optional
import json
from pathlib import Path

# Custom theme for xplain
XPLAIN_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "command": "bold magenta",
    "code": "dim cyan",
    "highlight": "bold yellow",
})

console = Console(theme=XPLAIN_THEME)

# Global output file path (set by --output CLI flag)
_output_file: Optional[str] = None


def set_output_file(path: Optional[str]):
    """Set the global output file path for auto-export."""
    global _output_file
    _output_file = path


def export_explanation(content: str, filepath: str, title: str = "Explanation"):
    """Export explanation content to a file.

    Format is auto-detected from extension: .json, .md, or plain text.
    """
    p = Path(filepath)
    ext = p.suffix.lower()

    if ext == ".json":
        data = {"title": title, "content": content}
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    elif ext in (".md", ".markdown"):
        p.write_text(f"# {title}\n\n{content}\n")
    else:
        # Plain text — strip markdown-ish formatting
        p.write_text(content + "\n")

    console.print(f"\n[dim]Saved to {filepath}[/]")


def print_banner():
    """Print the xplain banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    ██╗  ██╗██████╗ ██╗      █████╗ ██╗███╗   ██╗                ║
║    ╚██╗██╔╝██╔══██╗██║     ██╔══██╗██║████╗  ██║                ║
║     ╚███╔╝ ██████╔╝██║     ███████║██║██╔██╗ ██║                ║
║     ██╔██╗ ██╔══╝  ██║     ██╔══██║██║██║╚██╗██║                ║
║    ██╔╝ ██╗██║     ███████╗██║  ██║██║██║ ╚████║                ║
║    ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝             ║
║                                                                  ║
║         🚀 AI-Powered Code & Command Explainer 🚀               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold cyan")


def print_explanation(
    content: str,
    title: str = "Explanation",
    subtitle: Optional[str] = None,
):
    """
    Print an explanation in a styled panel.
    
    Args:
        content: The explanation content (supports markdown)
        title: Panel title
        subtitle: Optional subtitle
    """
    md = Markdown(content)
    panel = Panel(
        md,
        title=f"[bold cyan]{title}[/]",
        subtitle=f"[dim]{subtitle}[/]" if subtitle else None,
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)

    # Auto-export if output file is set
    if _output_file:
        export_explanation(content, _output_file, title=title)


def print_command(command: str):
    """Print a command with syntax highlighting."""
    console.print()
    console.print(Panel(
        Syntax(command, "bash", theme="monokai", line_numbers=False),
        title="[bold magenta]Command[/]",
        border_style="magenta",
        padding=(0, 2),
    ))


def print_code(code: str, language: str = "python", filename: Optional[str] = None):
    """Print code with syntax highlighting."""
    title = f"[bold green]{filename}[/]" if filename else "[bold green]Code[/]"
    console.print()
    console.print(Panel(
        Syntax(code, language, theme="monokai", line_numbers=True),
        title=title,
        border_style="green",
        padding=(0, 1),
    ))


def print_error(message: str, title: str = "Error"):
    """Print an error message."""
    console.print()
    console.print(Panel(
        Text(message, style="bold red"),
        title=f"[bold red]❌ {title}[/]",
        border_style="red",
        padding=(1, 2),
    ))


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[warning]⚠️  {message}[/]")


def print_success(message: str):
    """Print a success message."""
    console.print(f"[success]✅ {message}[/]")


def print_info(message: str):
    """Print an info message."""
    console.print(f"[info]ℹ️  {message}[/]")


class LoadingSpinner:
    """Context manager for showing a loading spinner."""
    
    def __init__(self, message: str = "Thinking..."):
        self.message = message
        self.live = None
    
    def __enter__(self):
        spinner = Spinner("dots", text=f"[cyan]{self.message}[/]")
        self.live = Live(spinner, console=console, refresh_per_second=10)
        self.live.__enter__()
        return self
    
    def __exit__(self, *args):
        if self.live:
            self.live.__exit__(*args)


def format_language_flag(lang: str) -> str:
    """Get flag emoji for language code."""
    flags = {
        "en": "🇺🇸",
        "vi": "🇻🇳",
        "zh": "🇨🇳",
        "ja": "🇯🇵",
        "ko": "🇰🇷",
        "es": "🇪🇸",
        "fr": "🇫🇷",
        "de": "🇩🇪",
        "pt": "🇧🇷",
        "ru": "🇷🇺",
    }
    return flags.get(lang, "🌐")


def detect_code_language(filename: str) -> str:
    """Detect programming language from filename."""
    extensions = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "jsx",
        ".tsx": "tsx",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "zsh",
        ".fish": "fish",
        ".ps1": "powershell",
        ".sql": "sql",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".sass": "sass",
        ".less": "less",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".xml": "xml",
        ".md": "markdown",
        ".r": "r",
        ".R": "r",
        ".lua": "lua",
        ".vim": "vim",
        ".dockerfile": "dockerfile",
        ".tf": "terraform",
        ".vue": "vue",
        ".svelte": "svelte",
    }
    
    for ext, lang in extensions.items():
        if filename.lower().endswith(ext):
            return lang
    
    # Check for special filenames
    special_files = {
        "Dockerfile": "dockerfile",
        "Makefile": "makefile",
        "CMakeLists.txt": "cmake",
        ".gitignore": "gitignore",
        ".env": "dotenv",
    }
    
    import os
    basename = os.path.basename(filename)
    return special_files.get(basename, "text")
