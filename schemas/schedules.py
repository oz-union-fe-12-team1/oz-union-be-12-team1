from pydantic import BaseModel, Field, field_serializer, ConfigDict
from typing import Optional, List
from datetime import datetime

from models.todo import Todo
from schemas.todos import TodoOut


# -----------------------------
# 요청(Request)
# -----------------------------
class ScheduleCreateRequest(BaseModel):
    title: str = Field(
        ...,
        json_schema_extra={"example": "회의"},
    )
    description: Optional[str] = Field(
        None,
        json_schema_extra={"example": "팀 주간 회의"},
    )
    start_time: datetime = Field(
        ...,
        json_schema_extra={"example": "2025-09-20T10:00:00"},
    )
    end_time: datetime = Field(
        ...,
        json_schema_extra={"example": "2025-09-20T11:00:00"},
    )
    all_day: bool = Field(
        False,
        json_schema_extra={"example": False},
    )
    location: Optional[str] = Field(
        None,
        json_schema_extra={"example": "서울 강남구 카페"},
    )


class ScheduleUpdateRequest(BaseModel):
    title: Optional[str] = Field(
        None,
        json_schema_extra={"example": "회의 (수정됨)"},
    )
    description: Optional[str] = Field(
        None,
        json_schema_extra={"example": "주간 회의 안건 추가"},
    )
    start_time: Optional[datetime] = Field(
        None,
        json_schema_extra={"example": "2025-09-20T10:30:00"},
    )
    end_time: Optional[datetime] = Field(
        None,
        json_schema_extra={"example": "2025-09-20T11:30:00"},
    )
    all_day: Optional[bool] = Field(
        None,
        json_schema_extra={"example": True},
    )
    location: Optional[str] = Field(
        None,
        json_schema_extra={"example": "서울 강남구 새로운 카페"},
    )

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
    todos: List[TodoOut] = Field(default_factory=list)

    @field_serializer("todos")
    def serialize_todos(self, todos: list[Todo]) -> List[TodoOut]:
        if not todos:
            return []
        return [TodoOut.model_validate(t, from_attributes=True) for t in todos]

    model_config = ConfigDict(from_attributes=True)


class ScheduleListOut(BaseModel):
    schedules: List[ScheduleOut]
    total: int = Field(..., json_schema_extra={"example": 1})


class ScheduleDeleteResponse(BaseModel):
    message: str = Field(
        "Schedule deleted successfully",
        json_schema_extra={"example": "Schedule deleted successfully"},
    )
