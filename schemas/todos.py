from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# -----------------------------
# 공통 속성
# -----------------------------
class TodoBase(BaseModel):
    title: str = Field(
        ...,
        json_schema_extra={"example": "장보기"},
    )
    description: Optional[str] = Field(
        None,
        json_schema_extra={"example": "우유, 계란, 빵 사오기"},
    )
    is_completed: bool = Field(
        False,
        json_schema_extra={"example": False},  #  기본값 False로 강제 (체크박스 대응)
    )


# -----------------------------
# 요청(Request)
# -----------------------------

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        json_schema_extra={"example": "장보기 (수정됨)"},
    )
    description: Optional[str] = Field(
        None,
        json_schema_extra={"example": "계란 대신 두부 사오기"},
    )
    is_completed: Optional[bool] = Field(
        None,
        json_schema_extra={"example": True},  #  수정 시에만 nullable 허용
    )


# -----------------------------
# 응답(Response)
# -----------------------------
class TodoOut(TodoBase):
    id: int = Field(
        ...,
        json_schema_extra={"example": 5},
    )
    user_id: int = Field(
        ...,
        json_schema_extra={"example": 42},
    )

    created_at: datetime = Field(
        ...,
        json_schema_extra={"example": "2025-09-18T12:34:56"},
    )
    updated_at: datetime = Field(
        ...,
        json_schema_extra={"example": "2025-09-18T12:34:56"},
    )

    model_config = {"from_attributes": True}  #  ORM 변환 허용 (Pydantic v2)


class TodoListOut(BaseModel):
    todos: List[TodoOut]
    total: int = Field(
        ...,
        json_schema_extra={"example": 1},
    )


class TodoDeleteResponse(BaseModel):
    message: str = Field(
        "Todo deleted successfully",
        json_schema_extra={"example": "Todo deleted successfully"},
    )