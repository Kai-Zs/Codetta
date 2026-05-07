# Codetta · 练笔小筑

一题一阶，拾级而上。

Python 刷题练习应用，622 道题库。

## 技术栈

- 前端：Vue 3 + Vite（SPA），Capacitor 打包 Android APK，PWA 安装 Windows
- 后端：Python FastAPI + SQLite（单文件数据库）
- AI 判题：DeepSeek API（40s 超时）

## 项目结构

```
practice/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口 + CORS
│   │   ├── config.py            # 配置
│   │   ├── database.py          # SQLite 建表 + 连接（WAL 模式）
│   │   ├── auth.py              # itsdangerous token 签发/鉴权
│   │   ├── schemas.py           # Pydantic 模型
│   │   ├── preview_server.py    # 数据库预览（端口 8765）
│   │   ├── routers/             # API 路由（auth/questions/progress/judge/export）
│   │   └── services/            # 业务逻辑
│   ├── seed/
│   │   └── seed.py              # 种子数据导入
│   └── data/
│       └── lianbi.db            # SQLite 数据库
├── frontend/
│   └── src/
│       ├── views/               # 页面组件
│       ├── components/          # 通用/题型组件
│       ├── stores/              # Pinia stores
│       ├── router/              # Vue Router + 守卫
│       └── api/                 # axios API 层
├── scripts/                    # 安装/辅助脚本
├── assets/                     # 静态资源
└── docs/                       # 设计文档 + 计划
```

## 数据库

| 表 | 内容 |
|------|------|
| users | 学生用户（学号、PIN bcrypt、偏好设置） |
| questions | 622 题（单选 194 / 判断 194 / 填空 144 / 编程 86，活跃 618） |
| progress | 作答记录（每次提交 INSERT 新行，保留历史） |

## Ubuntu 安装

### 自动安装

```bash
chmod +x scripts/setup-ubuntu.sh
./scripts/setup-ubuntu.sh
```

脚本会自动安装 Python 依赖、初始化数据库、导入种子数据，并可选创建 systemd 自启动服务。

### 手动安装

```bash
# 1. 安装 Python
sudo apt update && sudo apt install -y python3 python3-pip python3-venv

# 2. 进入后端目录
cd backend
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install fastapi uvicorn openpyxl bcrypt sqlalchemy httpx itsdangerous

# 4. 导入种子数据
python3 seed/seed.py

# 5. 设置环境变量
export DEEPSEEK_API_KEY="your-api-key"
export SECRET_KEY="$(python3 -c 'import secrets;print(secrets.token_hex(32))')"

# 6. 启动
uvicorn app.main:app --host 0.0.0.0 --port 8765
```

### 前端（开发）

```bash
cd frontend
npm install
npm run dev        # 开发模式，代理 API 到 localhost:8765
npm run build      # 生产构建到 dist/
```

## Windows 安装

```bash
# 后端依赖
pip install fastapi uvicorn openpyxl bcrypt sqlalchemy httpx itsdangerous

# 导入种子数据
python backend/seed/seed.py

# 启动后端
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8765

# 前端
cd frontend
npm install
npm run dev
```

## 已完成的种子数据清洗

- Excel 题号文本格式化（修复 1.10→1.1 浮点精度丢失）
- `$` 转义残留清洗（内容/标题字段）
- 单选题：选项解析为 JSON，答案匹配为字母 A/B/C/D
- 填空题：`$` 全当分隔符，拆分为 answer_parts JSON
- 编程题：HTML 表格解析，template（纯黑骨架）+ answer_code（完整代码）
- 8.33-8.36 无答案停用

## 许可证

GPL v3
