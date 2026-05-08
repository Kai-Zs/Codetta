# Codetta · 练笔小筑

一题一阶，拾级而上。

Python 刷题练习应用，622 道题库。

## 技术栈

- 前端：Vue 3 + Vite（SPA），Tailwind CSS v4
- 后端：Python FastAPI + SQLite（单文件数据库）
- AI 判题：DeepSeek API（40s 超时）

## 项目结构

```
practice/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置（.env 加载）
│   │   ├── database.py          # SQLite 建表 + 连接（WAL 模式）
│   │   ├── auth.py              # itsdangerous token 签发/鉴权
│   │   ├── schemas.py           # Pydantic 模型
│   │   ├── routers/             # API 路由
│   │   └── services/            # 业务逻辑
│   ├── seed/
│   │   └── seed.py              # 种子数据导入（Excel + HTML）
│   ├── deploy.sh                # 一键部署脚本
│   └── data/
│       └── lianbi.db            # SQLite 数据库
├── frontend/
│   └── src/
│       ├── views/               # 页面组件
│       ├── components/          # 通用/题型组件
│       ├── stores/              # Pinia stores
│       ├── router/              # Vue Router + 守卫
│       └── api/                 # axios API 层
├── assets/                      # 静态资源
└── docs/                        # 设计文档
```

## Ubuntu 部署（生产环境）

### 前置要求

- Ubuntu 22.04+，已安装 Nginx / OpenResty
- 域名已配置 SSL（如 kaizs.cn）

### 后端一键部署

```bash
# 首次：克隆 + 部署（替换 sk-xxx 为你的 DeepSeek API Key）
git clone https://github.com/Kai-Zs/Codetta.git /var/www/codetta
cd /var/www/codetta/backend
bash deploy.sh sk-你的DeepSeek_API_Key

# 后续更新
git -C /var/www/codetta pull && bash /var/www/codetta/backend/deploy.sh
```

后端监听 `127.0.0.1:8765`，通过 systemd 管理：
```bash
systemctl status codetta     # 查看状态
journalctl -u codetta -f     # 查看日志
```

### Nginx 反向代理

在 server 块中添加：

```nginx
# 前端静态文件（如放在 /codetta 子路径）
location /codetta {
    try_files $uri $uri/ /codetta/index.html;
}

# 后端 API
location /api {
    proxy_pass http://127.0.0.1:8765;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_read_timeout 60s;
}
```

### 前端构建部署

```bash
cd frontend
npm install
npm run build
# 将 dist/ 内容复制到 Nginx 网站目录
cp -r dist/* /opt/1panel/www/sites/kaizs.cn/index/codetta/
```

> 前端配置了 `base: '/codetta/'`，如需改为其他子路径，修改 `vite.config.js` 和 `router/index.js` 后重新构建。

## 本地开发

### 后端

```bash
cd backend
pip install fastapi uvicorn python-dotenv openpyxl httpx itsdangerous bcrypt python-docx
# 创建 .env 文件：DEEPSEEK_API_KEY=你的Key
python -m uvicorn app.main:app --reload --port 8765
```

### 前端

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173，自动代理 /api → 127.0.0.1:8765
```

### 重新导入题库

```bash
cd backend
python -m seed.seed    # ⚠️ 会清空所有用户进度
```

## 数据库

| 表 | 内容 |
|------|------|
| users | 学生用户（学号、PIN bcrypt、偏好设置） |
| questions | 622 题（单选 194 / 判断 194 / 填空 144 / 编程 86，活跃 618） |
| progress | 作答记录（每次提交 INSERT 新行，保留历史） |

## 种子数据清洗

- Excel 题号格式化、`$` 转义残留清洗
- 单选题：选项解析为 JSON，答案匹配字母 A/B/C/D
- 填空题：`$` 分隔，拆分为 answer_parts JSON
- 编程题：HTML 表格解析，template（骨架）+ answer_code（完整代码），保留缩进
- 8.33-8.36 无答案停用

## 许可证

GPL v3
