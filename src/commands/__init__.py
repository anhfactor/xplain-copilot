"""Command modules for xplain CLI."""

from .cmd import cmd
from .error import error_cmd
from .code import code_cmd
from .chat import chat
from .pipe import pipe_cmd, _detect_content_type
from .diff import diff_cmd
from .history import history_cmd
from .wtf import wtf_cmd

__all__ = [
    "cmd", "error_cmd", "code_cmd", "chat",
    "pipe_cmd", "diff_cmd", "history_cmd",
    "wtf_cmd", "_detect_content_type",
]
