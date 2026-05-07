"""导出路由"""
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from ..auth import get_user_id
from ..services.export import export_wrong

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/wrong")
def export(user_id: int = Depends(get_user_id)):
    data = export_wrong(user_id)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=wrong_questions.xlsx"},
    )
