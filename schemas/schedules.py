from pydantic import BaseModel, Field, field_serializer, ConfigDict
from typing import Optional, List
from datetime import datetime

from models.todo import Todo
from schemas.todos import TodoOut


class ScheduleCreateRequest(BaseModel):
    title: str = Field(..., example="현기 생일 파티")
    description: Optional[str] = Field(None, example="현기 생일 파티 준비 (케이크, 선물 챙기기)")
    start_time: datetime = Field(..., example="2025-09-20T18:00:00")
    end_time: datetime = Field(..., example="2025-09-20T22:00:00")
    all_day: bool = Field(False, example=False)
    location: Optional[str] = Field(None, example="현기 집")


class ScheduleUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, example="현기 생일 파티 (장소 변경)")
    description: Optional[str] = Field(None, example="파티 장소를 현기 집에서 카페로 변경")
    start_time: Optional[datetime] = Field(None, example="2025-09-20T19:00:00")
    end_time: Optional[datetime] = Field(None, example="2025-09-20T23:00:00")
    all_day: Optional[bool] = Field(None, example=True)
    location: Optional[str] = Field(None, example="현기 집")


class ScheduleCreateResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    all_day: bool
    location: Optional[str]

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class ScheduleListOut(BaseModel):
    schedules: List[ScheduleOut]
    total: int = Field(..., example=1)


class ScheduleDeleteResponse(BaseModel):
    message: str = Field(
        "Schedule deleted successfully",
        example="Schedule deleted successfully",
    )
