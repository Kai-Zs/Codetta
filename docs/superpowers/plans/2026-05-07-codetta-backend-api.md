# Codetta Backend API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build complete Codetta backend API — auth (login/PIN/token), questions CRUD, progress tracking, AI judging, and Excel export.

**Architecture:** FastAPI routers delegate to service layer, which calls SQLite via existing `database.py`. Token-based auth via itsdangerous, per-endpoint dependency injection. Judge endpoint offloads to thread pool to avoid blocking.

**Tech Stack:** Python FastAPI, SQLite (sqlite3), itsdangerous, bcrypt, openpyxl, httpx

---

### Task 1: Install Dependencies & Config

**Files:**
- Modify: `backend/app/config.py`

- [ ] **Step 1: Install itsdangerous and httpx**

```bash
pip install itsdangerous httpx
```

- [ ] **Step 2: Add config values**

Edit `backend/app/config.py`, append after existing:

```python
SECRET_KEY = os.environ.get("SECRET_KEY", "codetta-dev-secret-change-in-production")
TOKEN_EXPIRE_HOURS = 24
PIN_MAX_ATTEMPTS = 5
PIN_LOCK_MINUTES = 15
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/config.py && git commit -m "feat(config): 添加 token/安全配置常量"
```

---

### Task 2: Database Migration — Add PIN Lock Fields

**Files:**
- Modify: `backend/app/database.py`

- [ ] **Step 1: Add migration to init_db**

In `backend/app/database.py`, after the users table CREATE, add ALTER TABLE statements (wrapped in try/except for idempotency):

```python
# Inside init_db(), after conn.commit() but before conn.close()
for col, ddl in [
    ("pin_attempts", "ALTER TABLE users ADD COLUMN pin_attempts INTEGER NOT NULL DEFAULT 0"),
    ("pin_locked_until", "ALTER TABLE users ADD COLUMN pin_locked_until TEXT"),
]:
    try:
        conn.execute(ddl)
    except sqlite3.OperationalError:
        pass  # column already exists
conn.commit()
```

- [ ] **Step 2: Run init_db to verify migration**

```bash
python -c "from backend.app.database import init_db; init_db()"
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/database.py && git commit -m "feat(db): users 表加 pin_attempts/pin_locked_until 字段"
```

---

### Task 3: Token Utilities

**Files:**
- Create: `backend/app/auth.py`

- [ ] **Step 1: Write auth.py**

```python
"""Token 签发与鉴权依赖"""
from itsdangerous import URLSafeTimedSerializer
from fastapi import Depends, HTTPException, Header
from .config import SECRET_KEY, TOKEN_EXPIRE_HOURS

serializer = URLSafeTimedSerializer(SECRET_KEY)


def create_token(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})


def verify_token(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid token")
    try:
        payload = serializer.loads(authorization[7:], max_age=TOKEN_EXPIRE_HOURS * 3600)
    except Exception:
        raise HTTPException(401, "Token expired or invalid")
    return payload


def get_user_id(payload: dict = Depends(verify_token)) -> int:
    return payload["user_id"]
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/auth.py && git commit -m "feat(auth): itsdangerous token 签发与鉴权依赖"
```

---

### Task 4: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas.py`

- [ ] **Step 1: Write schemas.py**

```python
"""Pydantic 请求/响应模型"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    student_id: str = Field(min_length=10, max_length=10, pattern=r"^\d{10}$")


class VerifyPinRequest(BaseModel):
    student_id: str = Field(min_length=10, max_length=10, pattern=r"^\d{10}$")
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


class SetPinRequest(BaseModel):
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")
    old_pin: str | None = None


class UpdateSettingsRequest(BaseModel):
    prog_mode: str | None = None
    sound_on: int | None = None
    vibrate_on: int | None = None


class ProgressSubmit(BaseModel):
    question_id: int
    answer_status: str  # correct/incorrect/partial/pending/timeout
    user_answer: str  # JSON array string
    mode: str = "sequential"
    prog_submit_type: str | None = None


class RemoveWrongRequest(BaseModel):
    question_ids: list[int]


class JudgeRequest(BaseModel):
    question_id: int
    user_code: str
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/schemas.py && git commit -m "feat(schemas): Pydantic 请求/响应模型"
```

---

### Task 5: Auth Service + Router

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/auth.py`
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/auth.py`

