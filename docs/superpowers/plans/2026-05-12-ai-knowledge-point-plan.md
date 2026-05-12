# AI 知识点解析 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在做题页面新增 AI 知识点解析面板，支持缓存、重新解析、追问，独立数据库不干扰主库。

**Architecture:** 后端新增 `knowledge_point` service + router（独立 `ai_kp.db`，复用 DeepSeek API），前端新增 `AiKpPanel` 组件 + 修改 `PracticeView` 布局。权限通过 `kp_access` 表 + 管理后台开关管控。

**Tech Stack:** FastAPI (Python), Vue 3 + Pinia, SQLite (独立文件), DeepSeek v4 Flash, marked + highlight.js + KaTeX + DOMPurify

**Spec:** `docs/superpowers/specs/2026-05-11-ai-knowledge-point-design.md`

---

## 文件清单

| 文件 | 操作 |
|------|------|
| `backend/app/services/knowledge_point.py` | 新建 |
| `backend/app/routers/knowledge_point.py` | 新建 |
| `backend/app/main.py` | 修改 — 注册路由 + startup |
| `backend/app/routers/admin.py` | 修改 — kp-access 端点 |
| `backend/app/services/judge.py` | 修改 — 模型名 |
| `frontend/src/api/knowledge_point.js` | 新建 |
| `frontend/src/components/practice/AiKpPanel.vue` | 新建 |
| `frontend/src/views/PracticeView.vue` | 修改 |
| `frontend/src/views/admin/AdminUsers.vue` | 修改 |

---

### Task 1: 模型切换 — deepseek-chat → deepseek-v4-flash

**Files:**
- Modify: `backend/app/services/judge.py:55`

- [ ] **Step 1: 修改模型名**

```python
# backend/app/services/judge.py:55
# 将 "deepseek-chat" 改为 "deepseek-v4-flash"
json={"model": "deepseek-v4-flash", "messages": [{"role": "user", "content": prompt}], "temperature": 0},
```

- [ ] **Step 2: 验证语法**

```bash
cd backend && python -c "from app.services.judge import judge_code; print('import OK')"
```

Expected: `import OK`

- [ ] **Step 3: 提交**

```bash
git add backend/app/services/judge.py
git commit -m "chore: 判题模型切换为 deepseek-v4-flash"
```

---

### Task 2: 知识点解析服务

**Files:**
- Create: `backend/app/services/knowledge_point.py`

- [ ] **Step 1: 创建服务文件**

