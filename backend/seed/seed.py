"""
将 题库(622道).xlsx 和 2544名单.xlsx 导入 SQLite 数据库。

Excel 结构: row[0]=注释, row[1]=表头, row[2:]=数据(含章节标题行)
列: 题号 | 题型 | 标题 | 题目 | 答案 | 备注
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl
from app.database import get_db, init_db

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXCEL_QA = os.path.join(ROOT, "data", "题库(622道).xlsx")
EXCEL_ROSTER = os.path.join(ROOT, "data", "2544名单.xlsx")
HTML_PROG = os.path.join(ROOT, "data", "编程题抽出来的题库.htm")


def load_qa_rows(path):
    """返回清洗后的题目行，跳过注释行和章节标题行"""
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        return []
    result = []
    for row in rows[2:]:
        if not row[0] or str(row[0]).strip() == "":
            continue
        qn = str(row[0]).strip()
        if qn.startswith("第") and "章" in qn:
            continue
        result.append({
            "q_number": qn,
            "type": str(row[1]).strip() if row[1] else "",
            "title": str(row[2]).strip() if row[2] else "",
            "content": str(row[3]).strip() if row[3] else "",
            "answer": str(row[4]).strip() if row[4] else "",
            "note": str(row[5]).strip() if row[5] else "",
        })
    return result


def load_roster_rows(path):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    sids = []
    for row in rows:
        for cell in row:
            if cell is not None:
                val = str(cell).strip()
                if val.isdigit() and len(val) == 10:
                    sids.append(val)
    return sids


def clean_dollar(val):
    if not isinstance(val, str):
        return val
    val = re.sub(r"'?\$'?w\+'?", "'w+'", val)
    val = val.replace("True$False", "True or False")
    val = re.sub(r"'?\$-inf'?", "-inf", val)
    val = re.sub(r"'?\+inf\$'?", "+inf", val)
    val = val.replace("$\n", "\n").replace("\n$", "\n")
    val = re.sub(r"\$\$+", "", val)
    return val.strip()


def parse_prog_html(path):
    """解析编程题 HTML：font10 color=red → 答案，黑色 → 模板"""
    if not os.path.exists(path):
        return {}
    html = None
    for enc in ("utf-8", "gbk", "gb2312", "gb18030"):
        try:
            with open(path, encoding=enc) as f:
                html = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    if html is None:
        print(f"无法解码 HTML 文件: {path}")
        return {}
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


def parse_single_choice_options(content):
    """从题干文本中提取 A/B/C/D 选项"""
    pattern = r'([A-D])[.、．]\s*(.+?)(?=\n?[A-D][.、．]|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    if matches:
        return [f"{m[0]}. {m[1].strip()}" for m in matches]
    return []


def seed_questions(db):
    prog_map = parse_prog_html(HTML_PROG)
    rows = load_qa_rows(EXCEL_QA)
    skipped = []

    for row in rows:
        q_number = row["q_number"]
        qtype = row["type"]
        title = clean_dollar(row["title"])
        content = clean_dollar(row["content"])
        raw_answer = clean_dollar(row["answer"])
        note = clean_dollar(row["note"])
        chapter = q_number.split(".")[0] if "." in q_number else q_number
        options = None
        answer_parts = None
        template = None
        answer_code = None
        is_active = 1

        if qtype == "单选":
            options = parse_single_choice_options(content)
            if options:
                answer_letter = None
                ans_text = raw_answer.strip()
                for opt_text in options:
                    opt_body = opt_text.split(".", 1)[-1].strip()
                    if ans_text == opt_body:
                        answer_letter = opt_text[0]
                        break
                if answer_letter:
                    raw_answer = answer_letter
                else:
                    skipped.append(f"{q_number}: 单选答案无法匹配选项 [{raw_answer[:50]}]")

        elif qtype == "判断":
            if raw_answer not in ("正确", "错误"):
                skipped.append(f"{q_number}: 判断题答案异常 [{raw_answer[:50]}]")

        elif qtype == "填空":
            answer_parts_list = [p.strip() for p in raw_answer.split("$") if p.strip()]
            if not answer_parts_list:
                answer_parts_list = [raw_answer]
            if raw_answer.count("$") + 1 != len(answer_parts_list):
                skipped.append(f"{q_number}: 填空 $ 数量({raw_answer.count('$')})与空数({len(answer_parts_list)})不匹配")
            answer_parts = json.dumps(answer_parts_list, ensure_ascii=False)

        elif qtype == "编程":
            prog_info = prog_map.get(q_number, {})
            template = prog_info.get("template", "")
            answer_code = prog_info.get("answer_code", "")
            if not raw_answer and not answer_code:
                is_active = 0
                skipped.append(f"{q_number}: 编程题无答案，标记为停用")

        if q_number in ("8.33", "8.34", "8.35", "8.36"):
            is_active = 0

        db.execute("""
            INSERT OR REPLACE INTO questions (q_number, chapter, type, title, content, options,
                                              answer, answer_parts, template, answer_code, note, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (q_number, chapter, qtype, title, content, options,
              raw_answer, answer_parts, template, answer_code, note, is_active))

    return skipped


def seed_roster(db):
    sids = load_roster_rows(EXCEL_ROSTER)
    for sid in sids:
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
        db.execute("DELETE FROM progress")
        db.execute("DELETE FROM questions")
        db.execute("DELETE FROM users")
        skipped = seed_questions(db)
        seed_roster(db)
    print(f"种子数据导入完成。")
    if skipped:
        print(f"\n警告 {len(skipped)} 条：")
        for s in skipped:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
