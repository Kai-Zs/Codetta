# Codetta — API 设计文档

## 概述

后端 API 采用 RESTful 风格，token 鉴权（itsdangerous JWT，24h 过期）。

## 鉴权策略

| 接口 | 鉴权 |
|------|------|
| `POST /api/auth/login` | 无 |
| `POST /api/auth/verify-pin` | PIN 错误次数限制（5 次锁 15 分钟） |
| 其余所有接口 | token（Header: `Authorization: Bearer <token>`） |

token 载荷：`{user_id, exp}`，从 token 提取 user_id，不从 URL 传入。

## API 端点

### 认证

| 方法 | 路径 | 鉴权 | 入参 | 出参 | 说明 |
|------|------|------|------|------|------|
| POST | `/api/auth/login` | 无 | `{student_id: str}` | `{status, name, need_pin}` | 查名单，无记录则创建 |
| POST | `/api/auth/verify-pin` | 限次 | `{student_id, pin}` | `{token, user}` | 校验 PIN |
| POST | `/api/auth/set-pin` | token | `{pin}` 或 `{old_pin, new_pin}` | `{ok}` | 首次只需 pin，修改需 old_pin |
| GET | `/api/auth/me` | token | — | `{student_id, name, prog_mode, sound_on, vibrate_on}` | 当前用户信息 |
| PATCH | `/api/auth/settings` | token | `{prog_mode?, sound_on?, vibrate_on?}` | `{ok}` | 更新设置 |
| POST | `/api/admin/reset-pin` | 暂无 | `{student_id}` | `{ok}` | 重置 PIN |

status 枚举：
- `"need_pin"` — 已有 PIN，需验证
- `"need_setup"` — 首次登录，需设置 PIN

### 题库

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | `/api/questions` | `?type=&chapter=&page=1&per=20` | 分页列表，返回题号/题型/标题/章节，不含答案 |
| GET | `/api/questions/{id}` | — | 单题详情，含 options/answer_parts/template |

### 进度

| 方法 | 路径 | 入参 | 说明 |
|------|------|------|------|
| GET | `/api/progress` | `?mode=sequential` | 进度概览：正确率、完成数、下一未做题 |
| POST | `/api/progress` | `{question_id, answer_status, user_answer, mode?}` | 提交答案 |
| GET | `/api/progress/wrong` | `?type=&chapter=&page=1&per=20` | 错题列表 |
| POST | `/api/progress/remove-wrong` | `{question_ids: [int]}` | 批量移出错题本 |
| DELETE | `/api/progress` | — | 清空全部进度 |

### 判题

| 方法 | 路径 | 入参 | 出参 | 说明 |
|------|------|------|------|------|
| POST | `/api/judge/code` | `{question_id, user_code}` | `{is_correct, score, comment}` | DeepSeek 判题，40s 超时，`run_in_executor` 扔线程池 |

### 导出

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/export/wrong` | 导出错题 Excel（xlsx） |

## 文件结构

```
backend/app/
  main.py             # FastAPI + CORS + 路由注册
  config.py            # 配置（已有）
  database.py          # SQLite 建表 + 连接（需加 pin_attempts/pin_locked_until）
  schemas.py           # Pydantic 请求/响应模型
  auth.py              # itsdangerous token 签发/校验 + 鉴权依赖
  routers/
    auth.py            # /api/auth/*
    questions.py       # /api/questions/*
    progress.py        # /api/progress/*
    judge.py           # /api/judge/*
    export.py          # /api/export/*
  services/
    auth.py            # 认证业务逻辑
    questions.py       # 题库查询
    progress.py        # 进度增删改查
    judge.py           # DeepSeek API 调用
    export.py          # Excel 导出
```

## 数据库变更

users 表新增：

```sql
ALTER TABLE users ADD COLUMN pin_attempts INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN pin_locked_until TEXT;
```

## 安全

- PIN bcrypt 哈希存储
- PIN 错 5 次锁定 15 分钟（`pin_locked_until`）
- token 24h 过期
- 进度接口 user_id 从 token 提取，防止水平越权
- 学号前后端校验 10 位纯数字
- PIN 前后端校验 4 位数字
- 分页 per 限制 1-100