```python
"""AI 知识点解析服务"""
import os
import threading
import httpx
from ..database import get_db
from ..config import DEEPSEEK_API_KEY, DEEPSEEK_TIMEOUT, BASE_DIR

KP_DB_PATH = os.path.join(BASE_DIR, "data", "ai_kp.db")
_locks = {}
_locks_lock = threading.Lock()

# === 独立数据库连接 ===

def get_kp_conn():
    import sqlite3
    conn = sqlite3.connect(KP_DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


def get_kp_db():
    conn = get_kp_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_kp_db():
    with get_kp_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS kp_cache (
                question_id INTEGER PRIMARY KEY,
                analysis_md  TEXT NOT NULL,
                created_at   TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            );
            CREATE TABLE IF NOT EXISTS kp_access (
                student_id TEXT PRIMARY KEY,
                enabled    INTEGER NOT NULL DEFAULT 1
            );
            INSERT OR IGNORE INTO kp_access (student_id, enabled) VALUES ('2025006708', 1);
        """)


# === 权限校验 ===

def check_kp_access(user_id: int) -> bool:
    with get_db() as db:
        row = db.execute("SELECT student_id FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            return False
        student_id = row["student_id"]
    with get_kp_db() as kdb:
        r = kdb.execute("SELECT enabled FROM kp_access WHERE student_id=?", (student_id,)).fetchone()
        return r is not None and r["enabled"] == 1


# === Prompt ===

KP_PROMPT = """你是一个 Python 知识点分析助手。请根据以下题目信息，提炼涉及的知识点，
简要介绍，并指出重点难点和易错点。

【题号】{q_number}
【章节】{chapter}
【题型】{type}
【题目】{content}
{answer_block}
{options_block}
{note_block}
请自由组织输出结构，使用 markdown 格式，可包含代码示例和公式。"""


CHAT_PROMPT = """你是一个 Python 学习助教。以下是一道题目的信息和 AI 已给出的知识点解析，
请根据用户的追问继续解答。

【题目信息】
题号：{q_number} | 章节：{chapter} | 题型：{type}
题目：{content}
答案：{answer}

【知识点解析】
{analysis_md}

请结合以上上下文回答用户的问题。"""


def _build_analyze_messages(question: dict) -> list[dict]:
    q_type = question["type"]
    if q_type == "编程题":
        answer_text = question.get("answer_code") or question.get("answer") or ""
    elif question.get("answer_parts"):
        answer_text = question["answer_parts"]
    else:
        answer_text = question.get("answer") or ""

    answer_block = f"【答案】\n{answer_text}" if answer_text else ""
    options_block = f"【选项】\n{question['options']}" if question.get("options") else ""
    note_block = f"【解析/备注】\n{question['note']}" if question.get("note") else ""

    prompt = KP_PROMPT.format(
        q_number=question["q_number"],
        chapter=question["chapter"],
        type=question["type"],
        content=question.get("content") or question.get("title", ""),
        answer_block=answer_block,
        options_block=options_block,
        note_block=note_block,
    )
    return [{"role": "user", "content": prompt}]


# === 缓存查询 ===

def get_cached_analysis(question_id: int) -> str | None:
    with get_kp_db() as db:
        row = db.execute("SELECT analysis_md FROM kp_cache WHERE question_id=?", (question_id,)).fetchone()
        return row["analysis_md"] if row else None


def save_analysis(question_id: int, analysis_md: str):
    with get_kp_db() as db:
        db.execute(
            "INSERT OR REPLACE INTO kp_cache (question_id, analysis_md, created_at) VALUES (?,?,datetime('now','localtime'))",
            (question_id, analysis_md),
        )


# === DeepSeek 调用 ===

def _call_deepseek(messages: list[dict]) -> str:
    with httpx.Client(timeout=DEEPSEEK_TIMEOUT) as client:
        resp = client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-v4-flash",
                "messages": messages,
                "temperature": 0.7,
            },
        )
    if resp.status_code != 200:
        raise ValueError(f"DeepSeek API 错误: {resp.status_code}")
    try:
        return resp.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise ValueError("DeepSeek 返回格式异常")


# === 解析（含缓存与锁） ===

def analyze_kp(question_id: int, force: bool = False) -> dict:
    if not force:
        cached = get_cached_analysis(question_id)
        if cached is not None:
            return {"analysis_md": cached, "cached": True}

    with get_db() as db:
        row = db.execute("SELECT * FROM questions WHERE id=? AND is_active=1", (question_id,)).fetchone()
        if not row:
            raise ValueError("题目不存在")

    with _locks_lock:
        lock = _locks.setdefault(question_id, threading.Lock())

    with lock:
        if not force:
            cached = get_cached_analysis(question_id)
            if cached is not None:
                return {"analysis_md": cached, "cached": True}

        messages = _build_analyze_messages(dict(row))
        analysis_md = _call_deepseek(messages)
        save_analysis(question_id, analysis_md)
        try:
            del _locks[question_id]
        except KeyError:
            pass
        return {"analysis_md": analysis_md, "cached": False}


# === 追问 ===

def chat_followup(question_id: int, messages: list[dict]) -> str:
    MAX_ROUNDS = 20
    MAX_CHARS = 8000
    MIN_KEEP = 3

    with get_db() as db:
        row = db.execute("SELECT * FROM questions WHERE id=? AND is_active=1", (question_id,)).fetchone()
        if not row:
            raise ValueError("题目不存在")

    q = dict(row)
    q_type = q["type"]
    if q_type == "编程题":
        answer_text = q.get("answer_code") or q.get("answer") or ""
    elif q.get("answer_parts"):
        answer_text = q["answer_parts"]
    else:
        answer_text = q.get("answer") or ""

    analysis_md = get_cached_analysis(question_id) or ""
    system_msg = {
        "role": "system",
        "content": CHAT_PROMPT.format(
            q_number=q["q_number"],
            chapter=q["chapter"],
            type=q["type"],
            content=q.get("content") or q.get("title", ""),
            answer=answer_text,
            analysis_md=analysis_md,
        ),
    }

    all_msgs = [system_msg] + messages

    # 截断：先按轮数
    if len(all_msgs) > 1 + MAX_ROUNDS * 2:
        keep_messages = messages[-(MAX_ROUNDS - 5) * 2:]  # 最近 (MAX_ROUNDS-5) 轮
        all_msgs = [system_msg] + keep_messages

    # 再按字符数
    total_chars = sum(len(m.get("content", "")) for m in all_msgs)
    while total_chars > MAX_CHARS and len(all_msgs) > 1 + MIN_KEEP * 2:
        all_msgs.pop(1)
        total_chars = sum(len(m.get("content", "")) for m in all_msgs)

    return _call_deepseek(all_msgs)
```

- [ ] **Step 2: 验证语法**

