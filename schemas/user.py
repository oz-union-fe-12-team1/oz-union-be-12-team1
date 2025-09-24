from typing import Annotated, Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime


# ========================
# 요청(Request)
# ========================

class UserCreateRequest(BaseModel):
    email: Annotated[EmailStr, Field(example="goturkey@example.com")]
    password: Annotated[str, Field(example="password123!")]
    password_check: Annotated[str, Field(example="password123!")]  # ✅ 비밀번호 재입력
    username: Annotated[str, Field(example="고터키")]
    birthday: Annotated[date, Field(example="1995-05-21")]

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
    email: Annotated[EmailStr, Field(example="goturkey@example.com")]
    code: Annotated[str, Field(example="123456")]


class UserLoginRequest(BaseModel):
    email: Annotated[EmailStr, Field(example="goturkey@example.com")]
    password: Annotated[str, Field(example="password123!")]


class GoogleLoginRequest(BaseModel):
    access_token: Annotated[str, Field(example="ya29.A0ARrdaM...")]


class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(default=None, example="고터키")
    bio: Optional[str] = Field(default=None, example="안녕하세요!")
    profile_image: Optional[str] = Field(default=None, example="https://example.com/profile.png")


# ========================
# 응답(Response)
# ========================

class UserCreateResponse(BaseModel):
    id: Annotated[int, Field(example=42)]
    email: Annotated[EmailStr, Field(example="goturkey@example.com")]
    username: Annotated[str, Field(example="고터키")]
    birthday: Annotated[date, Field(example="1995-05-21")]
    is_email_verified: Annotated[bool, Field(example=False)]
    created_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]
    updated_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]

    model_config = ConfigDict(from_attributes=True)


class UserVerifySuccessResponse(BaseModel):
    success: Annotated[bool, Field(example=True)]


class UserVerifyErrorResponse(BaseModel):
    errors: Annotated[List[str], Field(example=["CODE_INVALID", "CODE_EXPIRED"])]
    status: Annotated[List[int], Field(example=[400])]


class UserLoginResponse(BaseModel):
    access_token: Annotated[str, Field(example="eyJhbGciOiJIUzI1NiIs...")]
    refresh_token: Annotated[str, Field(example="eyJhbGciOiJIUzI1NiIs...")]
    token_type: Annotated[str, Field(default="bearer", example="bearer")]


class GoogleLoginResponse(BaseModel):
    access_token: Annotated[str, Field(example="eyJhbGciOiJIUzI1NiIs...")]
    refresh_token: Annotated[str, Field(example="eyJhbGciOiJIUzI1NiIs...")]
    token_type: Annotated[str, Field(default="bearer", example="bearer")]


class UserOut(BaseModel):
    id: Annotated[int, Field(example=42)]
    email: Annotated[EmailStr, Field(example="goturkey@example.com")]
    username: Annotated[str, Field(example="고터키")]
    birthday: Annotated[date, Field(example="1995-05-21")]
    is_email_verified: Annotated[bool, Field(example=False)]
    created_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]
    updated_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]

    model_config = ConfigDict(from_attributes=True)


class AdminUserOut(UserOut):
    is_superuser: Annotated[bool, Field(default=False, example=False)]

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    users: List[UserOut]
    total: Annotated[int, Field(example=1)]

    model_config = ConfigDict(from_attributes=True)


class AdminUserListResponse(BaseModel):
    users: List[AdminUserOut]
    total: Annotated[int, Field(example=1)]

    model_config = ConfigDict(from_attributes=True)


class UserUpdateResponse(BaseModel):
    id: Annotated[int, Field(example=42)]
    username: Annotated[str, Field(example="고터키")]
    bio: Optional[str] = Field(default=None, example="안녕하세요!")
    profile_image: Optional[str] = Field(default=None, example="https://example.com/profile.png")
    updated_at: Annotated[datetime, Field(example="2025-09-18T12:34:56")]

    model_config = ConfigDict(from_attributes=True)


class UserDeleteResponse(BaseModel):
    message: Annotated[str, Field(default="User deleted successfully", example="User deleted successfully")]
