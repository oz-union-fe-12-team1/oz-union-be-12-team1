from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# 👉 공통 속성
class TokenRevocationBase(BaseModel):
    token: str = Field(
        ...,
        json_schema_extra={
            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        },
    )
    revoked_at: datetime = Field(
        ...,
        json_schema_extra={"example": "2025-09-19T10:30:00"},
    )
    expires_at: Optional[datetime] = Field(
        None,
        json_schema_extra={"example": "2025-09-20T10:30:00"},
    )


# 👉 생성 요청 (토큰 무효화)
class TokenRevocationCreate(BaseModel):
    token: str = Field(
        ...,
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIs..."},
    )
    user_id: int = Field(
        ...,
        json_schema_extra={"example": 42},
    )


# 👉 단일 조회 응답
class TokenRevocationOut(TokenRevocationBase):
    id: int = Field(
        ...,
        json_schema_extra={"example": 1},
    )
    user_id: int = Field(
        ...,
        json_schema_extra={"example": 42},
    )

    model_config = {"from_attributes": True}  # ✅ Pydantic v2


# 👉 목록 조회 응답
class TokenRevocationListOut(BaseModel):
    revocations: List[TokenRevocationOut] = Field(
        ...,
        json_schema_extra={
            "example": [
                {
                    "id": 1,
                    "user_id": 42,
                    "token": "eyJhbGciOiJIUzI1NiIs...",
                    "revoked_at": "2025-09-19T10:30:00",
                    "expires_at": "2025-09-20T10:30:00",
                }
            ]
        },
    )
    total: int = Field(
        ...,
        json_schema_extra={"example": 1},
    )


# 👉 삭제 응답 (관리자 전용, 선택적)
class TokenRevocationDeleteResponse(BaseModel):
    message: str = Field(
        "Token revocation entry deleted successfully",
        json_schema_extra={
            "example": "Token revocation entry deleted successfully"
        },
    )