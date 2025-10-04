from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class ScheduleCreateRequest(BaseModel):
    """일정 생성 요청"""
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    location: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "현기 생일 파티",
                "description": "현기 생일 파티 준비 (케이크, 선물 챙기기)",
                "start_time": "2025-09-20T18:00:00",
                "end_time": "2025-09-20T22:00:00",
                "all_day": False,
                "location": "현기 집",
            }
        }
    )

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ScheduleUpdateRequest(BaseModel):
    """일정 부분 수정 요청 (PATCH 전용)"""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    location: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "현기 생일 파티 (장소 변경)",
                "description": "파티 장소를 현기 집에서 카페로 변경",
                "start_time": "2025-09-20T19:00:00",
                "end_time": "2025-09-20T23:00:00",
                "all_day": True,
                "location": "강남역 근처 카페",
            }
        }
    )

class ScheduleCreateResponse(BaseModel):
    """일정 생성 응답"""
    id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    all_day: bool
    location: Optional[str]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 7,
                "title": "현기 생일 파티",
                "description": "현기 생일 파티 준비 (케이크, 선물 챙기기)",
                "start_time": "2025-09-20T18:00:00",
                "end_time": "2025-09-20T22:00:00",
                "all_day": False,
                "location": "현기 집",
            }
        },
    )


class ScheduleOut(BaseModel):
    """일정 단일 조회 / 상세 응답"""
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

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 7,
                "user_id": 4,
                "title": "회의",
                "description": "팀 주간 회의",
                "start_time": "2025-09-20T10:00:00Z",
                "end_time": "2025-09-20T11:00:00Z",
                "all_day": False,
                "location": "서울 강남구 카페",
                "created_at": "2025-10-04T07:40:45.525328Z",
                "updated_at": "2025-10-04T07:40:45.525335Z",
            }
        },
    )


class ScheduleListOut(BaseModel):
    """일정 목록 조회 응답"""
    schedules: List[ScheduleOut]
    total: int = Field(default=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "schedules": [
                    {
                        "id": 7,
                        "user_id": 4,
                        "title": "회의",
                        "description": "팀 주간 회의",
                        "start_time": "2025-09-20T10:00:00Z",
                        "end_time": "2025-09-20T11:00:00Z",
                        "all_day": False,
                        "location": "서울 강남구 카페",
                        "created_at": "2025-10-04T07:40:45.525328Z",
                        "updated_at": "2025-10-04T07:40:45.525335Z",
                    }
                ],
                "total": 1,
            }
        },
    )


class ScheduleDeleteResponse(BaseModel):
    """일정 삭제 응답"""
    message: str = Field(
        default="Schedule deleted successfully",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Schedule deleted successfully"
            }
        },
    )
