from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# 👉 공통 속성
class TodoBase(BaseModel):
    title: str = Field(..., example="장보기")
    description: Optional[str] = Field(None, example="우유, 계란, 빵 사오기")
    is_completed: Optional[bool] = Field(False, example=False)


# 👉 생성 요청
class TodoCreate(TodoBase):
    schedule_id: Optional[int] = Field(None, example=1)


# 👉 수정 요청
class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, example="장보기 (수정됨)")
    description: Optional[str] = Field(None, example="계란 대신 두부 사오기")
    is_completed: Optional[bool] = Field(None, example=True)
    schedule_id: Optional[int] = Field(None, example=1)


# 👉 단일 조회 응답
class TodoOut(TodoBase):
    id: int = Field(..., example=5)
    user_id: int = Field(..., example=42)
    schedule_id: Optional[int] = Field(None, example=1)
    created_at: datetime = Field(..., example="2025-09-18T12:34:56")
    updated_at: datetime = Field(..., example="2025-09-18T12:34:56")

    class Config:
        orm_mode = True


# 👉 리스트 조회 응답
class TodoListOut(BaseModel):
    todos: List[TodoOut] = Field(
        ...,
        example=[
            {
                "id": 5,
                "user_id": 42,
                "schedule_id": 1,
                "title": "장보기",
                "description": "우유, 계란, 빵 사오기",
                "is_completed": False,
                "created_at": "2025-09-18T12:34:56",
                "updated_at": "2025-09-18T12:34:56"
            }
        ]
    )
    total: int = Field(..., example=1)


# 👉 삭제 응답
class TodoDeleteResponse(BaseModel):
    message: str = Field(
        "Todo deleted successfully",
        example="Todo deleted successfully"
    )
