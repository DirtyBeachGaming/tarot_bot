"""Per-user daily reading limit (rolling 24 hours), stored in SQLite."""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

WINDOW = 24 * 60 * 60  # seconds


class ReadingLimiter:
    def __init__(self, db_path: Path, limit: int):
        self.limit = limit
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db_path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS readings (user_id INTEGER NOT NULL, ts REAL NOT NULL)"
        )
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_user_ts ON readings (user_id, ts)")
        self.db.commit()

    def _recent(self, user_id: int, now: float) -> list[float]:
        rows = self.db.execute(
            "SELECT ts FROM readings WHERE user_id = ? AND ts > ? ORDER BY ts",
            (user_id, now - WINDOW),
        ).fetchall()
        return [r[0] for r in rows]

    def try_use(self, user_id: int) -> tuple[bool, int, float | None]:
        """Record a reading if allowed.

        Returns (allowed, readings_left_after_this, next_available_unix_time_if_blocked).
        """
        if self.limit <= 0:  # 0 = unlimited
            return True, -1, None
        now = time.time()
        recent = self._recent(user_id, now)
        if len(recent) >= self.limit:
            return False, 0, recent[0] + WINDOW
        self.db.execute("INSERT INTO readings (user_id, ts) VALUES (?, ?)", (user_id, now))
        # tidy up old rows
        self.db.execute("DELETE FROM readings WHERE ts < ?", (now - WINDOW,))
        self.db.commit()
        return True, self.limit - len(recent) - 1, None

    def reset(self, user_id: int):
        self.db.execute("DELETE FROM readings WHERE user_id = ?", (user_id,))
        self.db.commit()
