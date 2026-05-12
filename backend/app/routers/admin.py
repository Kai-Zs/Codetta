"""管理员后台路由"""
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from ..schemas_admin import QuestionUpdate, QuestionCreate, PasswordChange
from ..services import admin as svc

router = APIRouter(prefix="/api/admin", tags=["admin"])


def verify_admin(x_admin_password: str = Header(None)):
    if not x_admin_password or not svc.verify_admin(x_admin_password):
        raise HTTPException(403, "管理员密码错误")
    return True


# === 验证（无需鉴权） ===
@router.post("/verify")
def verify(x_admin_password: str = Header(None)):
    if svc.verify_admin(x_admin_password or ""):
        return {"ok": True}
    raise HTTPException(403, "密码错误")


# === 题目管理 ===
@router.get("/questions", dependencies=[Depends(verify_admin)])
def list_questions(
    type: str = Query(""),
    chapter: str = Query(""),
    q_number: str = Query(""),
    page: int = Query(1, ge=1),
    per: int = Query(20, ge=1, le=100),
):
    return svc.list_questions(type=type, chapter=chapter, q_number=q_number, page=page, per=per)


@router.put("/questions/{question_id}", dependencies=[Depends(verify_admin)])
def update_question(question_id: int, body: QuestionUpdate):
    return svc.update_question(question_id, body.model_dump(exclude_none=True))


@router.post("/questions", dependencies=[Depends(verify_admin)])
def create_question(body: QuestionCreate):
    return svc.create_question(body.model_dump())


@router.put("/questions/{question_id}/active", dependencies=[Depends(verify_admin)])
def toggle_active(question_id: int, active: int = Query(...)):
    return svc.toggle_active(question_id, active)


# === 用户管理 ===
@router.get("/users", dependencies=[Depends(verify_admin)])
def list_users(
    search: str = Query(""),
    page: int = Query(1, ge=1),
    per: int = Query(20, ge=1, le=100),
):
    return svc.list_users(search=search, page=page, per=per)


@router.get("/users/{user_id}", dependencies=[Depends(verify_admin)])
def get_user_detail(user_id: int):
    try:
        return svc.get_user_detail(user_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/users/{user_id}/reset-pin", dependencies=[Depends(verify_admin)])
def reset_user_pin(user_id: int):
    svc.reset_user_pin(user_id)
    return {"ok": True}


# === 统计 ===
@router.get("/stats", dependencies=[Depends(verify_admin)])
def get_stats():
    return svc.get_stats()


# === 系统设置 ===
@router.get("/settings", dependencies=[Depends(verify_admin)])
def get_settings():
    return {"maintenance": svc.get_maintenance_status()}


@router.post("/maintenance", dependencies=[Depends(verify_admin)])
def toggle_maintenance(enable: int = Query(...)):
    svc.toggle_maintenance(bool(enable))
    return {"ok": True, "maintenance": bool(enable)}


@router.put("/password", dependencies=[Depends(verify_admin)])
def change_password(body: PasswordChange):
    if not svc.verify_admin(body.old_password):
        raise HTTPException(400, "旧密码错误")
    svc.change_admin_password(body.new_password)
    return {"ok": True}


@router.post("/reload-seed", dependencies=[Depends(verify_admin)])
def reload_seed():
    try:
        svc.reload_seed()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(500, f"重载失败: {str(e)[:100]}")


@router.get("/kp-access", dependencies=[Depends(verify_admin)])
def list_kp_access(search: str = Query("")):
    return {"items": svc.list_kp_access(search)}


@router.post("/kp-access", dependencies=[Depends(verify_admin)])
def set_kp_access(body: dict):
    student_id = body.get("student_id", "")
    enabled = body.get("enabled", False)
    if not student_id:
        raise HTTPException(400, "student_id 必填")
    svc.set_kp_access(student_id, enabled)
    return {"ok": True}
