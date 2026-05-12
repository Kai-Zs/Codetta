"""知识点解析路由"""
import concurrent.futures
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..auth import get_user_id
from ..services.knowledge_point import check_kp_access, analyze_kp, chat_followup

router = APIRouter(prefix="/api/kp", tags=["kp"])


class AnalyzeRequest(BaseModel):
    question_id: int
    force: bool = False


class ChatRequest(BaseModel):
    question_id: int
    messages: list[dict]


def require_kp_access(user_id: int = Depends(get_user_id)):
    if not check_kp_access(user_id):
        raise HTTPException(403, "此功能未对你开放")
    return user_id


@router.get("/check")
def check(user_id: int = Depends(get_user_id)):
    return {"kp_enabled": check_kp_access(user_id)}


@router.post("/analyze")
def analyze(body: AnalyzeRequest, user_id: int = Depends(require_kp_access)):
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(analyze_kp, body.question_id, body.force)
            return future.result(timeout=45)
    except concurrent.futures.TimeoutError:
        raise HTTPException(408, "分析超时，请重试")
    except ValueError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"分析服务异常: {str(e)[:100]}")


@router.post("/chat")
def chat(body: ChatRequest, user_id: int = Depends(require_kp_access)):
    if not body.messages:
        raise HTTPException(400, "消息不能为空")

    user_messages = [m for m in body.messages if m.get("role") == "user"]
    if not user_messages:
        raise HTTPException(400, "至少需要一条用户消息")

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(chat_followup, body.question_id, body.messages)
            return {"reply": future.result(timeout=45)}
    except concurrent.futures.TimeoutError:
        raise HTTPException(408, "追问超时，请重试")
    except ValueError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"追问服务异常: {str(e)[:100]}")
