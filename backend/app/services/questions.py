"""题库查询"""
from ..database import get_db


def list_questions(type: str = "", chapter: str = "", ids: str = "", page: int = 1, per: int = 20) -> dict:
    with get_db() as db:
        where = ["is_active=1"]
        params = []
        if ids:
            id_list = [int(x.strip()) for x in ids.split(",") if x.strip().isdigit()]
            if id_list:
                placeholders = ",".join("?" * len(id_list))
                where.append(f"id IN ({placeholders})")
                params.extend(id_list)
        if type:
            type_list = [t.strip() for t in type.split(",") if t.strip()]
            if type_list:
                placeholders = ",".join("?" * len(type_list))
                where.append(f"type IN ({placeholders})")
                params.extend(type_list)
        if chapter:
            where.append("chapter=?")
            params.append(chapter)
        w = " AND ".join(where)
        total = db.execute(f"SELECT COUNT(*) FROM questions WHERE {w}", params).fetchone()[0]
        offset = (page - 1) * per
        rows = db.execute(
            f"SELECT id, q_number, chapter, type, title FROM questions WHERE {w} ORDER BY id LIMIT ? OFFSET ?",
            params + [per, offset]
        ).fetchall()
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
    with get_db() as db:
        row = db.execute("SELECT * FROM questions WHERE id=? AND is_active=1", (question_id,)).fetchone()
        if not row:
            raise ValueError("题目不存在")
        return dict(row)