- [ ] **Step 1: Write auth service**

`backend/app/services/auth.py`:

```python
"""认证业务逻辑"""
import bcrypt
from datetime import datetime, timedelta
from ..database import get_conn
from ..config import PIN_MAX_ATTEMPTS, PIN_LOCK_MINUTES


def handle_login(student_id: str) -> dict:
    conn = get_conn()
    row = conn.execute("SELECT id, name, pin, in_roster FROM users WHERE student_id=?", (student_id,)).fetchone()
    if not row:
        name = student_id[-4:] + "同学"
        conn.execute("INSERT INTO users (student_id, name, in_roster) VALUES (?,?,0)", (student_id, name))
        conn.commit()
        conn.close()
        return {"status": "need_setup", "name": name, "need_pin": False}
    if not row["pin"]:
        conn.close()
        return {"status": "need_setup", "name": row["name"], "need_pin": False}
    conn.close()
    return {"status": "need_pin", "name": row["name"], "need_pin": True}


def verify_pin(student_id: str, pin: str) -> dict:
    conn = get_conn()
    row = conn.execute("SELECT id, pin, pin_attempts, pin_locked_until FROM users WHERE student_id=?", (student_id,)).fetchone()
    if not row or not row["pin"]:
        conn.close()
        raise ValueError("用户不存在或未设置 PIN")

    if row["pin_locked_until"] and datetime.fromisoformat(row["pin_locked_until"]) > datetime.now():
        conn.close()
        raise ValueError("账户已锁定，请稍后再试")

    if not bcrypt.checkpw(pin.encode(), row["pin"].encode()):
        attempts = row["pin_attempts"] + 1
        if attempts >= PIN_MAX_ATTEMPTS:
            locked = (datetime.now() + timedelta(minutes=PIN_LOCK_MINUTES)).isoformat()
            conn.execute("UPDATE users SET pin_attempts=?, pin_locked_until=? WHERE id=?", (attempts, locked, row["id"]))
        else:
            conn.execute("UPDATE users SET pin_attempts=? WHERE id=?", (attempts, row["id"]))
        conn.commit()
        conn.close()
        raise ValueError(f"PIN 错误，剩余尝试 {PIN_MAX_ATTEMPTS - attempts} 次")

    conn.execute("UPDATE users SET pin_attempts=0, pin_locked_until=NULL WHERE id=?", (row["id"],))
    conn.commit()
    conn.close()
    return {"user_id": row["id"], "name": ""}


def set_pin(user_id: int, pin: str, old_pin: str | None = None) -> None:
    conn = get_conn()
    row = conn.execute("SELECT pin FROM users WHERE id=?", (user_id,)).fetchone()
    if row and row["pin"] and old_pin is None:
        conn.close()
        raise ValueError("修改 PIN 需要提供旧 PIN")
    if row and row["pin"]:
        if not bcrypt.checkpw(old_pin.encode(), row["pin"].encode()):
            conn.close()
            raise ValueError("旧 PIN 错误")
    hashed = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
    conn.execute("UPDATE users SET pin=? WHERE id=?", (hashed, user_id))
    conn.commit()
    conn.close()


def get_me(user_id: int) -> dict:
    conn = get_conn()
    row = conn.execute("SELECT student_id, name, prog_mode, sound_on, vibrate_on FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row)


def update_settings(user_id: int, data: dict) -> None:
    conn = get_conn()
    for field in ("prog_mode", "sound_on", "vibrate_on"):
        if field in data and data[field] is not None:
            conn.execute(f"UPDATE users SET {field}=? WHERE id=?", (data[field], user_id))
    conn.commit()
    conn.close()


def reset_pin(student_id: str) -> None:
    conn = get_conn()
    conn.execute("UPDATE users SET pin=NULL, pin_attempts=0, pin_locked_until=NULL WHERE student_id=?", (student_id,))
    conn.commit()
    conn.close()
```

- [ ] **Step 2: Write auth router**

`backend/app/routers/auth.py`:

