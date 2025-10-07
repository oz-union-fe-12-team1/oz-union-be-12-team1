from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


#  상태 Enum (명세서 기준)
class InquiryStatus(str):
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


#  공통 속성
class InquiryBase(BaseModel):
    title: str = Field(
        ...,
        json_schema_extra={"example": "로그인 오류가 발생합니다"},
    )
    message: str = Field(
        ...,
        json_schema_extra={"example": "구글 로그인 시 500 오류가 뜹니다."},
    )


#  생성 요청
class InquiryCreate(InquiryBase):
    pass

# 유저 본인 문의 수정
class InquiryUserUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        json_schema_extra={
            "example": "문의 내용 잘못 적었어요"
        }
    )

    message: Optional[str] = Field(
        None,
        json_schema_extra={
            "example": "수정 어떻게 해요?!"
        }
    )



#  수정 요청 (관리자 답변, 상태 변경 등)
class InquiryUpdate(BaseModel):
    status: Optional[str] = Field(
        None,
        json_schema_extra={"example": "resolved"},
    )
    admin_reply: Optional[str] = Field(
        None,
        json_schema_extra={"example": "서버 설정 문제를 수정했습니다."},
    )
    replied_at: Optional[datetime] = Field(
        None,
        json_schema_extra={"example": "2025-09-19T15:30:00"},
    )


#  단일 조회 응답
class InquiryOut(InquiryBase):
    id: int = Field(
        ...,
        json_schema_extra={"example": 12},
    )
    user_id: int = Field(
        ...,
        json_schema_extra={"example": 42},
    )
    status: str = Field(
        ...,
        json_schema_extra={"example": "pending"},
    )
    admin_reply: Optional[str] = Field(
        None,
        json_schema_extra={"example": None},
    )
    replied_at: Optional[datetime] = Field(
        None,
        json_schema_extra={"example": None},
    )
    created_at: datetime = Field(
        ...,
        json_schema_extra={"example": "2025-09-18T12:34:56"},
    )
    updated_at: datetime = Field(
        ...,
        json_schema_extra={"example": "2025-09-18T12:34:56"},
    )

    model_config = {"from_attributes": True}  #  v2 스타일


#  목록 조회 응답
class InquiryListOut(BaseModel):
    inquiries: List[InquiryOut]
    total: int = Field(
        ...,
        json_schema_extra={"example": 1},
    )

    model_config = {"from_attributes": True}  #  v2 스타일


#  삭제 응답
class InquiryDeleteResponse(BaseModel):
    message: str = Field(
        default="Inquiry deleted successfully",
        json_schema_extra={"example": "Inquiry deleted successfully"},
    )