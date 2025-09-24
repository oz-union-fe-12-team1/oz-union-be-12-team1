from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime


# ========================
# 요청(Request)
# ========================

class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., example="goturkey@example.com")
    password: str = Field(..., example="password123!")
    password_check: str = Field(..., example="password123!")  # ✅ 비밀번호 재입력
    username: str = Field(..., example="고터키")
    birthday: date = Field(..., example="1995-05-21")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "goturkey@example.com",
                "password": "password123!",
                "password_check": "password123!",
                "username": "고터키",
                "birthday": "1995-05-21",
            }
        }
    )


class UserVerifyRequest(BaseModel):
    email: EmailStr = Field(..., example="goturkey@example.com")
    code: str = Field(..., example="123456")


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., example="goturkey@example.com")
    password: str = Field(..., example="password123!")


class GoogleLoginRequest(BaseModel):
    access_token: str = Field(..., example="ya29.A0ARrdaM...")


class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, example="고터키")
    bio: Optional[str] = Field(None, example="안녕하세요!")
    profile_image: Optional[str] = Field(None, example="https://example.com/profile.png")


# ========================
# 응답(Response)
# ========================

class UserCreateResponse(BaseModel):
    id: int = Field(..., example=42)
    email: EmailStr = Field(..., example="goturkey@example.com")
    username: str = Field(..., example="고터키")
    birthday: date = Field(..., example="1995-05-21")
    is_email_verified: bool = Field(default=False, example=False)
    created_at: datetime = Field(..., example="2025-09-18T12:34:56")
    updated_at: datetime = Field(..., example="2025-09-18T12:34:56")

    model_config = ConfigDict(from_attributes=True)


class UserVerifySuccessResponse(BaseModel):
    success: bool = Field(..., example=True)


class UserVerifyErrorResponse(BaseModel):
    errors: List[str] = Field(..., example=["CODE_INVALID", "CODE_EXPIRED"])
    status: List[int] = Field(..., example=[400])


class UserLoginResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIs...")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIs...")
    token_type: str = Field(default="bearer", example="bearer")


class GoogleLoginResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIs...")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIs...")
    token_type: str = Field(default="bearer", example="bearer")


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    birthday: date
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserOut(UserOut):
    is_superuser: bool = Field(default=False, example=False)

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    users: List[UserOut]
    total: int

    model_config = ConfigDict(from_attributes=True)


class AdminUserListResponse(BaseModel):
    users: List[AdminUserOut]
    total: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdateResponse(BaseModel):
    id: int
    username: str
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDeleteResponse(BaseModel):
    message: str = Field(
        default="User deleted successfully",
        example="User deleted successfully",
    )
