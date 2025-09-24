from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# -----------------------------
# 공통 속성
# -----------------------------
class TokenRevocationBase(BaseModel):
    token: str = Field(default="", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    revoked_at: datetime = Field(default_factory=datetime.utcnow, example="2025-09-19T10:30:00")
    expires_at: Optional[datetime] = Field(default=None, example="2025-09-20T10:30:00")


# -----------------------------
# 생성 요청
# -----------------------------
class TokenRevocationCreate(BaseModel):
    token: str = Field(default="", example="eyJhbGciOiJIUzI1NiIs...")
    user_id: int = Field(default=0, example=42)


# -----------------------------
# 단일 조회 응답
# -----------------------------
class TokenRevocationOut(TokenRevocationBase):
    id: int = Field(default=0, example=1)
    user_id: int = Field(default=0, example=42)

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# 목록 조회 응답
# -----------------------------
class TokenRevocationListOut(BaseModel):
    revocations: List[TokenRevocationOut] = Field(default_factory=list)
    total: int = Field(default=0, example=1)

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# 삭제 응답
# -----------------------------
class TokenRevocationDeleteResponse(BaseModel):
    message: str = Field(
        default="Token revocation entry deleted successfully",
        example="Token revocation entry deleted successfully"
    )

    model_config = ConfigDict(from_attributes=True)
