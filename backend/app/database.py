import os
import sqlite3
from contextlib import contextmanager
from .config import DB_PATH


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            pin TEXT,
            in_roster INTEGER NOT NULL DEFAULT 1,
            prog_mode TEXT,
            sound_on INTEGER NOT NULL DEFAULT 1,
            vibrate_on INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            q_number TEXT UNIQUE NOT NULL,
            chapter TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            options TEXT,
            answer TEXT NOT NULL,
            answer_parts TEXT,
            template TEXT,
            answer_code TEXT,
            note TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            question_id INTEGER NOT NULL REFERENCES questions(id),
            answer_status TEXT NOT NULL,
            user_answer TEXT,
            ai_feedback TEXT,
            mode TEXT NOT NULL,
            prog_submit_type TEXT,
            removed_from_wrong INTEGER NOT NULL DEFAULT 0,
            answered_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE INDEX IF NOT EXISTS idx_progress_user_q
            ON progress(user_id, question_id, answered_at DESC);
    """)
    conn.commit()

    for col, ddl in [
        ("pin_attempts", "ALTER TABLE users ADD COLUMN pin_attempts INTEGER NOT NULL DEFAULT 0"),
        ("pin_locked_until", "ALTER TABLE users ADD COLUMN pin_locked_until TEXT"),
    ]:
        try:
            conn.execute(ddl)
        except sqlite3.OperationalError:
            pass  # column already exists
    conn.commit()

    conn.close()


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
