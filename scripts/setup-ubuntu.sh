#!/bin/bash
set -e

echo "=== Codetta 后端安装脚本 (Ubuntu) ==="

# 检查 Python
if ! command -v python3 &>/dev/null; then
    echo ">> 安装 Python 3..."
    sudo apt update && sudo apt install -y python3 python3-pip python3-venv
fi

echo "Python: $(python3 --version)"

# 项目目录
APP_DIR="$(cd "$(dirname "$0")/../backend" && pwd)"
cd "$APP_DIR"

# 虚拟环境
if [ ! -d "venv" ]; then
    echo ">> 创建虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate

# 依赖
echo ">> 安装 Python 依赖..."
pip install --upgrade pip
pip install fastapi uvicorn openpyxl bcrypt sqlalchemy httpx itsdangerous

# 初始化数据库
echo ">> 初始化数据库..."
python3 -m app.database 2>/dev/null || python3 -c "from app.database import init_db; init_db()"

# 导入种子数据
echo ">> 导入种子数据..."
python3 seed/seed.py

# 创建 systemd 服务（可选）
echo ""
read -p "创建 systemd 自启动服务? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/codetta.service"
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Codetta API Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="SECRET_KEY=$(python3 -c 'import secrets;print(secrets.token_hex(32))')"
Environment="DEEPSEEK_API_KEY=your-deepseek-api-key"
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8765
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable codetta
    echo ">> 服务已创建: sudo systemctl start codetta"
    echo ">> 注意: 请编辑 $SERVICE_FILE 设置 DEEPSEEK_API_KEY"
fi

echo ""
echo "=== 安装完成 ==="
echo "启动: cd $APP_DIR && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8765"
echo "或: sudo systemctl start codetta"
