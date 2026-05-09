"""管理员后台业务逻辑"""
import os
import json
import bcrypt
from ..database import get_db
from ..config import BASE_DIR, ADMIN_PASSWORD

MAINTENANCE_FILE = os.path.join(BASE_DIR, "maintenance.lock")


def verify_admin(password: str) -> bool:
    return password == ADMIN_PASSWORD


# === 题目管理 ===

def list_questions(type: str = "", chapter: str = "", q_number: str = "", page: int = 1, per: int = 20) -> dict:
    with get_db() as db:
        where = []
        params = []
        if type:
            where.append("type=?")
            params.append(type)
        if chapter:
            where.append("chapter=?")
            params.append(chapter)
        if q_number:
            where.append("q_number LIKE ?")
            params.append(f"%{q_number}%")
        w = " AND ".join(where) if where else "1=1"
        total = db.execute(f"SELECT COUNT(*) FROM questions WHERE {w}", params).fetchone()[0]
        offset = (page - 1) * per
        rows = db.execute(
            f"SELECT * FROM questions WHERE {w} ORDER BY id LIMIT ? OFFSET ?",
            params + [per, offset]
        ).fetchall()
        return {"total": total, "page": page, "per": per, "items": [dict(r) for r in rows]}


def update_question(question_id: int, data: dict) -> dict:
    with get_db() as db:
        allowed = ["q_number", "chapter", "type", "title", "content", "options",
                   "answer", "answer_parts", "template", "answer_code", "note", "is_active"]
        updates = {k: v for k, v in data.items() if k in allowed and v is not None}
        if not updates:
            return {"ok": True}
        sets = ", ".join(f"{k}=?" for k in updates)
        vals = list(updates.values()) + [question_id]
        db.execute(f"UPDATE questions SET {sets} WHERE id=?", vals)
        return {"ok": True}


def create_question(data: dict) -> dict:
    with get_db() as db:
        db.execute(
            "INSERT INTO questions (q_number, chapter, type, title, content, options, "
            "answer, answer_parts, template, answer_code, note, is_active) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,1)",
            (data["q_number"], data["chapter"], data["type"], data.get("title", ""),
             data.get("content", ""), data.get("options"), data.get("answer", ""),
             data.get("answer_parts"), data.get("template"), data.get("answer_code"),
             data.get("note", ""))
        )
        qid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"id": qid}


def toggle_active(question_id: int, active: int) -> dict:
    with get_db() as db:
        db.execute("UPDATE questions SET is_active=? WHERE id=?", (active, question_id))
        return {"ok": True}


# === 用户管理 ===

