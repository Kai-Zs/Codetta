"""Pydantic 请求/响应模型"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    student_id: str = Field(min_length=10, max_length=10, pattern=r"^\d{10}$")


class VerifyPinRequest(BaseModel):
    student_id: str = Field(min_length=10, max_length=10, pattern=r"^\d{10}$")
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")


class SetPinRequest(BaseModel):
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")
    old_pin: str | None = None


class UpdateSettingsRequest(BaseModel):
    prog_mode: str | None = None
    sound_on: int | None = None
    vibrate_on: int | None = None


class ProgressSubmit(BaseModel):
    question_id: int
    answer_status: str
    user_answer: str
    mode: str = "sequential"
    prog_submit_type: str | None = None


class RemoveWrongRequest(BaseModel):
    question_ids: list[int]


class JudgeRequest(BaseModel):
    question_id: int
    user_code: str
