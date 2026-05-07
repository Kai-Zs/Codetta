"""进度业务逻辑"""
from ..database import get_conn


def get_progress(user_id: int) -> dict:
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM questions WHERE is_active=1").fetchone()[0]
    done_rows = conn.execute(
        "SELECT question_id, answer_status FROM progress WHERE user_id=? GROUP BY question_id HAVING MAX(rowid)",
        (user_id,)
    ).fetchall()
    done = len(done_rows)
    correct = sum(1 for r in done_rows if r["answer_status"] == "correct")
    done_ids = [r["question_id"] for r in done_rows]
    if done_ids:
        placeholders = ",".join("?" * len(done_ids))
        next_q = conn.execute(
            f"SELECT id FROM questions WHERE is_active=1 AND id NOT IN ({placeholders}) ORDER BY id LIMIT 1",
            done_ids
        ).fetchone()
    else:
        next_q = conn.execute("SELECT id FROM questions WHERE is_active=1 ORDER BY id LIMIT 1").fetchone()
    conn.close()
    return {
        "total": total,
        "done": done,
        "correct": correct,
        "accuracy": round(correct / done * 100, 1) if done else 0,
        "next_question_id": next_q["id"] if next_q else None,
    }


def submit_progress(user_id: int, data: dict) -> dict:
    conn = get_conn()
    conn.execute(
        "INSERT INTO progress (user_id, question_id, answer_status, user_answer, mode, prog_submit_type) VALUES (?,?,?,?,?,?)",
        (user_id, data["question_id"], data["answer_status"], data["user_answer"],
         data.get("mode", "sequential"), data.get("prog_submit_type"))
    )
    conn.commit()
    progress_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return {"id": progress_id}


def get_wrong(user_id: int, type: str = "", chapter: str = "", page: int = 1, per: int = 20) -> dict:
    conn = get_conn()
    where = ["p.user_id=? AND p.answer_status IN ('incorrect','partial') AND p.removed_from_wrong=0"]
    params = [user_id]
    if type:
        where.append("q.type=?")
        params.append(type)
    if chapter:
        where.append("q.chapter=?")
        params.append(chapter)
    w = " AND ".join(where)
    total = conn.execute(
        f"SELECT COUNT(DISTINCT p.question_id) FROM progress p JOIN questions q ON p.question_id=q.id WHERE {w}",
        params
    ).fetchone()[0]
    offset = (page - 1) * per
    rows = conn.execute(
        f"SELECT DISTINCT p.question_id, q.q_number, q.type, q.title, p.answer_status FROM progress p JOIN questions q ON p.question_id=q.id WHERE {w} ORDER BY q.id LIMIT ? OFFSET ?",
        params + [per, offset]
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "page": page,
        "per": per,
        "items": [dict(r) for r in rows],
    }


def remove_from_wrong(user_id: int, question_ids: list[int]) -> None:
    conn = get_conn()
    for qid in question_ids:
        conn.execute(
            "UPDATE progress SET removed_from_wrong=1 WHERE user_id=? AND question_id=?",
            (user_id, qid)
        )
    conn.commit()
    conn.close()


def clear_progress(user_id: int) -> None:
    conn = get_conn()
    conn.execute("DELETE FROM progress WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
