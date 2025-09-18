from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ========================
# 요청(Request)
# ========================

# 👉 회원가입 요청
class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., example="goturkey@example.com")
    password: str = Field(..., example="password123!")
    name: str = Field(..., example="고터키")
    phone: Optional[str] = Field(None, example="010-1234-5678")
    profile_image: Optional[str] = Field(None, example="https://example.com/profile.png")


# 👉 이메일 인증 요청
class UserVerifyRequest(BaseModel):
    token: str = Field(..., example="verify-token")


# 👉 로그인 요청
class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., example="goturkey@example.com")
    password: str = Field(..., example="password123!")


# 👉 구글 로그인 요청
class GoogleLoginRequest(BaseModel):
    access_token: str = Field(..., example="ya29.A0ARrdaM...")


# 👉 사용자 정보 수정 요청
class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, example="고터키")
    phone: Optional[str] = Field(None, example="010-9876-5432")
    profile_image: Optional[str] = Field(None, example="https://example.com/new.png")


# ========================
# 응답(Response)
# ========================

# 👉 회원가입 성공 응답
class UserCreateResponse(BaseModel):
    id: int = Field(..., example=42)
    email: EmailStr = Field(..., example="goturkey@example.com")
    name: str = Field(..., example="고터키")
    phone: Optional[str] = Field(None, example="010-1234-5678")
    profile_image: Optional[str] = Field(None, example="https://example.com/profile.png")
    is_verified: bool = Field(False, example=False)
    created_at: datetime = Field(..., example="2025-09-18T12:34:56")
    updated_at: datetime = Field(..., example="2025-09-18T12:34:56")

    class Config:
        orm_mode = True


# 👉 이메일 인증 성공 응답
class UserVerifySuccessResponse(BaseModel):
    success: bool = Field(..., example=True)


# 👉 이메일 인증 실패 응답
class UserVerifyErrorResponse(BaseModel):
    errors: List[str] = Field(..., example=["TOKEN_INVALID", "TOKEN_EXPIRED"])
    status: List[int] = Field(..., example=[400])


# 👉 로그인 성공 응답
class UserLoginResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIs...")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIs...")
    token_type: str = Field("bearer", example="bearer")


# 👉 구글 로그인 성공 응답
class GoogleLoginResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIs...")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIs...")
    token_type: str = Field("bearer", example="bearer")


# 👉 단일 조회 응답
class UserOut(BaseModel):
    id: int = Field(..., example=42)
    email: EmailStr = Field(..., example="goturkey@example.com")
    name: str = Field(..., example="고터키")
    phone: Optional[str] = Field(None, example="010-1234-5678")
    profile_image: Optional[str] = Field(None, example="https://example.com/profile.png")
    is_verified: bool = Field(False, example=False)
    created_at: datetime = Field(..., example="2025-09-18T12:34:56")
    updated_at: datetime = Field(..., example="2025-09-18T12:34:56")

    class Config:
        orm_mode = True


# 👉 사용자 목록 조회 응답
class UserListResponse(BaseModel):
    users: List[UserOut]
    total: int = Field(..., example=1)


# 👉 사용자 정보 수정 응답
class UserUpdateResponse(BaseModel):
    id: int = Field(..., example=42)
    name: str = Field(..., example="고터키")
    phone: Optional[str] = Field(None, example="010-9876-5432")
    profile_image: Optional[str] = Field(None, example="https://example.com/new.png")
    updated_at: datetime = Field(..., example="2025-09-18T12:34:56")


# 👉 사용자 삭제 응답
class UserDeleteResponse(BaseModel):
    message: str = Field("User deleted successfully", example="User deleted successfully")
