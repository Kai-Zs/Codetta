"""题库路由"""
from fastapi import APIRouter, Depends, Query, HTTPException
from ..auth import get_user_id
from ..services.questions import list_questions, get_question

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("")
def list_q(
    type: str = Query(""),
    chapter: str = Query(""),
    page: int = Query(1, ge=1),
    per: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_user_id),
):
    return list_questions(type=type, chapter=chapter, page=page, per=per)


@router.get("/{question_id}")
def get_q(question_id: int, user_id: int = Depends(get_user_id)):
    try:
        return get_question(question_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
