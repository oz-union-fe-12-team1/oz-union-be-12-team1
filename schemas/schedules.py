from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Annotated
from datetime import datetime
from schemas.todos import TodoCreateResponse  # ✅ todos와 연계 (TodoOut → TodoCreateResponse)


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
    # 명세서에 맞춰 추가 가능: user_id, is_recurring, recurrence_rule, parent_schedule_id 등


class ScheduleUpdateRequest(BaseModel):
    title: Annotated[Optional[str], Field(example="회의 (수정됨)")] = None
    description: Annotated[Optional[str], Field(example="주간 회의 안건 추가")] = None
    start_time: Annotated[Optional[datetime], Field(example="2025-09-20T10:30:00")] = None
    end_time: Annotated[Optional[datetime], Field(example="2025-09-20T11:30:00")] = None
    all_day: Annotated[Optional[bool], Field(example=True)] = None
    location: Annotated[Optional[str], Field(example="서울 강남구 새로운 카페")] = None
    # 명세서 기반: is_recurring, recurrence_rule, parent_schedule_id 등 추가 가능


# -----------------------------
# 응답(Response)
# -----------------------------
class ScheduleCreateResponse(BaseModel):
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
    todos: List[TodoCreateResponse] = []  # ✅ Todo 연결

    model_config = ConfigDict(from_attributes=True)


class ScheduleUpdateResponse(ScheduleCreateResponse):
    """업데이트 후 반환은 생성 응답과 동일 구조 사용"""


class ScheduleListResponse(BaseModel):
    schedules: List[ScheduleCreateResponse] = []
    total: Annotated[int, Field(example=1)] = 0

    model_config = ConfigDict(from_attributes=True)


class ScheduleDeleteResponse(BaseModel):
    message: Annotated[str, Field(example="Schedule deleted successfully")] = (
        "Schedule deleted successfully"
    )

    model_config = ConfigDict(from_attributes=True)
