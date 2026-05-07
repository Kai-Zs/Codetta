"""判题路由"""
import concurrent.futures
from fastapi import APIRouter, Depends, HTTPException
from ..schemas import JudgeRequest
from ..auth import get_user_id
from ..services.judge import judge_code

router = APIRouter(prefix="/api/judge", tags=["judge"])


@router.post("/code")
def judge(body: JudgeRequest, user_id: int = Depends(get_user_id)):
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(judge_code, body.question_id, body.user_code)
            return future.result(timeout=40)
    except concurrent.futures.TimeoutError:
        raise HTTPException(408, "判题超时，请手动判断")
    except ValueError as e:
        raise HTTPException(400, str(e))
