from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 👉 상태 Enum (명세서 기준)
class InquiryStatus(str):
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


# 👉 공통 속성
class InquiryBase(BaseModel):
    title: str = Field(..., example="로그인 오류가 발생합니다")
    message: str = Field(..., example="구글 로그인 시 500 오류가 뜹니다.")


# 👉 생성 요청
class InquiryCreate(InquiryBase):
    pass


# 👉 수정 요청 (관리자 답변, 상태 변경 등)
class InquiryUpdate(BaseModel):
    status: Optional[str] = Field(None, example="resolved")
    admin_reply: Optional[str] = Field(None, example="서버 설정 문제를 수정했습니다.")
    replied_at: Optional[datetime] = Field(None, example="2025-09-19T15:30:00")


# 👉 단일 조회 응답
class InquiryOut(InquiryBase):
    id: int = Field(..., example=12)
    user_id: int = Field(..., example=42)
    status: str = Field(..., example="pending")
    admin_reply: Optional[str] = Field(None, example=None)
    replied_at: Optional[datetime] = Field(None, example=None)
    created_at: datetime = Field(..., example="2025-09-18T12:34:56")
    updated_at: datetime = Field(..., example="2025-09-18T12:34:56")

    class Config:
        from_attributes = True   # ✅ Pydantic v2 필수


# 👉 목록 조회 응답
class InquiryListOut(BaseModel):
    inquiries: List[InquiryOut]
    total: int = Field(..., example=1)

    class Config:
        from_attributes = True   # ✅ 추가


# 👉 삭제 응답
class InquiryDeleteResponse(BaseModel):
    message: str = Field(
        "Inquiry deleted successfully",
        example="Inquiry deleted successfully"
    )
