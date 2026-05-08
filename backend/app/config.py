import os
from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(_env_path)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "lianbi.db")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_TIMEOUT = 40
ADMIN_PASSWORD = ""  # 暂不启用
SECRET_KEY = os.environ.get("SECRET_KEY", "codetta-dev-secret-change-in-production")
TOKEN_EXPIRE_HOURS = 24
PIN_MAX_ATTEMPTS = 5
PIN_LOCK_MINUTES = 15
