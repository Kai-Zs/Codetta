"""AI 知识点解析服务"""
import os
import threading
import httpx
from ..database import get_db
from ..config import DEEPSEEK_API_KEY, DEEPSEEK_TIMEOUT, BASE_DIR

KP_DB_PATH = os.path.join(BASE_DIR, "data", "ai_kp.db")
_locks = {}
_locks_lock = threading.Lock()


def get_kp_conn():
    import sqlite3
    conn = sqlite3.connect(KP_DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


def get_kp_db():
    conn = get_kp_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_kp_db():
    with get_kp_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS kp_cache (
                question_id INTEGER PRIMARY KEY,
                analysis_md  TEXT NOT NULL,
                created_at   TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            );
            CREATE TABLE IF NOT EXISTS kp_access (
                student_id TEXT PRIMARY KEY,
                enabled    INTEGER NOT NULL DEFAULT 1
            );
            INSERT OR IGNORE INTO kp_access (student_id, enabled) VALUES ('2025006708', 1);
        """)


def check_kp_access(user_id: int) -> bool:
    with get_db() as db:
        row = db.execute("SELECT student_id FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            return False
        student_id = row["student_id"]
    with get_kp_db() as kdb:
        r = kdb.execute(
            "SELECT enabled FROM kp_access WHERE student_id=?", (student_id,)
        ).fetchone()
        return r is not None and r["enabled"] == 1


KP_PROMPT = """你是一个 Python 知识点分析助手。请根据以下题目信息，提炼涉及的知识点，
简要介绍，并指出重点难点和易错点。

【题号】{q_number}
【章节】{chapter}
【题型】{type}
【题目】{content}
{answer_block}
{options_block}
{note_block}
请自由组织输出结构，使用 markdown 格式，可包含代码示例和公式。"""

CHAT_PROMPT = """你是一个 Python 学习助教。以下是一道题目的信息和 AI 已给出的知识点解析，
请根据用户的追问继续解答。

【题目信息】
题号：{q_number} | 章节：{chapter} | 题型：{type}
题目：{content}
答案：{answer}

【知识点解析】
{analysis_md}

请结合以上上下文回答用户的问题。"""


def _build_analyze_messages(question: dict) -> list[dict]:
    q_type = question["type"]
    if q_type == "编程题":
        answer_text = question.get("answer_code") or question.get("answer") or ""
    elif question.get("answer_parts"):
        answer_text = question["answer_parts"]
    else:
        answer_text = question.get("answer") or ""

    answer_block = f"【答案】\n{answer_text}" if answer_text else ""
    options_block = f"【选项】\n{question['options']}" if question.get("options") else ""
    note_block = f"【解析/备注】\n{question['note']}" if question.get("note") else ""

    prompt = KP_PROMPT.format(
        q_number=question["q_number"],
        chapter=question["chapter"],
        type=question["type"],
        content=question.get("content") or question.get("title", ""),
        answer_block=answer_block,
        options_block=options_block,
        note_block=note_block,
    )
    return [{"role": "user", "content": prompt}]


def get_cached_analysis(question_id: int) -> str | None:
    with get_kp_db() as db:
        row = db.execute(
            "SELECT analysis_md FROM kp_cache WHERE question_id=?", (question_id,)
        ).fetchone()
        return row["analysis_md"] if row else None


def save_analysis(question_id: int, analysis_md: str):
    with get_kp_db() as db:
        db.execute(
            "INSERT OR REPLACE INTO kp_cache (question_id, analysis_md, created_at) "
            "VALUES (?,?,datetime('now','localtime'))",
            (question_id, analysis_md),
        )


def _call_deepseek(messages: list[dict]) -> str:
    with httpx.Client(timeout=DEEPSEEK_TIMEOUT) as client:
        resp = client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-v4-flash",
                "messages": messages,
                "temperature": 0.7,
            },
        )
    if resp.status_code != 200:
        raise ValueError(f"DeepSeek API 错误: {resp.status_code}")
    try:
        return resp.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise ValueError("DeepSeek 返回格式异常")


def analyze_kp(question_id: int, force: bool = False) -> dict:
    if not force:
        cached = get_cached_analysis(question_id)
        if cached is not None:
            return {"analysis_md": cached, "cached": True}

    with get_db() as db:
        row = db.execute(
            "SELECT * FROM questions WHERE id=? AND is_active=1", (question_id,)
        ).fetchone()
        if not row:
            raise ValueError("题目不存在")

    with _locks_lock:
        lock = _locks.setdefault(question_id, threading.Lock())

    with lock:
        if not force:
            cached = get_cached_analysis(question_id)
            if cached is not None:
                return {"analysis_md": cached, "cached": True}

        messages = _build_analyze_messages(dict(row))
        analysis_md = _call_deepseek(messages)
        save_analysis(question_id, analysis_md)
        try:
            del _locks[question_id]
        except KeyError:
            pass
        return {"analysis_md": analysis_md, "cached": False}


def chat_followup(question_id: int, messages: list[dict]) -> str:
    MAX_ROUNDS = 20
    MAX_CHARS = 8000
    MIN_KEEP = 3

    with get_db() as db:
        row = db.execute(
            "SELECT * FROM questions WHERE id=? AND is_active=1", (question_id,)
        ).fetchone()
        if not row:
            raise ValueError("题目不存在")

    q = dict(row)
    q_type = q["type"]
    if q_type == "编程题":
        answer_text = q.get("answer_code") or q.get("answer") or ""
    elif q.get("answer_parts"):
        answer_text = q["answer_parts"]
    else:
        answer_text = q.get("answer") or ""

    analysis_md = get_cached_analysis(question_id) or ""
    system_msg = {
        "role": "system",
        "content": CHAT_PROMPT.format(
            q_number=q["q_number"],
            chapter=q["chapter"],
            type=q["type"],
            content=q.get("content") or q.get("title", ""),
            answer=answer_text,
            analysis_md=analysis_md,
        ),
    }

    all_msgs = [system_msg] + list(messages)

    if len(all_msgs) > 1 + MAX_ROUNDS * 2:
        keep = messages[-(MAX_ROUNDS - 5) * 2:]
        all_msgs = [system_msg] + keep

    total_chars = sum(len(m.get("content", "")) for m in all_msgs)
    while total_chars > MAX_CHARS and len(all_msgs) > 1 + MIN_KEEP * 2:
        all_msgs.pop(1)
        total_chars = sum(len(m.get("content", "")) for m in all_msgs)

    return _call_deepseek(all_msgs)
