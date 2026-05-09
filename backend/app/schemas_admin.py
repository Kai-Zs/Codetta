"""管理员后台 Pydantic 模型"""
from pydantic import BaseModel, Field
from typing import Optional


class QuestionUpdate(BaseModel):
    q_number: Optional[str] = None
    chapter: Optional[str] = None
    type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    options: Optional[str] = None  # JSON string
    answer: Optional[str] = None
    answer_parts: Optional[str] = None  # JSON string
    template: Optional[str] = None
    answer_code: Optional[str] = None
    note: Optional[str] = None
    is_active: Optional[int] = None


class QuestionCreate(BaseModel):
    q_number: str
    chapter: str
    type: str
    title: str = ""
    content: str = ""
    options: Optional[str] = None
    answer: str = ""
    answer_parts: Optional[str] = None
    template: Optional[str] = None
    answer_code: Optional[str] = None
    note: str = ""


class PasswordChange(BaseModel):
    old_password: str
    new_password: str
