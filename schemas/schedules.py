from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Annotated
from datetime import datetime
from schemas.todos import TodoOut


# -----------------------------
# 요청(Request)
# -----------------------------
class ScheduleCreateRequest(BaseModel):
    title: Annotated[str, Field(example="회의")]
    description: Annotated[Optional[str], Field(example="팀 주간 회의")] = None
    start_time: Annotated[datetime, Field(example="2025-09-20T10:00:00")]
    end_time: Annotated[datetime, Field(example="2025-09-20T11:00:00")]
    all_day: Annotated[bool, Field(example=False)] = False
    location: Annotated[Optional[str], Field(example="서울 강남구 카페")] = None


class ScheduleUpdateRequest(BaseModel):
    title: Annotated[Optional[str], Field(example="회의 (수정됨)")] = None
    description: Annotated[Optional[str], Field(example="주간 회의 안건 추가")] = None
    start_time: Annotated[Optional[datetime], Field(example="2025-09-20T10:30:00")] = None
    end_time: Annotated[Optional[datetime], Field(example="2025-09-20T11:30:00")] = None
    all_day: Annotated[Optional[bool], Field(example=True)] = None
    location: Annotated[Optional[str], Field(example="서울 강남구 새로운 카페")] = None


# -----------------------------
# 응답(Response)
# -----------------------------
class ScheduleOut(BaseModel):
    id: Annotated[int, Field(example=1)]
    user_id: Annotated[int, Field(example=42)]
    title: Annotated[str, Field(example="회의")]
    description: Annotated[Optional[str], Field(example="팀 주간 회의")] = None
    start_time: Annotated[datetime, Field(example="2025-09-20T10:00:00")]
    end_time: Annotated[datetime, Field(example="2025-09-20T11:00:00")]
    all_day: Annotated[bool, Field(example=False)]
    location: Annotated[Optional[str], Field(example="서울 강남구 카페")] = None
    created_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]
    updated_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]
    todos: List[TodoOut] = []

    model_config = ConfigDict(from_attributes=True)


class ScheduleListOut(BaseModel):
    schedules: List[ScheduleOut] = []
    total: Annotated[int, Field(example=1)] = 0

    model_config = ConfigDict(from_attributes=True)


class ScheduleDeleteResponse(BaseModel):
    message: Annotated[str, Field(example="Schedule deleted successfully")] = (
        "Schedule deleted successfully"
    )

    model_config = ConfigDict(from_attributes=True)
