# AI 知识点解析 — 设计 Spec

**日期**: 2026-05-11  
**状态**: 待实现  
**分支**: main

---

## 1. 功能概述

做题页面新增 "AI 知识点解析" 功能。用户点击手机壳右侧的竖排触发按钮，AI 分析当前题目涉及的知识点（简要介绍 + 重难点 + 易错点），结果以 Markdown 渲染展示在右侧面板。支持重新解析和追问。所有数据存入独立 SQLite 数据库，不修改原有数据库结构和数据。

权限通过独立表 `kp_access` 管理，默认仅对学号 `2025006708` 开放，管理员可在后台用户管理页开关。

---

## 2. 后端设计

### 2.1 独立数据库 `data/ai_kp.db`

完全独立于主库 `data/lianbi.db`，自有连接管理（WAL + busy_timeout）。

```sql
CREATE TABLE IF NOT EXISTS kp_cache (
    question_id INTEGER PRIMARY KEY,
    analysis_md  TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS kp_access (
    student_id TEXT PRIMARY KEY,
    enabled    INTEGER NOT NULL DEFAULT 1
);

-- 初始数据
INSERT OR IGNORE INTO kp_access (student_id, enabled) VALUES ('2025006708', 1);
```

表在 `main.py` 的 startup 事件中自动创建。

### 2.2 文件变更

| 文件 | 变化 |
|------|------|
| `backend/app/services/knowledge_point.py` | **新建** — AI 调用、缓存读写、追问、token 截断 |
| `backend/app/routers/knowledge_point.py` | **新建** — 3 个 API 端点 |
| `backend/app/main.py` | **修改** — 注册路由 + startup 事件建 `ai_kp.db` 表 |
| `backend/app/routers/admin.py` | **修改** — 新增 kp-access 端点 |
| `backend/app/services/auth.py` | **修改** — `/auth/me` 返回 `kp_enabled` 字段 |
| `backend/app/services/judge.py` | **修改** — 模型改为 `deepseek-v4-flash` |

### 2.3 模型变更

`backend/app/services/judge.py` 第 55 行：`deepseek-chat` → `deepseek-v4-flash`

知识点解析与追问均使用 `deepseek-v4-flash`。

### 2.4 API 端点

| 方法 | 路径 | 请求体 | 说明 |
|------|------|--------|------|
| `POST` | `/api/kp/analyze` | `{question_id}` | 有缓存返回缓存，无缓存调 AI 后存入 |
| `POST` | `/api/kp/analyze` | `{question_id, force: true}` | 强制重新解析，覆盖缓存 |
| `POST` | `/api/kp/chat` | `{question_id, messages: [{role, content}]}` | 追问，不存库 |

所有端点入口校验权限：查 `kp_access` 表，用户不在白名单或 `enabled=0` 则返回 403。

权限校验逻辑抽取为公共函数 `check_kp_access(user_id)`，在 `knowledge_point.py` 服务层实现。

`/api/auth/me` 响应新增 `kp_enabled` 布尔字段，供前端判断是否展示触发按钮。

### 2.5 Prompt 设计

#### 解析 Prompt

根据题型 `type` 选择答案字段：编程题取 `answer_code`，其他取 `answer`（有 `answer_parts` 则拼接）。`options` 和 `note` 存在时才拼入。

```
你是一个 Python 知识点分析助手。请根据以下题目信息，提炼涉及的知识点，
简要介绍，并指出重点难点和易错点。

【题号】{q_number}
【章节】{chapter}
【题型】{type}
【题目】{content}
【答案】{answer}
【选项】{options}          ← 仅选择题
【解析/备注】{note}         ← 仅当存在

请自由组织输出结构，使用 markdown 格式，可包含代码示例和公式。
```

输出格式不限制死板结构，AI 自由组织。

#### 追问 Prompt

```
你是一个 Python 学习助教。以下是一道题目的信息和 AI 已给出的知识点解析，
请根据用户的追问继续解答。

【题目信息】
题号：{q_number} | 章节：{chapter} | 题型：{type}
题目：{content}
答案：{answer}

【知识点解析】
{analysis_md}

请结合以上上下文回答用户的问题。
```

后端固定 system prompt，用户只能追加 user role 消息。每次请求前端传完整历史，后端限制最多 20 轮；超过 20 轮截断保留最近 15 轮。

Token 预算：消息总字符数超过 8000 时，丢弃最早的非 system 消息直到总量 < 8000。

### 2.6 竞态保护

- **后端**：同一 `question_id` 的并发解析请求通过 `threading.Lock`（以 question_id 为 key）保证只调一次 DeepSeek，其他等待结果
- **前端**：`aiLoading` 期间禁用解析/重新解析按钮

---

## 3. 前端设计

### 3.1 新增/修改文件

| 文件 | 变化 |
|------|------|
| `frontend/src/api/knowledge_point.js` | **新建** — `analyzeKp(questionId, force?)`, `chatKp(questionId, messages)` |
| `frontend/src/components/practice/AiKpPanel.vue` | **新建** — AI 面板全功能 |
| `frontend/src/views/PracticeView.vue` | **修改** — 布局切换、触发按钮、状态管理 |
| `frontend/src/views/admin/` | **修改** — 用户列表加 "AI知识点" 开关列 |

### 3.2 依赖

```bash
npm install marked highlight.js katex dompurify
```

全局导入 `katex/dist/katex.min.css`。