```bash
cd backend && python -c "from app.services.knowledge_point import init_kp_db, check_kp_access, analyze_kp, chat_followup; print('import OK')"
```

Expected: `import OK`

- [ ] **Step 3: 提交**

```bash
git add backend/app/services/knowledge_point.py
git commit -m "feat: 知识点解析服务 — AI 分析、缓存、追问、独立数据库"
```

---

### Task 3: 知识点解析路由

**Files:**
- Create: `backend/app/routers/knowledge_point.py`

- [ ] **Step 1: 创建路由文件**

```python
"""知识点解析路由"""
import concurrent.futures
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..auth import get_user_id
from ..services.knowledge_point import check_kp_access, analyze_kp, chat_followup

router = APIRouter(prefix="/api/kp", tags=["kp"])


class AnalyzeRequest(BaseModel):
    question_id: int
    force: bool = False


class ChatRequest(BaseModel):
    question_id: int
    messages: list[dict]


def require_kp_access(user_id: int = Depends(get_user_id)):
    if not check_kp_access(user_id):
        raise HTTPException(403, "此功能未对你开放")
    return user_id


@router.get("/check")
def check(user_id: int = Depends(get_user_id)):
    return {"kp_enabled": check_kp_access(user_id)}


@router.post("/analyze")
def analyze(body: AnalyzeRequest, user_id: int = Depends(require_kp_access)):
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(analyze_kp, body.question_id, body.force)
            return future.result(timeout=45)
    except concurrent.futures.TimeoutError:
        raise HTTPException(408, "分析超时，请重试")
    except ValueError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"分析服务异常: {str(e)[:100]}")


@router.post("/chat")
def chat(body: ChatRequest, user_id: int = Depends(require_kp_access)):
    if not body.messages or len(body.messages) == 0:
        raise HTTPException(400, "消息不能为空")

    user_messages = [m for m in body.messages if m.get("role") == "user"]
    if not user_messages:
        raise HTTPException(400, "至少需要一条用户消息")

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(chat_followup, body.question_id, body.messages)
            return {"reply": future.result(timeout=45)}
    except concurrent.futures.TimeoutError:
        raise HTTPException(408, "追问超时，请重试")
    except ValueError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"追问服务异常: {str(e)[:100]}")
```

- [ ] **Step 2: 验证语法**

```bash
cd backend && python -c "from app.routers.knowledge_point import router; print('import OK')"
```

Expected: `import OK`

- [ ] **Step 3: 提交**

```bash
git add backend/app/routers/knowledge_point.py
git commit -m "feat: 知识点解析路由 — check/analyze/chat 端点"
```

---

### Task 4: 注册路由与 startup 事件

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: 在 main.py 顶部添加 import**

```python
# backend/app/main.py — 在现有 from .routers import ... 行追加 knowledge_point
from .routers import auth, questions, progress, judge, export, admin, knowledge_point
```

- [ ] **Step 2: 在 app = FastAPI(...) 之后添加 startup 事件与 import**

```python
# 在 import 区域下方、middleware 之前插入
from .services.knowledge_point import init_kp_db

@app.on_event("startup")
def startup():
    init_kp_db()
```

- [ ] **Step 3: 在现有 app.include_router(admin.router) 之后注册路由**

```python
# 在 app.include_router(admin.router) 下方添加
app.include_router(knowledge_point.router)
```

- [ ] **Step 4: 验证**

```bash
cd backend && python -c "from app.main import app; print('startup OK'); print([r.path for r in app.routes if hasattr(r, 'path')])"
```

Expected: 输出包含 `/api/kp/check`, `/api/kp/analyze`, `/api/kp/chat`

- [ ] **Step 5: 提交**

```bash
git add backend/app/main.py
git commit -m "feat: 注册 kp 路由 + startup 初始化 ai_kp.db"
```

---

### Task 5: 管理后台 — kp-access 端点

**Files:**
- Modify: `backend/app/routers/admin.py`
- Modify: `backend/app/services/admin.py` (add 2 functions)

- [ ] **Step 1: 在 services/admin.py 末尾添加 kp-access 函数**

```python
# backend/app/services/admin.py 末尾追加
from .knowledge_point import get_kp_db


def list_kp_access(search: str = "") -> list[dict]:
    from .knowledge_point import get_kp_db

    with get_kp_db() as kdb:
        kp_rows = kdb.execute("SELECT student_id, enabled FROM kp_access").fetchall()
    kp_map = {r["student_id"]: r["enabled"] for r in kp_rows}

    with get_db() as db:
        where = "WHERE student_id LIKE ? OR name LIKE ?" if search else ""
        params = [f"%{search}%", f"%{search}%"] if search else []
        users = db.execute(
            f"SELECT student_id, name FROM users {where} ORDER BY id",
            params,
        ).fetchall()

    result = []
    for u in users:
        sid = u["student_id"]
        result.append({
            "student_id": sid,
            "name": u["name"],
            "kp_enabled": bool(kp_map.get(sid, 0)),
        })
    return result


def set_kp_access(student_id: str, enabled: bool):
    with get_kp_db() as kdb:
        kdb.execute(
            "INSERT OR REPLACE INTO kp_access (student_id, enabled) VALUES (?,?)",
            (student_id, 1 if enabled else 0),
        )
```

