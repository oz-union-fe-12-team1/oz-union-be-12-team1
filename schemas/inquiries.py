from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Annotated
from datetime import datetime
from enum import Enum


# -----------------------------
# 상태 Enum (명세서 기준)
# -----------------------------
class InquiryStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


# -----------------------------
# 공통 속성
# -----------------------------
class InquiryBase(BaseModel):
    title: Annotated[str, Field(example="로그인 오류가 발생합니다")]
    message: Annotated[str, Field(example="구글 로그인 시 500 오류가 뜹니다.")]


# -----------------------------
# 요청(Request)
# -----------------------------
class InquiryCreateRequest(InquiryBase):
    pass


class InquiryUpdateRequest(BaseModel):
    status: Annotated[Optional[InquiryStatus], Field(example="resolved")] = None
    admin_reply: Annotated[Optional[str], Field(example="서버 설정 문제를 수정했습니다.")] = None
    replied_at: Annotated[Optional[datetime], Field(example="2025-09-19T15:30:00")] = None


# -----------------------------
# 응답(Response)
# -----------------------------
class InquiryCreateResponse(InquiryBase):
    id: Annotated[int, Field(example=12)]
    user_id: Annotated[int, Field(example=42)]
    status: Annotated[InquiryStatus, Field(example="pending")]
    admin_reply: Annotated[Optional[str], Field(example=None)] = None
    replied_at: Annotated[Optional[datetime], Field(example=None)] = None
    created_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]
    updated_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]

    model_config = ConfigDict(from_attributes=True)


class InquiryUpdateResponse(InquiryCreateResponse):
    """업데이트 응답은 생성 응답과 동일 구조"""


class InquiryListResponse(BaseModel):
    inquiries: List[InquiryCreateResponse]
    total: Annotated[int, Field(example=1)]

    model_config = ConfigDict(from_attributes=True)


class InquiryDeleteResponse(BaseModel):
    message: Annotated[str, Field(example="Inquiry deleted successfully")] = (
        "Inquiry deleted successfully"
    )

    model_config = ConfigDict(from_attributes=True)
