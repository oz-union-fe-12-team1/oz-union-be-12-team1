from typing import Annotated, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from schemas.todos import TodoOut


# -----------------------------
# 요청(Request)
# -----------------------------
class ScheduleCreateRequest(BaseModel):
    title: Annotated[str, Field(example="회의")]
    description: Optional[str] = Field(default=None, example="팀 주간 회의")
    start_time: Annotated[datetime, Field(example="2025-09-20T10:00:00")]
    end_time: Annotated[datetime, Field(example="2025-09-20T11:00:00")]
    all_day: Annotated[bool, Field(default=False, example=False)]
    location: Optional[str] = Field(default=None, example="서울 강남구 카페")


class ScheduleUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, example="회의 (수정됨)")
    description: Optional[str] = Field(default=None, example="주간 회의 안건 추가")
    start_time: Optional[datetime] = Field(default=None, example="2025-09-20T10:30:00")
    end_time: Optional[datetime] = Field(default=None, example="2025-09-20T11:30:00")
    all_day: Optional[bool] = Field(default=None, example=True)
    location: Optional[str] = Field(default=None, example="서울 강남구 새로운 카페")


# -----------------------------
# 응답(Response)
# -----------------------------
class ScheduleOut(BaseModel):
    id: Annotated[int, Field(example=1)]
    user_id: Annotated[int, Field(example=42)]
    title: Annotated[str, Field(example="회의")]
    description: Optional[str] = Field(default=None, example="팀 주간 회의")
    start_time: Annotated[datetime, Field(example="2025-09-20T10:00:00")]
    end_time: Annotated[datetime, Field(example="2025-09-20T11:00:00")]
    all_day: Annotated[bool, Field(example=False)]
    location: Optional[str] = Field(default=None, example="서울 강남구 카페")
    created_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]
    updated_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]
    todos: List[TodoOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ScheduleListOut(BaseModel):
    schedules: List[ScheduleOut]
    total: Annotated[int, Field(example=1)]

    model_config = ConfigDict(from_attributes=True)


class ScheduleDeleteResponse(BaseModel):
    message: Annotated[str, Field(
        default="Schedule deleted successfully",
        example="Schedule deleted successfully"
    )]

    model_config = ConfigDict(from_attributes=True)
