from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import enum


# ======================
# 우선순위 Enum
# ======================
class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


# ======================
# Notification 응답 (선택사항)
# ======================
class NotificationResponse(BaseModel):
    main_alert: Optional[datetime] = Field(
        None, example="2025-09-15T10:00:00Z", description="메인 알림 시각 (NULL이면 알림 없음)"
    )


# ======================
# Todo 응답 스키마
# ======================
class TodoResponse(BaseModel):
    id: int = Field(..., example=1, description="할 일 고유 ID")
    title: str = Field(..., example="오전 10시 운동가기", description="할 일 제목")
    description: Optional[str] = Field(None, example="아침에 헬스장 가기", description="할 일 설명 (선택사항)")
    is_completed: bool = Field(..., example=False, description="완료 여부")
    scheduled_time: Optional[datetime] = Field(
        None, example="2025-09-15T10:00:00Z", description="예정 시간 (선택사항)"
    )
    priority: Optional[Priority] = Field(
        None, example="medium", description="우선순위 (null/low/medium/high)"
    )
    notifications: Optional[NotificationResponse] = Field(
        None, description="알림 정보 (선택사항)"
    )
    created_at: datetime = Field(..., example="2025-09-15T09:00:00Z", description="생성 시각")
    updated_at: datetime = Field(..., example="2025-09-15T09:05:00Z", description="수정 시각")

    class Config:
        from_attributes = True  # ORM 객체 → Pydantic 변환 허용

# ======================
# Todo 생성 요청 (POST /todos)
# ======================
class TodoCreate(TodoBase):
    pass


# ======================
# Todo 수정 요청 (PUT /todos/{id})
# ======================
class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    scheduled_time: Optional[datetime] = None
    notifications: Optional[NotificationBase] = None


# ======================
# Todo 응답 스키마 (GET /todos)
# ======================
class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ORM → Pydantic 변환 지원