from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


# ========================
# ✅ 내 위치 조회 (Response)
# ========================
class UserLocationResponse(BaseModel):
    id: int = Field(default=..., example=1)
    latitude: float = Field(default=..., example=37.5665)    # 위도
    longitude: float = Field(default=..., example=126.9780)  # 경도
    label: Optional[str] = Field(default=None, example="집")  # 위치 라벨
    is_default: bool = Field(default=..., example=True)      # 기본 여부
    created_at: datetime = Field(default=..., example="2025-09-22T12:34:56")
    updated_at: datetime = Field(default=..., example="2025-09-22T12:40:00")

    model_config = ConfigDict(from_attributes=True)


# ========================
# ✅ 내 위치 수정 (Request)
# ========================
class UserLocationUpdateRequest(BaseModel):
    latitude: Optional[float] = Field(default=None, example=37.5000)
    longitude: Optional[float] = Field(default=None, example=127.0000)
    label: Optional[str] = Field(default=None, example="회사")
    is_default: Optional[bool] = Field(default=None, example=False)


# ========================
# ✅ 내 위치 수정 (Response)
# ========================
class UserLocationUpdateResponse(BaseModel):
    id: int = Field(default=..., example=2)
    latitude: float = Field(default=..., example=37.5000)
    longitude: float = Field(default=..., example=127.0000)
    label: Optional[str] = Field(default=None, example="회사")
    is_default: bool = Field(default=..., example=False)
    updated_at: datetime = Field(default=..., example="2025-09-22T13:15:00")

    model_config = ConfigDict(from_attributes=True)
