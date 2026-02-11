"""Tests for xplain CLI."""

import json
import tempfile
from pathlib import Path
from typer.testing import CliRunner
from src.cli import app
from src.config import LANGUAGE_NAMES, config

runner = CliRunner()


class TestCLI:
    """Test CLI commands."""

    def test_version(self):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "xplain" in result.stdout

    def test_langs(self):
        """Test langs command."""
        result = runner.invoke(app, ["langs"])
        assert result.exit_code == 0
        for lang_code in LANGUAGE_NAMES:
            assert lang_code in result.stdout

    def test_config_show(self):
        """Test config --show command."""
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Configuration" in result.stdout

    def test_help(self):
        """Test help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "cmd" in result.stdout
        assert "error" in result.stdout
        assert "code" in result.stdout
        assert "chat" in result.stdout
        assert "pipe" in result.stdout
        assert "diff" in result.stdout
        assert "history" in result.stdout


class TestConfig:
    """Test configuration."""

    def test_default_language(self):
        """Test default language is set."""
        assert config.language in LANGUAGE_NAMES

    def test_language_names(self):
        """Test all language codes have names."""
        assert len(LANGUAGE_NAMES) >= 10
        for code, name in LANGUAGE_NAMES.items():
            assert len(code) == 2
            assert len(name) > 0


class TestFormatter:
    """Test formatter utilities."""

    def test_detect_code_language(self):
        """Test programming language detection."""
        from src.core.formatter import detect_code_language

        assert detect_code_language("test.py") == "python"
        assert detect_code_language("app.js") == "javascript"
        assert detect_code_language("main.go") == "go"
        assert detect_code_language("Dockerfile") == "dockerfile"
        assert detect_code_language("unknown.xyz") == "text"

    def test_format_language_flag(self):
        """Test language flag formatting."""
        from src.core.formatter import format_language_flag

        assert format_language_flag("en") == "🇺🇸"
        assert format_language_flag("vi") == "🇻🇳"
        assert format_language_flag("unknown") == "🌐"


class TestHistoryStore:
    """Test history storage."""

    def test_add_and_list(self):
        """Test adding and listing history entries."""
        from src.core.history_store import HistoryStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = HistoryStore(history_dir=Path(tmpdir))
            store.add("cmd", "ls -la", "Lists files in detail", language="en")
            store.add("error", "TypeError", "Type mismatch", language="vi")

            entries = store.list_entries()
            assert len(entries) == 2
            assert entries[0].command_type == "cmd"
            assert entries[1].command_type == "error"

    def test_search(self):
        """Test searching history."""
        from src.core.history_store import HistoryStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = HistoryStore(history_dir=Path(tmpdir))
            store.add("cmd", "docker run nginx", "Runs nginx container")
            store.add("cmd", "git push origin main", "Pushes to main")
            store.add("error", "docker: command not found", "Docker not installed")

            results = store.search("docker")
            assert len(results) == 2

    def test_clear(self):
        """Test clearing history."""
        from src.core.history_store import HistoryStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = HistoryStore(history_dir=Path(tmpdir))
            store.add("cmd", "test", "test explanation")
            assert store.count() == 1
            store.clear()
            assert store.count() == 0

    def test_get_by_index(self):
        """Test getting entry by index (1-based from recent)."""
        from src.core.history_store import HistoryStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = HistoryStore(history_dir=Path(tmpdir))
            store.add("cmd", "first", "first explanation")
            store.add("cmd", "second", "second explanation")
            store.add("cmd", "third", "third explanation")

            # Index 1 = most recent
            entry = store.get(1)
            assert entry.query == "third"

            entry = store.get(3)
            assert entry.query == "first"

            assert store.get(0) is None
            assert store.get(4) is None


class TestPipeDetection:
    """Test pipe content type detection."""

    def test_detect_error(self):
        """Test error detection in piped content."""
        from src.commands.pipe import _detect_content_type

        content = """Traceback (most recent call last):
  File "app.py", line 10, in <module>
    result = process(data)
TypeError: 'NoneType' object is not subscriptable"""
        assert _detect_content_type(content) == "error"

    def test_detect_code(self):
        """Test code detection in piped content."""
        from src.commands.pipe import _detect_content_type

        content = """import os
from pathlib import Path

def process_files(directory):
    for f in Path(directory).glob('*.py'):
        print(f.name)
"""
        assert _detect_content_type(content) == "code"

    def test_detect_auto(self):
        """Test auto detection for general output."""
        from src.commands.pipe import _detect_content_type

        content = """total 48