- [ ] **Step 2: 在 routers/admin.py 的 verify_admin 依赖之后添加 kp-access 端点**

```python
# backend/app/routers/admin.py — 在现有路由之后添加
@router.get("/kp-access", dependencies=[Depends(verify_admin)])
def list_kp_access(search: str = Query("")):
    return {"items": svc.list_kp_access(search)}


@router.post("/kp-access", dependencies=[Depends(verify_admin)])
def set_kp_access(body: dict):
    student_id = body.get("student_id", "")
    enabled = body.get("enabled", False)
    if not student_id:
        raise HTTPException(400, "student_id 必填")
    svc.set_kp_access(student_id, enabled)
    return {"ok": True}
```

注：需要在 admin.py 顶部已有 import 处确认 `Query` 已从 fastapi 导入（现有代码已有）。

- [ ] **Step 3: 验证语法**

```bash
cd backend && python -c "from app.routers.admin import router; from app.services.admin import list_kp_access, set_kp_access; print('import OK')"
```

Expected: `import OK`

- [ ] **Step 4: 提交**

```bash
git add backend/app/routers/admin.py backend/app/services/admin.py
git commit -m "feat: 管理后台 kp-access 列表与开关端点"
```

---

### Task 6: 前端依赖安装

- [ ] **Step 1: 安装 npm 包**

```bash
cd frontend && npm install marked highlight.js katex dompurify
```

Expected: 安装成功，无 error

- [ ] **Step 2: 提交**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore: 安装 marked/highlight.js/katex/dompurify"
```

---

### Task 7: 前端 API 模块

**Files:**
- Create: `frontend/src/api/knowledge_point.js`

- [ ] **Step 1: 创建 API 模块**

```javascript
import api from './index'

export function checkKp() {
  return api.get('/kp/check').then(r => r.data)
}

export function analyzeKp(questionId, force = false) {
  return api.post('/kp/analyze', { question_id: questionId, force }).then(r => r.data)
}

export function chatKp(questionId, messages) {
  return api.post('/kp/chat', { question_id: questionId, messages }).then(r => r.data)
}
```

- [ ] **Step 2: 验证无语法错误**

```bash
cd frontend && npx eslint src/api/knowledge_point.js 2>/dev/null; echo "syntax check done"
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/api/knowledge_point.js
git commit -m "feat: 前端知识解析 API 模块"
```

---

### Task 8: AiKpPanel 组件

**Files:**
- Create: `frontend/src/components/practice/AiKpPanel.vue`

- [ ] **Step 1: 创建组件**

```vue
<template>
  <div class="kp-panel">
    <!-- 顶栏 -->
    <div class="kp-topbar">
      <h3 class="kp-title">知识点解析</h3>
      <div class="kp-topbar-actions">
        <button v-if="content" @click="$emit('reanalyze')" class="kp-btn-sm">重新解析</button>
        <button @click="$emit('close')" class="kp-btn-close" title="关闭">&#10005;</button>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="kp-body" ref="bodyRef">
      <!-- 加载态 -->
      <div v-if="loading" class="kp-state">
        <div class="kp-skeleton">
          <div class="kp-skel-line w-3/4"></div>
          <div class="kp-skel-line w-1/2"></div>
          <div class="kp-skel-line w-full"></div>
          <div class="kp-skel-line w-2/3"></div>
        </div>
        <p class="kp-loading-text">AI 正在分析知识点…</p>
      </div>

      <!-- 错误态 -->
      <div v-else-if="error" class="kp-state">
        <p class="kp-error-text">{{ error }}</p>
        <button @click="$emit('reanalyze')" class="kp-btn-retry">重试</button>
      </div>

      <!-- 空态 -->
      <div v-else-if="!content" class="kp-state">
        <p class="kp-empty-text">点击「AI 知识点解析」按钮获取分析</p>
      </div>

      <!-- Markdown 渲染 -->
      <div v-else class="kp-markdown" v-html="renderedHtml"></div>
    </div>

    <!-- 追问区 -->
    <div v-if="content" class="kp-chat">
      <div class="kp-chat-messages" ref="chatRef">
        <div v-for="(m, i) in chatMessages" :key="i" class="kp-chat-msg" :class="m.role">
          <div class="kp-chat-bubble" v-html="m.role === 'assistant' ? renderMd(m.content) : escapeHtml(m.content)"></div>
        </div>
        <div v-if="chatLoading" class="kp-chat-msg assistant">
          <div class="kp-chat-bubble"><span class="kp-typing">…</span></div>
        </div>
      </div>
      <div class="kp-chat-input-row">
        <textarea
          v-model="chatInput"
          @keydown.enter.exact.prevent="send"
          @keydown.shift.enter="chatInput += '\n'"
          placeholder="追问 AI…"
          :disabled="chatLoading"
          rows="1"
          ref="inputRef"
          class="kp-chat-input"
        ></textarea>
        <button @click="send" :disabled="chatLoading || !chatInput.trim()" class="kp-chat-send">发送</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import DOMPurify from 'dompurify'

