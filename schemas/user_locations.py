from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# ========================
#  내 위치 조회 (Response)
# ========================
class UserLocationResponse(BaseModel):
    id: int
    latitude: float      # 위도
    longitude: float     # 경도
    label: Optional[str] = None  # 위치 라벨
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "latitude": 37.5665,
                "longitude": 126.9780,
                "label": "집",
                "is_default": True,
                "created_at": "2025-09-22T12:34:56",
                "updated_at": "2025-09-22T12:40:00",
            }
        }
    )


# ========================
#  내 위치 수정 (Request)
# ========================
class UserLocationUpdateRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    label: Optional[str] = None
    is_default: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "latitude": 37.5000,
                "longitude": 127.0000,
                "label": "회사",
                "is_default": False,
            }
        }
    )


# ========================
#  내 위치 수정 (Response)
# ========================
class UserLocationUpdateResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    label: Optional[str] = None
    is_default: bool
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "latitude": 37.5000,
                "longitude": 127.0000,
                "label": "회사",
                "is_default": False,
                "updated_at": "2025-09-22T13:15:00",
            }
        }
    )