from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# -----------------------------
# 공통 속성
# -----------------------------
class TodoBase(BaseModel):
    title: str = Field(default="", example="장보기")
    description: Optional[str] = Field(default=None, example="우유, 계란, 빵 사오기")
    is_completed: bool = Field(default=False, example=False)  # 기본값 False


# -----------------------------
# 요청(Request)
# -----------------------------
class TodoCreate(TodoBase):
    schedule_id: Optional[int] = Field(default=None, example=1)  # 일정 ID (없으면 독립 Todo)


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, example="장보기 (수정됨)")
    description: Optional[str] = Field(default=None, example="계란 대신 두부 사오기")
    is_completed: Optional[bool] = Field(default=None, example=True)
    schedule_id: Optional[int] = Field(default=None, example=1)


# -----------------------------
# 응답(Response)
# -----------------------------
class TodoOut(TodoBase):
    id: int = Field(default=0, example=5)
    user_id: int = Field(default=0, example=42)
    schedule_id: Optional[int] = Field(default=None, example=1)  # 연결된 일정 ID
    created_at: datetime = Field(default_factory=datetime.utcnow, example="2025-09-18T12:34:56")
    updated_at: datetime = Field(default_factory=datetime.utcnow, example="2025-09-18T12:34:56")

    model_config = ConfigDict(from_attributes=True)


class TodoListOut(BaseModel):
    todos: List[TodoOut] = Field(default_factory=list)
    total: int = Field(default=0, example=1)

    model_config = ConfigDict(from_attributes=True)


class TodoDeleteResponse(BaseModel):
    message: str = Field(
        default="Todo deleted successfully",
        example="Todo deleted successfully"
    )

    model_config = ConfigDict(from_attributes=True)
