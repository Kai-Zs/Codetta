#!/bin/bash
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_NAME="codetta"
PYTHON="python3"
VENV_DIR="$APP_DIR/venv"

# 接受命令行参数作为 API Key
DEEPSEEK_KEY="${1:-}"

echo "=== Codetta 后端部署 ==="

# 1. 虚拟环境（自动安装 python3-venv 如缺失）
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "[1/5] 创建虚拟环境..."
    rm -rf "$VENV_DIR"
    $PYTHON -m venv "$VENV_DIR" 2>/dev/null || {
        echo "  安装 python3-venv..."
        sudo apt install -y -q python3-venv
        $PYTHON -m venv "$VENV_DIR"
    }
fi
source "$VENV_DIR/bin/activate"

# 2. 依赖
echo "[2/5] 安装依赖..."
pip install -q --upgrade pip
pip install -q fastapi uvicorn python-dotenv openpyxl httpx itsdangerous python-docx

# 3. .env
if [ -n "$DEEPSEEK_KEY" ]; then
    echo "[3/5] 写入 API Key..."
    echo "DEEPSEEK_API_KEY=$DEEPSEEK_KEY" > "$APP_DIR/.env"
elif [ -f "$APP_DIR/.env" ]; then
    echo "[3/5] .env 已存在，跳过"
else
    echo "[3/5] .env 不存在，请传入 API Key："
    echo "  bash deploy.sh sk-你的Key"
    exit 1
fi

# 4. systemd 服务
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
if [ ! -f "$SERVICE_FILE" ]; then
    echo "[4/5] 注册 systemd 服务..."
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Codetta Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/uvicorn app.main:app --host 127.0.0.1 --port 8765
Restart=always
EnvironmentFile=$APP_DIR/.env

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
else
    echo "[4/4] systemd 服务已存在，跳过注册"
fi

# 重启
sudo systemctl restart "$SERVICE_NAME"
sleep 2
sudo systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "=== 部署完成 ==="
echo "API 文档: http://127.0.0.1:8765/docs"
echo "查看日志: sudo journalctl -u $SERVICE_NAME -f"
