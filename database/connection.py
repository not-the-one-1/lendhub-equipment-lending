import sqlite3
from contextlib import contextmanager
from pathlib import Path
from config.settings import DB_PATH

class Database:
    def __init__(self, path=DB_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        conn = sqlite3.connect(self.path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('PRAGMA busy_timeout = 15000')
        return conn

    @contextmanager
    def transaction(self):
        conn = self.connect()
        try:
            # Acquire the writer lock before checking stock and limits.
            conn.execute('BEGIN IMMEDIATE')
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @contextmanager
    def read(self):
        conn = self.connect()
        try:
            yield conn
        finally:
            conn.close()

    def initialize(self):
        with self.read() as conn:
            conn.executescript(Path(__file__).with_name('schema.sql').read_text(encoding='utf-8'))

def connect_db():
    return Database().connect()
