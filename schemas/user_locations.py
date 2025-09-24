from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Annotated


# ========================
# ✅ 내 위치 조회 (Response)
# ========================
class UserLocationResponse(BaseModel):
    id: Annotated[int, Field(example=1)]
    latitude: Annotated[float, Field(example=37.5665)]        # 위도
    longitude: Annotated[float, Field(example=126.9780)]      # 경도
    label: Annotated[Optional[str], Field(example="집")] = None  # 위치 라벨
    is_default: Annotated[bool, Field(example=True)]
    created_at: Annotated[datetime, Field(example="2025-09-22T12:34:56")]
    updated_at: Annotated[datetime, Field(example="2025-09-22T12:40:00")]

    model_config = ConfigDict(from_attributes=True)


# ========================
# ✅ 내 위치 수정 (Request)
# ========================
class UserLocationUpdateRequest(BaseModel):
    latitude: Annotated[Optional[float], Field(example=37.5000)] = None
    longitude: Annotated[Optional[float], Field(example=127.0000)] = None
    label: Annotated[Optional[str], Field(example="회사")] = None
    is_default: Annotated[Optional[bool], Field(example=False)] = None


# ========================
# ✅ 내 위치 수정 (Response)
# ========================
class UserLocationUpdateResponse(BaseModel):
    id: Annotated[int, Field(example=2)]
    latitude: Annotated[float, Field(example=37.5000)]
    longitude: Annotated[float, Field(example=127.0000)]
    label: Annotated[Optional[str], Field(example="회사")] = None
    is_default: Annotated[bool, Field(example=False)]
    updated_at: Annotated[datetime, Field(example="2025-09-22T13:15:00")]

    model_config = ConfigDict(from_attributes=True)