```python
"""认证路由"""
from fastapi import APIRouter, Depends, HTTPException
from ..schemas import LoginRequest, VerifyPinRequest, SetPinRequest, UpdateSettingsRequest
from ..auth import create_token, get_user_id
from ..services.auth import handle_login, verify_pin, set_pin, get_me, update_settings, reset_pin

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(body: LoginRequest):
    return handle_login(body.student_id)


@router.post("/verify-pin")
def verify(body: VerifyPinRequest):
    try:
        result = verify_pin(body.student_id, body.pin)
    except ValueError as e:
        raise HTTPException(400, str(e))
    token = create_token(result["user_id"])
    user = get_me(result["user_id"])
    return {"token": token, "user": user}


@router.post("/set-pin")
def set_pin_route(body: SetPinRequest, user_id: int = Depends(get_user_id)):
    try:
        set_pin(user_id, body.pin, body.old_pin)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"ok": True}


@router.get("/me")
def me_route(user_id: int = Depends(get_user_id)):
    return get_me(user_id)


@router.patch("/settings")
def settings_route(body: UpdateSettingsRequest, user_id: int = Depends(get_user_id)):
    update_settings(user_id, body.model_dump(exclude_none=True))
    return {"ok": True}


@router.post("/admin/reset-pin")
def reset_pin_route(body: LoginRequest):
    reset_pin(body.student_id)
    return {"ok": True}
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/__init__.py backend/app/services/auth.py backend/app/routers/__init__.py backend/app/routers/auth.py && git commit -m "feat(auth): 认证 API — login/verify-pin/set-pin/me/settings/reset-pin"
```

---

### Task 6: Questions Service + Router

**Files:**
- Create: `backend/app/services/questions.py`
- Create: `backend/app/routers/questions.py`

- [ ] **Step 1: Write questions service**

`backend/app/services/questions.py`:

```python
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
    return {"total": total, "page": page, "per": per,
            "items": [{"id": r["id"], "q_number": r["q_number"], "chapter": r["chapter"],
                        "type": r["type"], "title": r["title"]} for r in rows]}


def get_question(question_id: int) -> dict:
    conn = get_conn()
    row = conn.execute("SELECT * FROM questions WHERE id=? AND is_active=1", (question_id,)).fetchone()
    conn.close()
    if not row:
        raise ValueError("题目不存在")
    return dict(row)
```

- [ ] **Step 2: Write questions router**

`backend/app/routers/questions.py`:

```python
"""题库路由"""
from fastapi import APIRouter, Depends, Query, HTTPException
from ..auth import get_user_id
from ..services.questions import list_questions, get_question

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("")
def list_q(type: str = Query(""), chapter: str = Query(""), page: int = Query(1, ge=1), per: int = Query(20, ge=1, le=100),
           user_id: int = Depends(get_user_id)):
    return list_questions(type=type, chapter=chapter, page=page, per=per)


@router.get("/{question_id}")
def get_q(question_id: int, user_id: int = Depends(get_user_id)):
    try:
        return get_question(question_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/questions.py backend/app/routers/questions.py && git commit -m "feat(questions): 题库 API — 列表查询/单题详情"
```

---

### Task 7: Progress Service + Router

**Files:**
- Create: `backend/app/services/progress.py`
- Create: `backend/app/routers/progress.py`

- [ ] **Step 1: Write progress service**

`backend/app/services/progress.py`:

```python
"""进度业务逻辑"""
import json
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
    # Find next undone question
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
    return {"total": total, "page": page, "per": per,
            "items": [dict(r) for r in rows]}


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
```

- [ ] **Step 2: Write progress router**

`backend/app/routers/progress.py`:

```python
"""进度路由"""
from fastapi import APIRouter, Depends, Query
from ..schemas import ProgressSubmit, RemoveWrongRequest
from ..auth import get_user_id
from ..services import progress as svc

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("")
def get_p(user_id: int = Depends(get_user_id)):
    return svc.get_progress(user_id)


@router.post("")
def submit(body: ProgressSubmit, user_id: int = Depends(get_user_id)):
    return svc.submit_progress(user_id, body.model_dump())


@router.get("/wrong")
def list_wrong(type: str = Query(""), chapter: str = Query(""), page: int = Query(1, ge=1), per: int = Query(20, ge=1, le=100),
               user_id: int = Depends(get_user_id)):
    return svc.get_wrong(user_id, type=type, chapter=chapter, page=page, per=per)


@router.post("/remove-wrong")
def remove_wrong(body: RemoveWrongRequest, user_id: int = Depends(get_user_id)):
    svc.remove_from_wrong(user_id, body.question_ids)
    return {"ok": True}


@router.delete("")
def clear(user_id: int = Depends(get_user_id)):
    svc.clear_progress(user_id)
    return {"ok": True}
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/progress.py backend/app/routers/progress.py && git commit -m "feat(progress): 进度 API — 概览/提交/错题/移出错题本/清空"
```

