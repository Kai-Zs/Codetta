"""进度路由"""
from fastapi import APIRouter, Depends, Query
from ..schemas import ProgressSubmit, RemoveWrongRequest
from ..auth import get_user_id
from ..services import progress as svc

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("")
def get_p(user_id: int = Depends(get_user_id)):
    return svc.get_progress(user_id)


@router.post("")
def submit(body: ProgressSubmit, user_id: int = Depends(get_user_id)):
    return svc.submit_progress(user_id, body.model_dump())


@router.get("/wrong")
def list_wrong(
    type: str = Query(""),
    chapter: str = Query(""),
    page: int = Query(1, ge=1),
    per: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_user_id),
):
    return svc.get_wrong(user_id, type=type, chapter=chapter, page=page, per=per)


@router.post("/remove-wrong")
def remove_wrong(body: RemoveWrongRequest, user_id: int = Depends(get_user_id)):
    svc.remove_from_wrong(user_id, body.question_ids)
    return {"ok": True}


@router.delete("")
def clear(user_id: int = Depends(get_user_id)):
    svc.clear_progress(user_id)
    return {"ok": True}
