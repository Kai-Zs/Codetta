# 练笔小筑

一题一阶，拾级而上。

Python 刷题练习应用，面向班级 2544（31 人），622 道题库。

## 技术栈

- 前端：Vue 3 + Vite（SPA），Capacitor 打包 Android APK，PWA 安装 Windows
- 后端：Python FastAPI + SQLite（单文件数据库）
- AI 判题：DeepSeek API（40s 超时）

## 项目结构

```
practice/
├── backend/
│   ├── app/
│   │   ├── config.py           # 配置（数据库路径、API Key）
│   │   ├── database.py         # SQLite 建表 + 连接（WAL 模式）
│   │   ├── preview_server.py   # 临时数据库预览（端口 8765）
│   │   ├── routers/            # API 路由（待开发）
│   │   └── services/           # 业务逻辑（待开发）
│   ├── seed/
│   │   └── seed.py             # 种子数据导入脚本
│   └── data/
│       └── lianbi.db           # SQLite 数据库（622 题 + 31 用户）
├── data/                       # 原始 Excel/HTML 数据（gitignore）
├── scripts/                    # 数据检查辅助脚本
├── assets/                     # 头像、图标等静态资源
└── docs/                       # 设计文档
```

## 数据库

| 表 | 内容 |
|------|------|
| users | 31 名学生（学号、PIN、偏好设置） |
| questions | 622 题（单选 194 / 判断 194 / 填空 144 / 编程 86，活跃 618） |
| progress | 作答记录（每次提交 INSERT 新行，保留历史） |

## 已完成的种子数据清洗

- Excel 题号文本格式化（修复 1.10→1.1 浮点精度丢失）
- `$` 转义残留清洗（内容/标题字段）
- 单选题：选项解析为 JSON，答案匹配为字母 A/B/C/D
- 填空题：`$` 全当分隔符，拆分为 answer_parts JSON
- 编程题：HTML 表格解析，template（纯黑骨架）+ answer_code（完整代码）
- 8.33-8.36 无答案停用

### 许可证

GPL v3

## 快速开始

```bash
# 导入种子数据（首次或重置）
python backend/seed/seed.py

# 启动数据库预览
python backend/app/preview_server.py
# 浏览器打开 http://127.0.0.1:8765

# 安装后端依赖
pip install fastapi uvicorn openpyxl bcrypt
```