drwxr-xr-x  12 user  staff   384 Feb 10 10:00 .
drwxr-xr-x   5 user  staff   160 Feb  9 09:00 ..
-rw-r--r--   1 user  staff  1234 Feb 10 10:00 README.md"""
        assert _detect_content_type(content) == "auto"

    def test_detect_empty(self):
        """Test empty content detection."""
        from src.commands.pipe import _detect_content_type

        assert _detect_content_type("") == "unknown"


class TestBackends:
    """Test AI backend selection."""

    def test_backend_classes_exist(self):
        """Test that backend classes are importable."""
        from src.core.copilot import GhModelsBackend, HttpxModelsBackend, AIBackend

        assert issubclass(GhModelsBackend, AIBackend)
        assert issubclass(HttpxModelsBackend, AIBackend)

    def test_gh_models_backend_name(self):
        """Test GhModelsBackend name."""
        from src.core.copilot import GhModelsBackend

        backend = GhModelsBackend()
        assert "GitHub Models" in backend.name

    def test_httpx_models_backend_name(self):
        """Test HttpxModelsBackend name."""
        from src.core.copilot import HttpxModelsBackend

        backend = HttpxModelsBackend()
        assert "GitHub Models" in backend.name

    def test_consolidated_backend(self):
        """Test that GhModelsBackend and HttpxModelsBackend are the same class."""
        from src.core.copilot import GhModelsBackend, HttpxModelsBackend, GitHubModelsBackend

        assert GhModelsBackend is GitHubModelsBackend
        assert HttpxModelsBackend is GitHubModelsBackend

    def test_ask_messages_method_exists(self):
        """Test that ask_messages method exists on backend."""
        from src.core.copilot import GitHubModelsBackend

        backend = GitHubModelsBackend()
        assert hasattr(backend, "ask_messages")
        assert callable(backend.ask_messages)


class TestExport:
    """Test output export functionality."""

    def test_export_markdown(self):
        """Test exporting to markdown file."""
        from src.core.formatter import export_explanation

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = str(Path(tmpdir) / "test.md")
            export_explanation("Hello **world**", filepath, title="Test")
            content = Path(filepath).read_text()
            assert "# Test" in content
            assert "Hello **world**" in content

    def test_export_json(self):
        """Test exporting to JSON file."""
        from src.core.formatter import export_explanation

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = str(Path(tmpdir) / "test.json")
            export_explanation("Hello world", filepath, title="Test")
            data = json.loads(Path(filepath).read_text())
            assert data["title"] == "Test"
            assert data["content"] == "Hello world"

    def test_export_text(self):
        """Test exporting to plain text file."""
        from src.core.formatter import export_explanation

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = str(Path(tmpdir) / "test.txt")
            export_explanation("Hello world", filepath, title="Test")
            content = Path(filepath).read_text()
            assert content.strip() == "Hello world"

    def test_set_output_file(self):
        """Test set_output_file sets the global."""
        from src.core.formatter import set_output_file
        import src.core.formatter as fmt

        set_output_file("/tmp/test.md")
        assert fmt._output_file == "/tmp/test.md"
        set_output_file(None)
        assert fmt._output_file is None


class TestCLIGlobalOptions:
    """Test global CLI options."""

    def test_help_shows_output_flag(self):
        """Test that --output flag appears in help."""
        result = runner.invoke(app, ["--help"])
        assert "--output" in result.stdout

    def test_help_shows_no_color_flag(self):
        """Test that --no-color flag appears in help."""
        result = runner.invoke(app, ["--help"])
        assert "--no-color" in result.stdout

    def test_help_shows_model_flag(self):
        """Test that --model flag appears in help."""
        result = runner.invoke(app, ["--help"])
        assert "--model" in result.stdout


class TestModelSelection:
    """Test AI model selection."""

    def test_models_command(self):
        """Test models command lists available models."""
        result = runner.invoke(app, ["models"])
        assert result.exit_code == 0
        assert "openai/gpt-4o-mini" in result.stdout
        assert "openai/gpt-4.1" in result.stdout

    def test_available_models_dict(self):
        """Test AVAILABLE_MODELS has entries."""
        from src.config import AVAILABLE_MODELS, DEFAULT_MODEL

        assert len(AVAILABLE_MODELS) >= 5
        assert DEFAULT_MODEL in AVAILABLE_MODELS

    def test_config_has_model(self):
        """Test config has model attribute."""
        assert hasattr(config, "model")
        assert config.model == "openai/gpt-4o-mini"  # default

    def test_set_model(self):
        """Test set_model changes the selected model."""
        from src.core.copilot import set_model
        import src.core.copilot as copilot_mod

        set_model("openai/gpt-4.1")
        assert copilot_mod._selected_model == "openai/gpt-4.1"
        # Reset
        set_model(None)
        copilot_mod._selected_model = None

    def test_backend_uses_model(self):
        """Test GitHubModelsBackend accepts model parameter."""
        from src.core.copilot import GitHubModelsBackend

        backend = GitHubModelsBackend(model="openai/gpt-4.1")
        assert backend.model == "openai/gpt-4.1"
        assert "gpt-4.1" in backend.name


class TestWTFCommand:
    """Test WTF command utilities."""

    def test_wtf_help(self):
        """Test wtf command appears in help."""
        result = runner.invoke(app, ["wtf", "--help"])
        assert result.exit_code == 0
        assert "last failed command" in result.stdout.lower() or "shell history" in result.stdout.lower()

    def test_wtf_registered(self):
        """Test wtf command is registered."""
        result = runner.invoke(app, ["--help"])
        assert "wtf" in result.stdout

    def test_get_last_command_zsh(self):
        """Test zsh history parsing."""
        from src.commands.wtf import _get_last_command_zsh
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode="w", suffix=".zsh_history", delete=False) as f:
            f.write(": 1707600000:0;echo hello\n")
            f.write(": 1707600001:0;git push origin main\n")
            tmppath = f.name

        old_histfile = os.environ.get("HISTFILE")
        try:
            os.environ["HISTFILE"] = tmppath
            cmd = _get_last_command_zsh()
            assert cmd == "git push origin main"
        finally:
            if old_histfile:
                os.environ["HISTFILE"] = old_histfile
            elif "HISTFILE" in os.environ:
                del os.environ["HISTFILE"]
            os.unlink(tmppath)

    def test_get_last_command_bash(self):
        """Test bash history parsing."""
        from src.commands.wtf import _get_last_command_bash
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode="w", suffix=".bash_history", delete=False) as f:
            f.write("echo hello\n")
            f.write("npm run build\n")
            tmppath = f.name

        old_histfile = os.environ.get("HISTFILE")
        try:
            os.environ["HISTFILE"] = tmppath
            cmd = _get_last_command_bash()
            assert cmd == "npm run build"
        finally:
            if old_histfile:
                os.environ["HISTFILE"] = old_histfile
            elif "HISTFILE" in os.environ:
                del os.environ["HISTFILE"]
            os.unlink(tmppath)


class TestTLDRMode:
    """Test TL;DR mode."""

    def test_tldr_flag_in_help(self):
        """Test --tldr flag appears in help."""
        result = runner.invoke(app, ["--help"])
        assert "--tldr" in result.stdout

    def test_set_tldr_mode(self):
        """Test set_tldr_mode toggles the flag."""
        from src.core.copilot import set_tldr_mode, is_tldr_mode
        import src.core.copilot as copilot_mod

        set_tldr_mode(True)
        assert is_tldr_mode() is True
        assert copilot_mod._tldr_mode is True

        set_tldr_mode(False)
        assert is_tldr_mode() is False
        assert copilot_mod._tldr_mode is False

    def test_tldr_system_prompt_exists(self):
        """Test SYSTEM_PROMPT_TLDR is defined and different from SYSTEM_PROMPT."""
        from src.core.copilot import SYSTEM_PROMPT, SYSTEM_PROMPT_TLDR

        assert SYSTEM_PROMPT_TLDR != SYSTEM_PROMPT
        assert "single" in SYSTEM_PROMPT_TLDR.lower() or "one" in SYSTEM_PROMPT_TLDR.lower()


class TestShellIntegration:
    """Test shell integration files exist and are valid."""

    def test_zsh_integration_exists(self):
        """Test zsh integration file exists."""
        from pathlib import Path
        zsh_file = Path(__file__).parent.parent / "shell" / "xplain.zsh"
        assert zsh_file.exists()
        content = zsh_file.read_text()
        assert "alias wtf" in content
        assert "xplain wtf" in content

    def test_bash_integration_exists(self):
        """Test bash integration file exists."""
        from pathlib import Path
        bash_file = Path(__file__).parent.parent / "shell" / "xplain.bash"
        assert bash_file.exists()
        content = bash_file.read_text()
        assert "alias wtf" in content
        assert "xplain wtf" in content
