from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List
from datetime import datetime
from schemas.todos import TodoOut  # ✅ 일정 속 투두 참조


# -----------------------------
# 요청(Request)
# -----------------------------
class ScheduleCreateRequest(BaseModel):
    title: str = Field(..., example="회의")
    description: Optional[str] = Field(None, example="팀 주간 회의")
    start_time: datetime = Field(..., example="2025-09-20T10:00:00")
    end_time: datetime = Field(..., example="2025-09-20T11:00:00")
    all_day: bool = Field(False, example=False)
    location: Optional[str] = Field(None, example="서울 강남구 카페")


class ScheduleUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, example="회의 (수정됨)")
    description: Optional[str] = Field(None, example="주간 회의 안건 추가")
    start_time: Optional[datetime] = Field(None, example="2025-09-20T10:30:00")
    end_time: Optional[datetime] = Field(None, example="2025-09-20T11:30:00")
    all_day: Optional[bool] = Field(None, example=True)
    location: Optional[str] = Field(None, example="서울 강남구 새로운 카페")


# -----------------------------
# 응답(Response)
# -----------------------------
class ScheduleOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    all_day: bool
    location: Optional[str]
    created_at: datetime
    updated_at: datetime

    # ✅ 일정 속 투두 포함
    todos: List[TodoOut] = Field(default_factory=list)

    # ✅ ReverseRelation → List[TodoOut] 변환
    @field_serializer("todos")
    def serialize_todos(self, todos):
        if not todos:
            return []
        return [TodoOut.model_validate(t, from_attributes=True) for t in todos]

    class Config:
        from_attributes = True  # ✅ ORM 변환 허용


class ScheduleListOut(BaseModel):
    schedules: List[ScheduleOut]
    total: int = Field(..., example=1)


class ScheduleDeleteResponse(BaseModel):
    message: str = Field(
        "Schedule deleted successfully",
        example="Schedule deleted successfully"
    )
