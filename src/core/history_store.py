"""JSON-based history storage for xplain CLI."""

import json
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class HistoryEntry:
    """A single history entry."""
    timestamp: float
    command_type: str  # cmd, error, code, diff, pipe, chat
    query: str  # The original input
    explanation: str  # The AI response
    language: str = "en"
    metadata: dict = field(default_factory=dict)

    @property
    def time_str(self) -> str:
        """Human-readable timestamp."""
        from datetime import datetime
        return datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def short_query(self) -> str:
        """Truncated query for display."""
        q = self.query.replace("\n", " ").strip()
        return q[:80] + "..." if len(q) > 80 else q


class HistoryStore:
    """Manages explanation history in a JSON file."""

    MAX_ENTRIES = 500

    def __init__(self, history_dir: Optional[Path] = None):
        if history_dir is None:
            history_dir = Path.home() / ".cache" / "xplain"
        history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = history_dir / "history.json"
        self._entries: Optional[list[HistoryEntry]] = None

    def _load(self) -> list[HistoryEntry]:
        """Load history from disk."""
        if self._entries is not None:
            return self._entries

        if not self.history_file.exists():
            self._entries = []
            return self._entries

        try:
            data = json.loads(self.history_file.read_text())
            self._entries = [HistoryEntry(**entry) for entry in data]
        except (json.JSONDecodeError, TypeError, KeyError):
            self._entries = []

        return self._entries

    def _save(self):
        """Save history to disk."""
        entries = self._load()
        # Trim to max entries
        if len(entries) > self.MAX_ENTRIES:
            entries = entries[-self.MAX_ENTRIES:]
            self._entries = entries

        data = [asdict(e) for e in entries]
        self.history_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def add(
        self,
        command_type: str,
        query: str,
        explanation: str,
        language: str = "en",
        metadata: Optional[dict] = None,
    ):
        """Add a new history entry."""
        entries = self._load()
        entries.append(HistoryEntry(
            timestamp=time.time(),
            command_type=command_type,
            query=query,
            explanation=explanation,
            language=language,
            metadata=metadata or {},
        ))
        self._save()

    def list_entries(
        self,
        limit: int = 20,
        command_type: Optional[str] = None,
    ) -> list[HistoryEntry]:
        """List recent history entries."""
        entries = self._load()
        if command_type:
            entries = [e for e in entries if e.command_type == command_type]
        return entries[-limit:]

    def search(self, query: str, limit: int = 20) -> list[HistoryEntry]:
        """Search history entries by query text."""
        entries = self._load()
        query_lower = query.lower()
        matches = [
            e for e in entries
            if query_lower in e.query.lower() or query_lower in e.explanation.lower()
        ]
        return matches[-limit:]

    def get(self, index: int) -> Optional[HistoryEntry]:
        """Get a specific history entry by index (1-based from recent)."""
        entries = self._load()
        if not entries or index < 1 or index > len(entries):
            return None
        return entries[-index]

    def clear(self):
        """Clear all history."""
        self._entries = []
        self._save()

    def count(self) -> int:
        """Get total number of entries."""
        return len(self._load())


# Global instance
history = HistoryStore()