### 3.3 布局与交互

```
默认态（面板关闭）：                面板打开态：
                                     整体居中
        ┌──────────┐            ┌──────────┬────────────┐
        │          │ ┌────┐     │          │  ✕ 关闭     │
        │  手机壳  │ │知  │     │  手机壳  │  重新解析    │
        │          │ │识  │     │          │            │
        │          │ │点  │  →  │          │ MD 内容区   │
        │          │ │分  │     │          │ (可滚动)    │
        │          │ │析  │     │          │            │
        │          │ │    │     │          │ ─────────  │
        │          │ └────┘     │          │ 追问消息    │
        │          │            │          │ 追问输入框  │
        └──────────┘            └──────────┴────────────┘
```

- **触发按钮**：竖排条形，蓝色主题，文字 "知识点解析"，在手机壳外右侧，与手机壳底部对齐
- **打开面板**：按钮隐藏，手机壳 + AI 面板整体居中，AI 区左 1/3 处约在屏幕中心
- **关闭面板**：点击 AI 区右上角 ✕，按钮重新显示，清空追问历史
- **AI 面板宽度**：`400px` 固定，内侧可滚动
- **面板最小高度**：`500px`，不足时撑开

### 3.4 切题行为

切换题目时面板保持打开，自动加载新题缓存。无缓存则显示"点击解析查看知识点"占位状态，不自动触发 DeepSeek。Loading 中切题：请求返回时比对 `question_id`，不匹配则丢弃结果。

### 3.5 状态设计

```js
// PracticeView
aiOpen: false,
aiQuestionId: null,   // 当前面板对应的题目 ID
aiContent: '',        // markdown 字符串
aiLoading: false,
aiError: '',          // 错误信息，非空展示错误态

// AiKpPanel
chatMessages: [],     // [{role, content}]
chatLoading: false,

// Admin (user list)
kpAccessMap: {},      // { student_id: boolean }
```

### 3.6 Loading / 错误 / 空态

- **解析加载中**：骨架屏 + "AI 正在分析知识点…" + spinner
- **超时（40s）**："分析超时，请重试" + 重新解析按钮
- **网络异常**：具体错误信息 + 重新解析按钮
- **无权限（403）**：按钮不可见（后端 `/api/auth/me` 需额外返回 `kp_enabled: true/false`，前端据此显隐按钮）
- **无缓存状态**："点击「AI 知识点解析」按钮获取分析" 占位提示
- **追问加载中**：发送按钮变 spinner

### 3.7 重新解析确认

点击"重新解析"弹出确认对话框："将重新调用 AI 分析当前题目的知识点，是否继续？" 确认后执行，覆盖缓存。

### 3.8 Markdown 渲染

- `marked` 渲染 markdown，配置 `breaks: true`, `gfm: true`
- `dompurify` sanitize HTML，防止 XSS
- `highlight.js` 代码高亮（主题：`github-dark`）
- `katex` 渲染数学公式：自定义 marked renderer，拦截 `$$...$$` 和 `$...$` 表达式

### 3.9 追问区

- 追问消息列表：气泡样式，AI 消息左对齐 + 用户消息右对齐
- AI 追问回复同样以 markdown 渲染
- 输入框固定在面板底部（`position: sticky; bottom: 0`），聚焦时 `scrollIntoView`
- 回车发送，Shift+回车换行

---

## 4. 管理后台

### 4.1 后端

在 `backend/app/routers/admin.py` 新增两个端点：

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/admin/kp-access` | 返回所有用户 `{student_id, name, kp_enabled}` |
| `POST` | `/api/admin/kp-access` | `{student_id, enabled}` 设置开关 |

需要验证 `X-Admin-Password`（复用现有 admin auth）。

### 4.2 前端

在管理后台用户管理页面，每个用户行增加一列 "AI知识点" 开关（toggle switch），调用上述 API。

---

## 5. 安全与边界

| 项 | 措施 |
|----|------|
| 权限校验 | 每个端点入口查 `kp_access` 表 |
| XSS | `dompurify` sanitize markdown 渲染输出 |
| 追问注入 | 后端固定 system prompt，用户仅提供 user message |
| 竞态 - 解析 | 前端 aiLoading lock + 后端 threading.Lock |
| 竞态 - 切题 | 前端比对 question_id，不匹配丢弃 |
| Token 溢出 | 追问消息 > 8000 字符时截断最早非 system 消息；最多 20 轮 |
| API 滥用 | 同一 question_id 有缓存直接返回，不重复调用 |

### 不涉及

- 不修改 `questions`、`progress`、`users` 表结构或数据
- 不修改 `database.py` 的 `get_db()` / `init_db()`
- 不影响现有判题、做题、导出、错题本等功能
- 追问不存库，刷新页面后消失

---

## 6. 测试要点

1. 白名单用户（2025006708）可见按钮，非白名单用户不可见
2. 点击按钮面板打开，布局正确（手机壳左移 + AI 面板右显）
3. 首次解析调 AI，再次打开命中缓存
4. 重新解析覆盖缓存，两次结果可不同
5. 追问多轮正常，刷新消失
6. 追问 > 20 轮截断
7. 管理后台开关即时生效
8. 切题时面板状态正确
9. 超时/网络错误 UI 反馈
10. Markdown 含代码块、公式正常渲染
11. XSS payload 被 sanitize
12. 无权限用户直接 curl API 返回 403
