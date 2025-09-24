from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Annotated
from datetime import datetime


# -----------------------------
# 공통 속성
# -----------------------------
class TokenRevocationBase(BaseModel):
    token: Annotated[str, Field(example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")]
    revoked_at: Annotated[datetime, Field(example="2025-09-19T10:30:00")] = datetime.utcnow()
    expires_at: Annotated[Optional[datetime], Field(example="2025-09-20T10:30:00")] = None


# -----------------------------
# 생성 요청
# -----------------------------
class TokenRevocationCreate(BaseModel):
    token: Annotated[str, Field(example="eyJhbGciOiJIUzI1NiIs...")] = ""
    user_id: Annotated[int, Field(example=42)] = 0


# -----------------------------
# 단일 조회 응답
# -----------------------------
class TokenRevocationOut(TokenRevocationBase):
    id: Annotated[int, Field(example=1)] = 0
    user_id: Annotated[int, Field(example=42)] = 0

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# 목록 조회 응답
# -----------------------------
class TokenRevocationListOut(BaseModel):
    revocations: List[TokenRevocationOut] = []
    total: Annotated[int, Field(example=1)] = 0

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# 삭제 응답
# -----------------------------
class TokenRevocationDeleteResponse(BaseModel):
    message: Annotated[str, Field(example="Token revocation entry deleted successfully")] = (
        "Token revocation entry deleted successfully"
    )

    model_config = ConfigDict(from_attributes=True)