// === marked 配置 ===
marked.setOptions({ breaks: true, gfm: true })

const renderer = new marked.Renderer()
renderer.code = function (code, language) {
  const lang = language && hljs.getLanguage(language) ? language : 'plaintext'
  const highlighted = hljs.highlight(code, { language: lang }).value
  return `<pre><code class="hljs language-${lang}">${highlighted}</code></pre>`
}

function renderMd(text) {
  // 处理 $$...$$ 块级公式
  let html = text.replace(/\$\$([\s\S]*?)\$\$/g, (_, formula) => {
    try { return katex.renderToString(formula.trim(), { displayMode: true, throwOnError: false }) }
    catch { return `<pre>${formula}</pre>` }
  })
  // 处理 $...$ 行内公式
  html = html.replace(/\$([^\$]+?)\$/g, (_, formula) => {
    try { return katex.renderToString(formula.trim(), { displayMode: false, throwOnError: false }) }
    catch { return formula }
  })
  const mdHtml = marked.parse(html)
  return DOMPurify.sanitize(mdHtml, { ADD_ATTR: ['target'] })
}

function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

const props = defineProps({
  content: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['close', 'reanalyze', 'chat'])

const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const bodyRef = ref(null)
const chatRef = ref(null)
const inputRef = ref(null)

const renderedHtml = computed(() => props.content ? renderMd(props.content) : '')

async function send() {
  const text = chatInput.value.trim()
  if (!text || chatLoading.value) return
  chatMessages.value.push({ role: 'user', content: text })
  chatInput.value = ''
  chatLoading.value = true
  await nextTick()
  chatRef.value?.scrollTo({ top: chatRef.value.scrollHeight, behavior: 'smooth' })

  try {
    const reply = await new Promise((resolve, reject) => {
      emit('chat', chatMessages.value, resolve, reject)
    })
    chatMessages.value.push({ role: 'assistant', content: reply })
  } catch {
    chatMessages.value.push({ role: 'assistant', content: '追问失败，请重试。' })
  } finally {
    chatLoading.value = false
    await nextTick()
    chatRef.value?.scrollTo({ top: chatRef.value.scrollHeight, behavior: 'smooth' })
  }
}

watch(() => props.content, () => {
  chatMessages.value = []
})
</script>

<style scoped>
.kp-panel {
  width: 400px;
  min-height: 500px;
  display: flex;
  flex-direction: column;
  background: var(--bg-card, #fff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  overflow: hidden;
}
.kp-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
  flex-shrink: 0;
}
.kp-title { font-size: 14px; font-weight: 600; margin: 0; }
.kp-topbar-actions { display: flex; gap: 8px; align-items: center; }
.kp-btn-sm {
  font-size: 12px; padding: 4px 10px; border-radius: 6px;
  border: 1px solid var(--border-color, #d1d5db);
  background: var(--bg, #f9fafb); cursor: pointer;
}
.kp-btn-close {
  font-size: 16px; border: none; background: none; cursor: pointer;
  line-height: 1; padding: 2px;
}
.kp-body { flex: 1; overflow-y: auto; padding: 14px; }
.kp-markdown { font-size: 13px; line-height: 1.7; }
.kp-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 20px; text-align: center; }
.kp-loading-text { font-size: 13px; color: var(--text-muted, #9ca3af); margin-top: 12px; }
.kp-empty-text { font-size: 13px; color: var(--text-muted, #9ca3af); }
.kp-error-text { font-size: 13px; color: #ef4444; margin-bottom: 12px; }
.kp-btn-retry {
  padding: 6px 16px; border-radius: 6px; font-size: 13px;
  background: #8b5cf6; color: #fff; border: none; cursor: pointer;
}
/* 骨架 */
.kp-skeleton { width: 100%; }
.kp-skel-line { height: 14px; background: var(--skeleton, #e5e7eb); border-radius: 4px; margin-bottom: 10px; }
/* 追问 */
.kp-chat { border-top: 1px solid var(--border-color, #e5e7eb); display: flex; flex-direction: column; flex-shrink: 0; }
.kp-chat-messages { flex: 1; max-height: 200px; overflow-y: auto; padding: 8px 14px; }
.kp-chat-msg { margin-bottom: 8px; }
.kp-chat-msg.user { text-align: right; }
.kp-chat-msg.assistant { text-align: left; }
.kp-chat-bubble {
  display: inline-block; max-width: 85%; padding: 6px 10px; border-radius: 10px;
  font-size: 12px; line-height: 1.5; word-break: break-word;
}
.kp-chat-msg.user .kp-chat-bubble { background: #8b5cf6; color: #fff; }
.kp-chat-msg.assistant .kp-chat-bubble { background: var(--bubble-bg, #f3f4f6); color: var(--text, #374151); }
.kp-typing { animation: kp-blink 1s infinite; }
@keyframes kp-blink { 50% { opacity: 0; } }
.kp-chat-input-row {
  display: flex; gap: 8px; padding: 8px 14px;
  border-top: 1px solid var(--border-color, #e5e7eb);
  position: sticky; bottom: 0; background: var(--bg-card, #fff);
}
.kp-chat-input {
  flex: 1; resize: none; padding: 6px 10px; border-radius: 8px;
  border: 1px solid var(--border-color, #d1d5db);
  font-size: 12px; line-height: 1.5;
  background: var(--bg, #fff); color: var(--text, #374151);
}
.kp-chat-send {
  padding: 6px 14px; border-radius: 8px; font-size: 12px;
  background: #8b5cf6; color: #fff; border: none; cursor: pointer;
  flex-shrink: 0;
}
.kp-chat-send:disabled { opacity: 0.5; cursor: not-allowed; }
/* markdown inner styles handled by global CSS fallback */
</style>

<style>
/* Global fallback for markdown inside panel */
.kp-markdown pre { background: #1f2937; color: #e5e7eb; padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 12px; }
.kp-markdown code { font-size: 12px; }
.kp-markdown p code { background: #f3f4f6; color: #374151; padding: 2px 5px; border-radius: 4px; }
.dark .kp-markdown p code { background: #374151; color: #e5e7eb; }
.kp-markdown table { width: 100%; border-collapse: collapse; }
.kp-markdown th, .kp-markdown td { border: 1px solid var(--border-color, #e5e7eb); padding: 6px 8px; font-size: 12px; }
.kp-markdown th { background: var(--bg, #f9fafb); }
.kp-chat-bubble pre { background: rgba(0,0,0,0.05); padding: 6px; border-radius: 6px; overflow-x: auto; font-size: 11px; }
</style>
```

- [ ] **Step 2: 验证无语法错误**

```bash
cd frontend && npx vue-tsc --noEmit src/components/practice/AiKpPanel.vue 2>/dev/null || npx eslint src/components/practice/AiKpPanel.vue 2>/dev/null; echo "check done"
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/practice/AiKpPanel.vue
git commit -m "feat: AiKpPanel 组件 — markdown 渲染、追问、加载/错误/空态"
```

---

### Task 9: PracticeView 修改

**Files:**
- Modify: `frontend/src/views/PracticeView.vue`

- [ ] **Step 1: 在 template 中手机壳外右侧添加触发按钮**

在现有题目区域 `<div class="flex-1 px-4 pb-4 overflow-y-auto">` 这一层外面，包裹一个居中布局，加入按钮和面板：

找到 `<div class="flex flex-col flex-1 relative">` 整行，保持此容器。在其内部、`<header>` 下方、题目区域之前，插入新的包裹层。但为了最小改动，采用以下方式：

在 `<div class="flex-1 px-4 pb-4 overflow-y-auto">` (题目区域) 的父级 `<div class="flex flex-col flex-1 relative">` 中，把题目区域 + 底部操作 + 底部栏 包裹在一个可变的弹性布局中。

简化：在 PracticeView 最外层容器内，修改结构为：

```vue
<template>
  <div class="flex flex-col flex-1 relative">
    <!-- 顶栏（不变） -->
    <header>...</header>
    <!-- 进度条（不变） -->
    <div class="h-1...">...</div>
    <!-- 翻页（不变） -->
    <div class="flex justify-between...">...</div>

    <!-- 新增：手机壳 + 按钮 + 面板 整体居中容器 -->
    <div class="kp-main-row" :class="{ 'kp-expanded': aiOpen }">
      <!-- 手机壳区域（原题目区域 + 底部操作 + 底部栏） -->
      <div class="kp-phone-area">
        <!-- 题目区域 -->
        <div class="flex-1 px-4 pb-4 overflow-y-auto">
          ...
        </div>
        <!-- 底部操作 -->
        <div class="px-4 pb-3">...</div>
        <!-- 底部 -->
        <div class="flex items-center...">...</div>
      </div>

      <!-- 触发按钮（竖排，手机壳外右侧） -->
      <button v-if="kpEnabled && !aiOpen" @click="openAiPanel" class="kp-trigger-btn">
        <span class="kp-trigger-text">知识点解析</span>
      </button>

      <!-- AI 面板 -->
      <AiKpPanel
        v-if="aiOpen"
        :content="aiContent"
        :loading="aiLoading"
        :error="aiError"
        @close="closeAiPanel"
        @reanalyze="reanalyze"
        @chat="onChat"
      />
    </div>

    <!-- 答题卡 (不变) -->
    <!-- 设置窗 (不变) -->
  </div>
</template>
```

- [ ] **Step 2: 在 script setup 中添加 import 和状态**

```javascript
// 在现有 import 之后添加
import { checkKp, analyzeKp, chatKp } from '../api/knowledge_point'
import AiKpPanel from '../components/practice/AiKpPanel.vue'

// 在现有 ref 声明之后添加
const kpEnabled = ref(false)
const aiOpen = ref(false)
const aiLoading = ref(false)
const aiContent = ref('')
const aiError = ref('')
const aiQuestionId = ref(null)
const chatMessages = ref([])

// 在 onMounted 中添加
onMounted(async () => {
  // ... existing code ...
  try {
    const r = await checkKp()
    kpEnabled.value = r.kp_enabled
  } catch { /* not enabled */ }
})
```

- [ ] **Step 3: 添加方法**

```javascript
async function openAiPanel() {
  aiOpen.value = true
  aiQuestionId.value = question.value?.id
  aiError.value = ''
  aiContent.value = ''
  chatMessages.value = []
  await loadAnalysis()
}

async function loadAnalysis() {
  if (!question.value?.id) return
  aiLoading.value = true
  aiError.value = ''
  const qid = question.value.id
  try {
    const r = await analyzeKp(qid)
    if (aiQuestionId.value !== qid) return // 竞态丢弃
    aiContent.value = r.analysis_md
  } catch (e) {
    if (aiQuestionId.value !== qid) return
    aiError.value = e.response?.data?.detail || e.message || '解析失败'
  } finally {
    if (aiQuestionId.value === qid) aiLoading.value = false
  }
}

async function reanalyze() {
  if (!question.value?.id) return
  if (!confirm('将重新调用 AI 分析当前题目的知识点，是否继续？')) return
  aiLoading.value = true
  aiError.value = ''
  const qid = question.value.id
  try {
    const r = await analyzeKp(qid, true)
    if (aiQuestionId.value !== qid) return
    aiContent.value = r.analysis_md
  } catch (e) {
    if (aiQuestionId.value !== qid) return
    aiError.value = e.response?.data?.detail || e.message || '重新解析失败'
  } finally {
    if (aiQuestionId.value === qid) aiLoading.value = false
  }
}

function closeAiPanel() {
  aiOpen.value = false
  aiContent.value = ''
  aiError.value = ''
  chatMessages.value = []
}

async function onChat(messages, resolve, reject) {
  try {
    const r = await chatKp(question.value.id, messages)
    resolve(r.reply)
  } catch (e) {
    reject(e)
  }
}
```

- [ ] **Step 4: 切题行为**

在现有的 `watch` 或切题逻辑（`nextQuestion`、`prevQuestion` 函数）中，如果 `aiOpen` 为 true，自动调用 `loadAnalysis()`：

```javascript
// 在 nextQuestion/prevQuestion 等切题函数末尾添加
if (aiOpen.value) {
  aiQuestionId.value = question.value?.id
  aiError.value = ''
  aiContent.value = ''
  await loadAnalysis()
}
```

- [ ] **Step 5: 添加 CSS**

```css
<style scoped>
.kp-main-row {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  flex: 1;
  overflow: hidden;
  gap: 0;
  transition: all 0.3s ease;
}
.kp-main-row.kp-expanded {
  gap: 12px;
}
.kp-phone-area {
  display: flex;
  flex-direction: column;
  flex: 1;
  max-width: 500px;
  min-width: 300px;
}
.kp-trigger-btn {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  padding: 14px 8px;
  border-radius: 8px;
  border: 1px solid #c4b5fd;
  background: #ede9fe;
  color: #7c3aed;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
  align-self: stretch;
  min-height: 160px;
}
.kp-trigger-btn:hover { background: #ddd6fe; }
.dark .kp-trigger-btn { background: #1e1b4b; border-color: #6d28d9; color: #a78bfa; }
.dark .kp-trigger-btn:hover { background: #312e81; }
</style>
```

- [ ] **Step 6: 编译验证**

```bash
cd frontend && npx vite build --mode development 2>&1 | tail -20
```

Expected: build 成功，无 error

- [ ] **Step 7: 提交**

```bash
git add frontend/src/views/PracticeView.vue
git commit -m "feat: PracticeView 接入 AI 知识点解析面板"
```

---

### Task 10: 管理后台 — 用户列表加 kp 开关

**Files:**
- Modify: `frontend/src/views/admin/AdminUsers.vue`

- [ ] **Step 1: 在表格 thead 中添加列头**

```html
<!-- 在现有 <th class="py-2 w-28">操作</th> 之前添加 -->
<th class="py-2 pr-2 w-20">AI知识点</th>
```

- [ ] **Step 2: 在表格 tbody 中每行添加 toggle 单元格**

```html
<!-- 在现有 <td class="py-2 text-xs flex gap-1"> 操作列之前添加 -->
<td class="py-2 pr-2 text-xs">
  <button
    @click="toggleKp(u)"
    :class="kpMap[u.student_id] ? 'bg-green text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-400'"
    class="w-10 h-5 rounded-full relative transition-colors"
  >
    <span
      class="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform"
      :class="kpMap[u.student_id] ? 'translate-x-5' : 'translate-x-0.5'"
    ></span>
  </button>
</td>
```

- [ ] **Step 3: 在 script setup 中添加状态与方法**

```javascript
// 添加
import api from '../../api'

const kpMap = ref({})

// 在 fetchList 之后调用 fetchKpMap
async function fetchKpMap() {
  try {
    const { data } = await api.get('/admin/kp-access')
    const map = {}
    data.items.forEach(i => { map[i.student_id] = i.kp_enabled })
    kpMap.value = map
  } catch { /* ignore */ }
}

// 修改 onMounted / fetchList 也调 fetchKpMap
onMounted(() => { fetchList(); fetchKpMap() })

async function toggleKp(u) {
  const newVal = !kpMap.value[u.student_id]
  kpMap.value[u.student_id] = newVal
  try {
    await api.post('/admin/kp-access', { student_id: u.student_id, enabled: newVal })
  } catch {
    kpMap.value[u.student_id] = !newVal
  }
}
```

- [ ] **Step 4: 编译验证**

```bash
cd frontend && npx vite build --mode development 2>&1 | tail -5
```

Expected: build 成功

- [ ] **Step 5: 提交**

```bash
git add frontend/src/views/admin/AdminUsers.vue
git commit -m "feat: 管理后台用户列表添加 AI知识点 开关"
```

---

### Task 11: 全链路构建验证

- [ ] **Step 1: 后端启动测试**

```bash
cd backend && timeout 3 python -c "
from app.services.knowledge_point import init_kp_db
init_kp_db()
from app.main import app
print('Backend OK')
" 2>&1
```

Expected: `Backend OK`，无 traceback

- [ ] **Step 2: 前端构建**

```bash
cd frontend && npx vite build 2>&1 | tail -10
```

Expected: 构建成功

- [ ] **Step 3: 检查数据库文件**

```bash
ls -la data/ai_kp.db 2>/dev/null && echo "ai_kp.db created" || echo "ai_kp.db will be created on startup"
```

- [ ] **Step 4: 提交（如有遗留变更）**

```bash
git status
git add -A  # 仅如有构建产物等必要文件
git diff --cached --stat
git commit -m "chore: 全链路构建验证通过"
```

---

## 执行顺序

```
Task 1  (模型切换)         —— 1 分钟
Task 2  (服务层)           —— 5 分钟
Task 3  (路由层)           —— 3 分钟
Task 4  (main.py 注册)     —— 2 分钟
Task 5  (admin 端点)       —— 3 分钟  ← 后端完备
Task 6  (前端 npm)         —— 2 分钟
Task 7  (前端 api)         —— 1 分钟
Task 8  (AiKpPanel)        —— 10 分钟
Task 9  (PracticeView)     —— 8 分钟
Task 10 (AdminUsers)       —— 3 分钟  ← 前端完备
Task 11 (全链路验证)       —— 3 分钟
```

Tasks 1-5 间有顺序依赖（服务→路由→注册）。Tasks 6-10 间 Task 8 依赖 7，9 依赖 8，10 独立。Task 11 最后。