---

### Task 8: Judge Service + Router

**Files:**
- Create: `backend/app/services/judge.py`
- Create: `backend/app/routers/judge.py`

- [ ] **Step 1: Write judge service**

`backend/app/services/judge.py`:

```python
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
{"is_correct": true/false, "score": 0-10, "comment": "评语"}"""


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
```

- [ ] **Step 2: Write judge router**

`backend/app/routers/judge.py`:

```python
"""判题路由"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from ..schemas import JudgeRequest
from ..auth import get_user_id
from ..services.judge import judge_code

router = APIRouter(prefix="/api/judge", tags=["judge"])


@router.post("/code")
async def judge(body: JudgeRequest, user_id: int = Depends(get_user_id)):
    try:
        return await asyncio.wait_for(judge_code(body.question_id, body.user_code), timeout=40)
    except asyncio.TimeoutError:
        raise HTTPException(408, "判题超时，请手动判断")
    except ValueError as e:
        raise HTTPException(400, str(e))
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/judge.py backend/app/routers/judge.py && git commit -m "feat(judge): DeepSeek 判题 API — 40s 超时，JSON 容错"
```

---

### Task 9: Export Service + Router

**Files:**
- Create: `backend/app/services/export.py`
- Create: `backend/app/routers/export.py`

- [ ] **Step 1: Write export service**

`backend/app/services/export.py`:

```python
"""错题导出 Excel"""
import io
import openpyxl
from ..database import get_conn


def export_wrong(user_id: int) -> bytes:
    conn = get_conn()
    rows = conn.execute(
        "SELECT DISTINCT q.q_number, q.type, q.title, q.content, p.answer_status "
        "FROM progress p JOIN questions q ON p.question_id=q.id "
        "WHERE p.user_id=? AND p.answer_status IN ('incorrect','partial') AND p.removed_from_wrong=0 "
        "ORDER BY q.id",
        (user_id,)
    ).fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["题号", "题型", "标题", "题目", "作答状态"])
    for r in rows:
        ws.append([r["q_number"], r["type"], r["title"], r["content"], r["answer_status"]])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()
```

- [ ] **Step 2: Write export router**

`backend/app/routers/export.py`:

```python
"""导出路由"""
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from ..auth import get_user_id
from ..services.export import export_wrong

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/wrong")
def export(user_id: int = Depends(get_user_id)):
    data = export_wrong(user_id)
    return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=wrong_questions.xlsx"})
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/export.py backend/app/routers/export.py && git commit -m "feat(export): 错题导出 Excel API"
```

---

### Task 10: FastAPI Entry Point

**Files:**
- Create: `backend/app/main.py`

- [ ] **Step 1: Write main.py**

```python
"""Codetta API 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, questions, progress, judge, export

app = FastAPI(title="Codetta API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(progress.router)
app.include_router(judge.router)
app.include_router(export.router)


@app.get("/api/health")
def health():
    return {"ok": True}
```

- [ ] **Step 2: Start server and smoke test**

```bash
# Terminal 1
uvicorn backend.app.main:app --reload --port 8765

# Terminal 2 — test health
curl http://127.0.0.1:8765/api/health

# test login
curl -X POST http://127.0.0.1:8765/api/auth/login -H "Content-Type: application/json" -d '{"student_id":"0000000001"}'

# test questions (公共题号)
curl http://127.0.0.1:8765/api/questions -H "Authorization: Bearer <token>"
```

Expected: health returns `{"ok": true}`, login returns status.

- [ ] **Step 3: Commit**

```bash
git add backend/app/main.py && git commit -m "feat(main): FastAPI 入口 + CORS + 路由注册"
```

---

### Task 11: Update Memory & Push

- [ ] **Step 1: Update project memory**

Update `C:\Users\KaiZs\.claude\projects\C--Users-KaiZs-Desktop-chaos-study------practice\memory\project_lianbixiaozhu.md`:
- Mark "认证 API" as done
- Mark "后端 API 全部完成"

- [ ] **Step 2: Final push**

```bash
git push
```
