from dataclasses import dataclass
from pathlib import Path
import sqlite3
from typing import List


@dataclass
class SavePath:
    id: int | None
    name: str
    description: str


class Config:
    """SQLite-backed storage for SavePath entries.

    This class uses a local sqlite database (by default `savepaths.db` in CWD)
    and provides CRUD operations for `SavePath` rows.
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = Path(db_path) if db_path else Path.cwd() / "savepaths.db"
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS savepaths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT
                )
                """
            )

    def get_all(self) -> List[SavePath]:
        with self._get_conn() as conn:
            cur = conn.execute("SELECT id, name, description FROM savepaths ORDER BY id")
            rows = cur.fetchall()
            return [SavePath(id=row["id"], name=row["name"], description=row["description"]) for row in rows]

    def create(self, name: str, description: str) -> SavePath:
        with self._get_conn() as conn:
            cur = conn.execute("INSERT INTO savepaths (name, description) VALUES (?, ?)", (name, description))
            id = cur.lastrowid
            return SavePath(id=id, name=name, description=description)

    def update(self, sp_id: int, name: str, description: str) -> bool:
        with self._get_conn() as conn:
            cur = conn.execute(
                "UPDATE savepaths SET name = ?, description = ? WHERE id = ?",
                (name, description, sp_id),
            )
            return cur.rowcount > 0

    def delete(self, sp_id: int) -> bool:
        with self._get_conn() as conn:
            cur = conn.execute("DELETE FROM savepaths WHERE id = ?", (sp_id,))
            return cur.rowcount > 0

    def get(self, sp_id: int) -> SavePath | None:
        with self._get_conn() as conn:
            cur = conn.execute("SELECT id, name, description FROM savepaths WHERE id = ?", (sp_id,))
            row = cur.fetchone()
            if row:
                return SavePath(id=row["id"], name=row["name"], description=row["description"]) 
            return None
