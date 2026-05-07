"""DeepSeek 判题"""
import asyncio
import json
import re
import httpx
from ..database import get_conn
from ..config import DEEPSEEK_API_KEY, DEEPSEEK_TIMEOUT


JUDGE_PROMPT = """你是一个 Python 编程题批改助手。请根据以下信息评判用户代码：

【题目描述】
{content}

【标准答案】
{answer}

【用户代码】
{user_code}

【评判要求】
1. 判断用户代码是否正确（功能等价即可，不需要逐字符一致）
2. 给出 0-10 的评分
3. 给出简短评语（中文，不超过 100 字）
4. 如果代码有错误，指出问题

请严格按以下 JSON 格式输出，不要包含任何其他内容：
{{"is_correct": true/false, "score": 0-10, "comment": "评语"}}"""


def parse_deepseek(raw: str) -> dict:
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
    if m:
        raw = m.group(1)
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        raise ValueError("未找到 JSON")
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"is_correct": False, "score": 0, "comment": "AI 判分解析失败，请手动判断"}


async def judge_code(question_id: int, user_code: str) -> dict:
    conn = get_conn()
    row = conn.execute("SELECT content, answer_code FROM questions WHERE id=?", (question_id,)).fetchone()
    conn.close()
    if not row:
        raise ValueError("题目不存在")

    prompt = JUDGE_PROMPT.format(content=row["content"], answer=row["answer_code"] or "", user_code=user_code)

    async with httpx.AsyncClient(timeout=DEEPSEEK_TIMEOUT) as client:
        resp = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0},
        )
    if resp.status_code != 200:
        raise ValueError(f"DeepSeek API 错误: {resp.status_code}")

    raw = resp.json()["choices"][0]["message"]["content"]
    return parse_deepseek(raw)
