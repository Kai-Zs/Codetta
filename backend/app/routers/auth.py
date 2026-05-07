"""认证路由"""
from fastapi import APIRouter, Depends, HTTPException
from ..schemas import LoginRequest, VerifyPinRequest, SetPinRequest, UpdateSettingsRequest
from ..auth import create_token, get_user_id
from ..services.auth import handle_login, verify_pin, set_pin, get_me, update_settings, reset_pin

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(body: LoginRequest):
    result = handle_login(body.student_id)
    if result["status"] == "need_setup":
        result["token"] = create_token(result["user_id"])
    return result


@router.post("/verify-pin")
def verify(body: VerifyPinRequest):
    try:
        result = verify_pin(body.student_id, body.pin)
    except ValueError as e:
        raise HTTPException(400, str(e))
    token = create_token(result["user_id"])
    user = get_me(result["user_id"])
    return {"token": token, "user": user}


@router.post("/set-pin")
def set_pin_route(body: SetPinRequest, user_id: int = Depends(get_user_id)):
    try:
        set_pin(user_id, body.pin, body.old_pin)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"ok": True}


@router.get("/me")
def me_route(user_id: int = Depends(get_user_id)):
    return get_me(user_id)


@router.patch("/settings")
def settings_route(body: UpdateSettingsRequest, user_id: int = Depends(get_user_id)):
    update_settings(user_id, body.model_dump(exclude_none=True))
    return {"ok": True}


@router.post("/admin/reset-pin")
def reset_pin_route(body: LoginRequest):
    reset_pin(body.student_id)
    return {"ok": True}
