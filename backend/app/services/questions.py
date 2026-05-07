"""题库查询"""
from ..database import get_conn


def list_questions(type: str = "", chapter: str = "", page: int = 1, per: int = 20) -> dict:
    conn = get_conn()
    where = ["is_active=1"]
    params = []
    if type:
        where.append("type=?")
        params.append(type)
    if chapter:
        where.append("chapter=?")
        params.append(chapter)
    w = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM questions WHERE {w}", params).fetchone()[0]
    offset = (page - 1) * per
    rows = conn.execute(
        f"SELECT id, q_number, chapter, type, title FROM questions WHERE {w} ORDER BY id LIMIT ? OFFSET ?",
        params + [per, offset]
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "page": page,
        "per": per,
        "items": [
            {
                "id": r["id"],
                "q_number": r["q_number"],
                "chapter": r["chapter"],
                "type": r["type"],
                "title": r["title"],
            }
            for r in rows
        ],
    }


def get_question(question_id: int) -> dict:
    conn = get_conn()
    row = conn.execute("SELECT * FROM questions WHERE id=? AND is_active=1", (question_id,)).fetchone()
    conn.close()
    if not row:
        raise ValueError("题目不存在")
    return dict(row)