def list_users(search: str = "", page: int = 1, per: int = 20) -> dict:
    with get_db() as db:
        where = []
        params = []
        if search:
            where.append("(student_id LIKE ? OR name LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        w = " AND ".join(where) if where else "1=1"
        total = db.execute(f"SELECT COUNT(*) FROM users WHERE {w}", params).fetchone()[0]
        offset = (page - 1) * per
        rows = db.execute(
            f"SELECT u.*, "
            f"(SELECT COUNT(DISTINCT question_id) FROM progress WHERE user_id=u.id) AS done_count, "
            f"(SELECT COUNT(DISTINCT question_id) FROM progress WHERE user_id=u.id AND answer_status='correct') AS correct_count "
            f"FROM users u WHERE {w} ORDER BY u.id LIMIT ? OFFSET ?",
            params + [per, offset]
        ).fetchall()
        items = []
        for r in rows:
            d = dict(r)
            d["accuracy"] = round(d["correct_count"] / d["done_count"] * 100, 1) if d["done_count"] else 0
            items.append(d)
        return {"total": total, "page": page, "per": per, "items": items}


def get_user_detail(user_id: int) -> dict:
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            raise ValueError("用户不存在")
        user = dict(row)
        records = db.execute(
            "SELECT p.answer_status, p.mode, p.answered_at, q.q_number, q.type, q.title "
            "FROM progress p JOIN questions q ON p.question_id=q.id "
            "WHERE p.user_id=? ORDER BY p.rowid DESC LIMIT 50",
            (user_id,)
        ).fetchall()
        user["records"] = [dict(r) for r in records]
        return user


def reset_user_pin(user_id: int) -> None:
    with get_db() as db:
        db.execute("UPDATE users SET pin=NULL WHERE id=?", (user_id,))
    from ..auth import bump_token_version
    bump_token_version(user_id)


# === 统计 ===

def get_stats() -> dict:
    with get_db() as db:
        total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_questions = db.execute("SELECT COUNT(*) FROM questions WHERE is_active=1").fetchone()[0]
        total_submissions = db.execute("SELECT COUNT(*) FROM progress").fetchone()[0]
        overall = db.execute(
            "SELECT COUNT(DISTINCT question_id) FROM progress WHERE answer_status='correct'"
        ).fetchone()[0]
        total_done = db.execute(
            "SELECT COUNT(DISTINCT question_id) FROM progress"
        ).fetchone()[0]
        overall_accuracy = round(overall / total_done * 100, 1) if total_done else 0

        # 章节正确率（取每题最新一条记录）
        chapters = db.execute(
            "SELECT q.chapter, COUNT(DISTINCT q.id) AS q_cnt, "
            "COUNT(DISTINCT p.question_id) AS done_cnt, "
            "SUM(CASE WHEN p.answer_status='correct' THEN 1 ELSE 0 END) AS correct_cnt "
            "FROM questions q "
            "LEFT JOIN (SELECT question_id, answer_status FROM progress WHERE rowid IN (SELECT MAX(rowid) FROM progress GROUP BY question_id)) p ON q.id=p.question_id "
            "WHERE q.is_active=1 GROUP BY q.chapter ORDER BY CAST(q.chapter AS INTEGER)"
        ).fetchall()

        chapter_stats = []
        for c in chapters:
            d = dict(c)
            d["accuracy"] = round(d["correct_cnt"] / d["done_cnt"] * 100, 1) if d["done_cnt"] else 0
            chapter_stats.append(d)

        # 题型分布
        type_dist = db.execute(
            "SELECT type, COUNT(*) AS cnt FROM questions WHERE is_active=1 GROUP BY type"
        ).fetchall()

        # TOP10 活跃用户
        top_users = db.execute(
            "SELECT u.student_id, u.name, COUNT(DISTINCT p.question_id) AS done "
            "FROM users u JOIN progress p ON u.id=p.user_id "
            "GROUP BY u.id ORDER BY done DESC LIMIT 10"
        ).fetchall()

        return {
            "total_users": total_users,
            "total_questions": total_questions,
            "total_submissions": total_submissions,
            "overall_accuracy": overall_accuracy,
            "chapter_stats": [dict(c) for c in chapter_stats],
            "type_distribution": [dict(t) for t in type_dist],
            "top_users": [dict(u) for u in top_users],
        }


# === 系统设置 ===

def get_maintenance_status() -> bool:
    return os.path.exists(MAINTENANCE_FILE)


def toggle_maintenance(enable: bool) -> None:
    if enable:
        with open(MAINTENANCE_FILE, "w") as f:
            f.write("1")
    else:
        if os.path.exists(MAINTENANCE_FILE):
            os.remove(MAINTENANCE_FILE)


def change_admin_password(new_password: str) -> None:
    env_file = os.path.join(BASE_DIR, ".env")
    lines = []
    found = False
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("ADMIN_PASSWORD="):
                    lines.append(f"ADMIN_PASSWORD={new_password}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"ADMIN_PASSWORD={new_password}\n")
    with open(env_file, "w") as f:
        f.writelines(lines)
    # 更新运行时变量
    import sys
    mod = sys.modules.get("app.config")
    if mod:
        mod.ADMIN_PASSWORD = new_password


def reload_seed() -> None:
    import subprocess
    import sys
    seed_path = os.path.join(BASE_DIR, "seed", "seed.py")
    subprocess.run([sys.executable, seed_path], cwd=BASE_DIR, check=True)
