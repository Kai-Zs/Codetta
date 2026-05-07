"""错题导出 Excel"""
import io
import openpyxl
from ..database import get_db


def export_wrong(user_id: int) -> bytes:
    with get_db() as db:
        rows = db.execute(
            "SELECT DISTINCT q.q_number, q.type, q.title, q.content, p.answer_status "
            "FROM progress p JOIN questions q ON p.question_id=q.id "
            "WHERE p.user_id=? AND p.answer_status IN ('incorrect','partial') AND p.removed_from_wrong=0 "
            "ORDER BY q.id",
            (user_id,)
        ).fetchall()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["题号", "题型", "标题", "题目", "作答状态"])
        for r in rows:
            ws.append([r["q_number"], r["type"], r["title"], r["content"], r["answer_status"]])

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.read()
