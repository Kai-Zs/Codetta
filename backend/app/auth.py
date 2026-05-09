"""Token 签发与鉴权依赖"""
import os
import json
from itsdangerous import URLSafeTimedSerializer
from fastapi import Depends, HTTPException, Header
from .config import SECRET_KEY, TOKEN_EXPIRE_HOURS, BASE_DIR

serializer = URLSafeTimedSerializer(SECRET_KEY)
TOKEN_VERSION_FILE = os.path.join(BASE_DIR, "data", "token_versions.json")


def _read_versions() -> dict:
    if not os.path.exists(TOKEN_VERSION_FILE):
        return {}
    with open(TOKEN_VERSION_FILE) as f:
        return json.load(f)


def _write_versions(versions: dict):
    os.makedirs(os.path.dirname(TOKEN_VERSION_FILE), exist_ok=True)
    with open(TOKEN_VERSION_FILE, "w") as f:
        json.dump(versions, f)


def bump_token_version(user_id: int):
    """PIN 重置后调用，使旧 token 失效"""
    versions = _read_versions()
    versions[str(user_id)] = versions.get(str(user_id), 0) + 1
    _write_versions(versions)


def create_token(user_id: int) -> str:
    versions = _read_versions()
    ver = versions.get(str(user_id), 0)
    return serializer.dumps({"user_id": user_id, "tv": ver})


def verify_token(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid token")
    try:
        payload = serializer.loads(authorization[7:], max_age=TOKEN_EXPIRE_HOURS * 3600)
    except Exception:
        raise HTTPException(401, "Token expired or invalid")
    # 检查 token 版本是否与当前一致
    versions = _read_versions()
    current_ver = versions.get(str(payload["user_id"]), 0)
    if payload.get("tv", 0) != current_ver:
        raise HTTPException(401, "Token revoked (PIN was reset)")
    return payload


def get_user_id(payload: dict = Depends(verify_token)) -> int:
    return payload["user_id"]
