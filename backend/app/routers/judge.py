"""判题路由"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from ..schemas import JudgeRequest
from ..auth import get_user_id
from ..services.judge import judge_code

router = APIRouter(prefix="/api/judge", tags=["judge"])


@router.post("/code")
async def judge(body: JudgeRequest, user_id: int = Depends(get_user_id)):
    try:
        return await asyncio.wait_for(judge_code(body.question_id, body.user_code), timeout=40)
    except asyncio.TimeoutError:
        raise HTTPException(408, "判题超时，请手动判断")
    except ValueError as e:
        raise HTTPException(400, str(e))
