import os
import sqlite3 as sql
import threading

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATABASE_PATH = os.path.join(REPO_ROOT, "build", "package.db")

SQL_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS package (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            built BOOLEAN DEFAULT 0,
            failed BOOLEAN DEFAULT 0
        );
"""

SQL_ADD_PACKAGE = "INSERT OR IGNORE INTO package (name) VALUES (?)"

SQL_IS_BUILT = "SELECT built FROM package WHERE name = ? LIMIT 1"

SQL_PACKAGE_EXISTS = "SELECT 1 FROM package WHERE name = ? LIMIT 1"

SQL_SET_BUILT = """
UPDATE package SET built = 1, failed = 0 WHERE name = ?
"""

SQL_SET_UNBUILT = "UPDATE package SET built = 0 WHERE name = ?"

SQL_SET_FAILED = """
UPDATE package SET built = 0, failed = 1 WHERE name = ?
"""

SQL_GET_FAILED = "SELECT * FROM package WHERE failed = 1"


class PackageDatabase(object):
    """SQLite build state, shared by the CLI across worker threads.

    The database lives under build/ (ignored by git) instead of the current
    directory, and all statements are parameterized.
    """

    def __init__(self, path=None, create=True):
        self._path = path or DEFAULT_DATABASE_PATH
        self._lock = threading.RLock()
        if create:
            directory = os.path.dirname(self._path)
            if directory:
                os.makedirs(directory, exist_ok=True)
        elif not os.path.isfile(self._path):
            raise FileNotFoundError(self._path)

        self._connection = sql.connect(
            self._path, check_same_thread=False, timeout=10)
        self._connection.execute("PRAGMA busy_timeout = 10000")
        if create:
            with self._lock:
                self._connection.execute(SQL_CREATE_TABLES)
                self._connection.commit()

    @classmethod
    def read_only(cls, path=None):
        """Open an existing database without ever creating or modifying it."""
        db = cls.__new__(cls)
        db._path = path or DEFAULT_DATABASE_PATH
        db._lock = threading.RLock()
        if not os.path.isfile(db._path):
            raise FileNotFoundError(db._path)
        db._connection = sql.connect(
            "file:{}?mode=ro".format(db._path), uri=True,
            check_same_thread=False, timeout=10)
        return db

    def close(self):
        with self._lock:
            self._connection.close()

    def add_package(self, name):
        with self._lock:
            cur = self._connection.execute(SQL_ADD_PACKAGE, (name,))
            self._connection.commit()
            return cur.rowcount > 0

    def has_package(self, name):
        with self._lock:
            row = self._connection.execute(
                SQL_PACKAGE_EXISTS, (name,)).fetchone()
        return row is not None

    def is_built(self, name):
        with self._lock:
            row = self._connection.execute(SQL_IS_BUILT, (name,)).fetchone()
        return bool(row and row[0] == 1)

    def set_built(self, name):
        with self._lock:
            self._connection.execute(SQL_SET_BUILT, (name,))
            self._connection.commit()

    def set_unbuilt(self, name):
        with self._lock:
            self._connection.execute(SQL_SET_UNBUILT, (name,))
            self._connection.commit()

    def set_failed(self, name):
        with self._lock:
            self._connection.execute(SQL_SET_FAILED, (name,))
            self._connection.commit()

    def get_failed(self):
        with self._lock:
            return self._connection.execute(SQL_GET_FAILED).fetchall()
