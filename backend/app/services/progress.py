"""进度业务逻辑"""
from ..database import get_db


def get_progress(user_id: int) -> dict:
    with get_db() as db:
        total = db.execute("SELECT COUNT(*) FROM questions WHERE is_active=1").fetchone()[0]
        done_rows = db.execute(
            "SELECT question_id, answer_status, user_answer FROM progress WHERE rowid IN (SELECT MAX(rowid) FROM progress WHERE user_id=? GROUP BY question_id)",
            (user_id,)
        ).fetchall()
        done = len(done_rows)
        correct = sum(1 for r in done_rows if r["answer_status"] == "correct")
        done_ids = [r["question_id"] for r in done_rows]
        done_map = {r["question_id"]: {"status": r["answer_status"], "user_answer": r["user_answer"]} for r in done_rows}
        if done_ids:
            placeholders = ",".join("?" * len(done_ids))
            next_q = db.execute(
                f"SELECT id FROM questions WHERE is_active=1 AND id NOT IN ({placeholders}) ORDER BY id LIMIT 1",
                done_ids
            ).fetchone()
        else:
            next_q = db.execute("SELECT id FROM questions WHERE is_active=1 ORDER BY id LIMIT 1").fetchone()
        return {
            "total": total,
            "done": done,
            "correct": correct,
            "accuracy": round(correct / done * 100, 1) if done else 0,
            "next_question_id": next_q["id"] if next_q else None,
            "done_map": done_map,
        }


def submit_progress(user_id: int, data: dict) -> dict:
    with get_db() as db:
        db.execute(
            "INSERT INTO progress (user_id, question_id, answer_status, user_answer, mode, prog_submit_type, ai_feedback) VALUES (?,?,?,?,?,?,?)",
            (user_id, data["question_id"], data["answer_status"], data["user_answer"],
             data.get("mode", "sequential"), data.get("prog_submit_type"), data.get("ai_feedback"))
        )
        progress_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": progress_id}


def get_wrong(user_id: int, type: str = "", chapter: str = "", page: int = 1, per: int = 20) -> dict:
    with get_db() as db:
        where = ["p.user_id=? AND p.answer_status IN ('incorrect','partial') AND p.removed_from_wrong=0 AND q.is_active=1"]
        params = [user_id]
        if type:
            where.append("q.type=?")
            params.append(type)
        if chapter:
            where.append("q.chapter=?")
            params.append(chapter)
        w = " AND ".join(where)
        total = db.execute(
            f"SELECT COUNT(DISTINCT p.question_id) FROM progress p JOIN questions q ON p.question_id=q.id WHERE {w}",
            params
        ).fetchone()[0]
        offset = (page - 1) * per
        rows = db.execute(
            f"SELECT DISTINCT p.question_id, q.q_number, q.type, q.title, p.answer_status FROM progress p JOIN questions q ON p.question_id=q.id WHERE {w} ORDER BY q.id LIMIT ? OFFSET ?",
            params + [per, offset]
        ).fetchall()
        return {
            "total": total,
            "page": page,
            "per": per,
            "items": [dict(r) for r in rows],
        }


def remove_from_wrong(user_id: int, question_ids: list[int]) -> None:
    with get_db() as db:
        for qid in question_ids:
            db.execute(
                "UPDATE progress SET removed_from_wrong=1 WHERE user_id=? AND question_id=?",
                (user_id, qid)
            )


def mark_correct(user_id: int, question_id: int) -> None:
    with get_db() as db:
        prev = db.execute(
            "SELECT user_answer, mode, prog_submit_type FROM progress WHERE user_id=? AND question_id=? ORDER BY rowid DESC LIMIT 1",
            (user_id, question_id)
        ).fetchone()
        db.execute(
            "INSERT INTO progress (user_id, question_id, answer_status, user_answer, mode, prog_submit_type) VALUES (?,?,?,?,?,?)",
            (user_id, question_id, "correct", prev["user_answer"] if prev else "[]",
             prev["mode"] if prev else "sequential", prev["prog_submit_type"] if prev else "write")
        )


def clear_progress(user_id: int) -> None:
    with get_db() as db:
        db.execute("DELETE FROM progress WHERE user_id=?", (user_id,))
