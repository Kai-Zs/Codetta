"""Token 签发与鉴权依赖"""
from itsdangerous import URLSafeTimedSerializer
from fastapi import Depends, HTTPException, Header
from .config import SECRET_KEY, TOKEN_EXPIRE_HOURS

serializer = URLSafeTimedSerializer(SECRET_KEY)


def create_token(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})


def verify_token(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid token")
    try:
        payload = serializer.loads(authorization[7:], max_age=TOKEN_EXPIRE_HOURS * 3600)
    except Exception:
        raise HTTPException(401, "Token expired or invalid")
    return payload


def get_user_id(payload: dict = Depends(verify_token)) -> int:
    return payload["user_id"]
