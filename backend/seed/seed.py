"""
将 题库(622道).xlsx 和 2544名单.xlsx 导入 SQLite 数据库。
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl
from app.database import get_db, init_db

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXCEL_QA = os.path.join(ROOT, "题库(622道).xlsx")
EXCEL_ROSTER = os.path.join(ROOT, "2544名单.xlsx")
HTML_PROG = os.path.join(ROOT, "编程题抽出来的题库.htm")


def load_workbook_safe(path):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    header = [str(h) if h else "" for h in rows[0]]
    data = []
    for row in rows[1:]:
        d = {header[i]: (str(row[i]) if row[i] is not None else "") for i in range(len(header))}
        data.append(d)
    return data


def clean_dollar(val):
    if not isinstance(val, str):
        return val
    val = val.replace("‘$’", "‘’")  # '$'w' -> 'w'
    val = re.sub(r"'?\$'?w\+'?", "'w+'", val)
    val = val.replace("'True$False'", "True or False")
    val = re.sub(r"'?\$-inf'?", "-inf", val)
    val = re.sub(r"'?\+inf\$'?", "+inf", val)
    val = re.sub(r"'?\$([.,;:，。；：])'?", r"\1", val)
    val = val.replace("$\n", "\n")
    val = val.replace("\n$", "\n")
    val = re.sub(r"'?\$'?$", "", val)
    val = re.sub(r"^'?\$'?", "", val)
    val = re.sub(r"\$\$+", "", val)
    val = val.strip()
    return val


def parse_prog_html(path):
    """解析编程题 HTML：font10 color=red → 答案，黑色 → 模板"""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        html = f.read()
    prog_map = {}
    blocks = re.findall(
        r'<p class="MsoNormal"><b><span[^>]*>(\d+\.\d+)</span></b></p>(.*?)(?=<p class="MsoNormal"><b><span|$)',
        html, re.DOTALL
    )
    for num, body in blocks:
        template_parts = []
        answer_parts = []
        for seg in re.split(r'(<font class="font10"[^>]*>.*?</font>)', body):
            m = re.match(r'<font class="font10"[^>]*>(.*?)</font>', seg)
            if m:
                is_red = 'color:red' in seg[:seg.index('>')] if '>' in seg else False
                if is_red:
                    answer_parts.append(m.group(1))
                else:
                    template_parts.append(m.group(1))
            else:
                template_parts.append(seg)
        prog_map[num] = {
            "template": "".join(template_parts).strip(),
            "answer_code": "".join(answer_parts).strip(),
        }
    return prog_map


def seed_questions(db):
    prog_map = parse_prog_html(HTML_PROG)
    data = load_workbook_safe(EXCEL_QA)
    skipped = []

    for row in data:
        q_number = clean_dollar(row.get("原题号", ""))
        chapter = clean_dollar(row.get("章节号", ""))
        qtype = clean_dollar(row.get("题型", ""))
        title = clean_dollar(row.get("标题", ""))
        content = clean_dollar(row.get("内容", ""))
        raw_answer = clean_dollar(row.get("答案栏", ""))
        note = clean_dollar(row.get("备注", ""))
        options = None
        answer_parts = None
        template = None
        answer_code = None

        if qtype == "单选":
            options = parse_single_choice_options(content)
            if options:
                answer_letter = None
                for opt in options:
                    opt_text = opt.split(".", 1)[-1].strip() if "." in opt else opt
                    ans_text = raw_answer.strip()
                    if ans_text == opt_text or ans_text.strip("'\"") == opt_text.strip("'\""):
                        answer_letter = opt.split(".")[0].split("、")[0].strip()
                        break
                if answer_letter:
                    raw_answer = answer_letter
                else:
                    skipped.append(f"{q_number}: 单选答案无法匹配选项 [{raw_answer}]")

        elif qtype == "判断":
            raw_answer = clean_dollar(row.get("答案栏", "")).strip()
            if raw_answer not in ("正确", "错误"):
                skipped.append(f"{q_number}: 判断题答案异常 [{raw_answer}]")

        elif qtype == "填空":
            cleaned = raw_answer
            answer_parts_list = [p.strip() for p in cleaned.split("$") if p.strip()]
            if answer_parts_list:
                if cleaned.count("$") + 1 != len(answer_parts_list):
                    skipped.append(f"{q_number}: 填空答案 $ 数量与空数不匹配")
                answer_parts = json.dumps(answer_parts_list, ensure_ascii=False)
            else:
                answer_parts = json.dumps([cleaned], ensure_ascii=False)

        elif qtype == "编程":
            prog_info = prog_map.get(q_number, {})
            template = prog_info.get("template", "")
            answer_code = prog_info.get("answer_code", "")
            if not template and not answer_code:
                skipped.append(f"{q_number}: 编程题未找到 HTML 对应")

        is_active = 1
        if chapter in ("8.33", "8.34", "8.35", "8.36"):
            is_active = 0

        db.execute("""
            INSERT INTO questions (q_number, chapter, type, title, content, options,
                                   answer, answer_parts, template, answer_code, note, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (q_number, chapter, qtype, title, content, options,
              raw_answer, answer_parts, template, answer_code, note, is_active))

    return skipped


def parse_single_choice_options(content):
    pattern = r'([A-D][.、．]\s*(?:<[^>]+>)*\s*[^\n]+)'
    matches = re.findall(pattern, content)
    if not matches:
        pattern2 = r'([A-D])\s*[.、．]\s*([^\n]+)'
        matches2 = re.findall(pattern2, content)
        if matches2:
            return [f"{m[0]}. {m[1].strip()}" for m in matches2]
    return matches


def seed_roster(db):
    data = load_workbook_safe(EXCEL_ROSTER)
    for row in data:
        for val in row.values():
            sid = str(val).strip()
            if sid.isdigit() and len(sid) == 10:
                db.execute("""
                    INSERT OR IGNORE INTO users (student_id, name, in_roster)
                    VALUES (?, '待定', 1)
                """, (sid,))


def main():
    try:
        init_db()
    except Exception as e:
        print(f"init_db 出错: {e}")
        return
    with get_db() as db:
        db.execute("DELETE FROM questions")
        db.execute("DELETE FROM progress")
        db.execute("DELETE FROM users")
        skipped = seed_questions(db)
        seed_roster(db)
    print(f"种子数据导入完成。")
    if skipped:
        print(f"警告 {len(skipped)} 条：")
        for s in skipped:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
