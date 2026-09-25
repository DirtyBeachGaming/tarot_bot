"""Per-user preferences and reading history, stored in SQLite next to the limit data."""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

HISTORY_KEEP = 25   # readings kept per user


class UserStore:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db_path)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS prefs (user_id INTEGER PRIMARY KEY, deck TEXT);
            CREATE TABLE IF NOT EXISTS history (
                user_id INTEGER NOT NULL, ts REAL NOT NULL, deck TEXT, spread TEXT,
                question TEXT, cards TEXT);
            CREATE INDEX IF NOT EXISTS idx_hist ON history (user_id, ts);
        """)
        self.db.commit()

    # ----- preferred deck -----
    def get_deck(self, user_id: int) -> str | None:
        row = self.db.execute("SELECT deck FROM prefs WHERE user_id = ?", (user_id,)).fetchone()
        return row[0] if row else None

    def set_deck(self, user_id: int, deck_id: str | None):
        if deck_id is None:
            self.db.execute("DELETE FROM prefs WHERE user_id = ?", (user_id,))
        else:
            self.db.execute("INSERT INTO prefs (user_id, deck) VALUES (?, ?) "
                            "ON CONFLICT(user_id) DO UPDATE SET deck = excluded.deck", (user_id, deck_id))
        self.db.commit()

    # ----- history -----
    def add(self, user_id: int, deck: str, spread: str, question: str | None, cards: list[str]):
        self.db.execute("INSERT INTO history VALUES (?, ?, ?, ?, ?, ?)",
                        (user_id, time.time(), deck, spread, question, json.dumps(cards)))
        # keep only the most recent readings per user
        self.db.execute("""DELETE FROM history WHERE user_id = ? AND ts NOT IN
                           (SELECT ts FROM history WHERE user_id = ? ORDER BY ts DESC LIMIT ?)""",
                        (user_id, user_id, HISTORY_KEEP))
        self.db.commit()

    def recent(self, user_id: int, n: int = 5) -> list[dict]:
        rows = self.db.execute("SELECT ts, deck, spread, question, cards FROM history "
                               "WHERE user_id = ? ORDER BY ts DESC LIMIT ?", (user_id, n)).fetchall()
        return [{"ts": r[0], "deck": r[1], "spread": r[2], "question": r[3], "cards": json.loads(r[4])}
                for r in rows]
