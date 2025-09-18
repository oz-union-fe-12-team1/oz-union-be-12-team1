from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NotificationBase(BaseModel):
    message: str = Field(..., example="회의 10분 전 알림")
    notify_at: Optional[datetime] = Field(
        None, example="2025-09-20T09:50:00"
    )
    is_read: Optional[bool] = Field(False, example=False)


class NotificationCreate(NotificationBase):
    schedule_id: Optional[int] = Field(None, example=1)
    todo_id: Optional[int] = Field(None, example=5)


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = Field(None, example=True)


class NotificationOut(NotificationBase):
    id: int = Field(..., example=10)
    user_id: int = Field(..., example=42)
    schedule_id: Optional[int] = Field(None, example=1)
    todo_id: Optional[int] = Field(None, example=5)
    created_at: datetime = Field(
        ..., example="2025-09-18T12:34:56"
    )
    updated_at: datetime = Field(
        ..., example="2025-09-18T12:34:56"
    )

    class Config:
        orm_mode = True


class NotificationListOut(BaseModel):
    notifications: List[NotificationOut] = Field(
        ..., example=[
            {
                "id": 10,
                "user_id": 42,
                "schedule_id": 1,
                "todo_id": 5,
                "message": "회의 10분 전 알림",
                "notify_at": "2025-09-20T09:50:00",
                "is_read": False,
                "created_at": "2025-09-18T12:34:56",
                "updated_at": "2025-09-18T12:34:56"
            }
        ]
    )
    total: int = Field(..., example=1)


class NotificationDeleteResponse(BaseModel):
    message: str = Field(
        "Notification deleted successfully",
        example="Notification deleted successfully"
    )
