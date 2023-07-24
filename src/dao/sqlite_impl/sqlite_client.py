import dataclasses
import json
import logging
import sqlite3
import threading
from typing import List, Any

from src.features.logging_supplier import get_logger


@dataclasses.dataclass
class SqliteQuery:
    sql: str
    args: List[Any] = dataclasses.field(default_factory=list)

    def __init__(self, sql: str, *args: str):
        self.sql = sql
        self.args = list(args)

    def __str__(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    def __repr__(self) -> str:
        return str(self)


class SqliteClient:
    _conn: sqlite3.Connection
    _cursor: sqlite3.Cursor
    _lock: threading.Lock
    _logger: logging.Logger = get_logger("sqlite3")

    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = lambda cursor, row: {
            col[0]: row[idx] for idx, col in enumerate(cursor.description)
        }
        self._cursor = self._conn.cursor()
        self._lock = threading.Lock()
        self._cursor.execute("PRAGMA foreign_keys = ON;")

    def __del__(self):
        self._conn.close()

    def commit(self):
        self._conn.commit()

    def execute(self, *queries: SqliteQuery, dump=True):
        with self._lock:
            self._logger.debug(f"SQL: {queries}")
            results = [
                self._cursor.execute(query.sql, query.args).fetchall()
                for query in queries
            ]
            if dump:
                self.commit()
            return results

    def batch_insert(self, query: SqliteQuery):
        with self._lock:
            self._logger.debug(f"SQL: {query}")
            result = self._cursor.executemany(query.sql, query.args).fetchall()
            self.commit()
            return result
