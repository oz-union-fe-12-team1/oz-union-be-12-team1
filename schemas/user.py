from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer
from typing import Optional, List, Union, Any
from datetime import date, datetime, timedelta, timezone

# ========================
# 요청(Request)
# ========================
class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    password_check: str
    username: str
    birthday: date

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "goturkey@example.com",
                "password": "password123!",
                "password_check": "password123!",
                "username": "고터키",
                "birthday": "1995-05-21",
            }
        }
    }


class UserVerifyRequest(BaseModel):
    email: EmailStr
    code: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "goturkey@example.com",
                "code": "123456",
            }
        }
    }


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "goturkey@example.com",
                "password": "password123!",
            }
        }
    }


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    birthday: Optional[date] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "고터키",
                "birthday": "1995-05-21",
                "bio": "안녕하세요!",
                "profile_image": "https://example.com/profile.png",
            }
        }
    }


# ========================
# 응답(Response)
# ========================

class UserCreateResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    birthday: date
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserVerifySuccessResponse(BaseModel):
    success: bool

    model_config = {"json_schema_extra": {"example": {"success": True}}}


class UserVerifyErrorResponse(BaseModel):
    errors: List[str]
    status: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "errors": ["CODE_INVALID", "CODE_EXPIRED"],
                "status": [400],
            }
        }
    }

class UserCreateErrorResponse(BaseModel):
    error: str



class UserLoginResponse(BaseModel):
    success: bool
    last_login_at: Union[datetime, str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "last_login_at": "2025-09-30T08:13:45.123Z"
            }
        }
    }
#구글 로그인
class GoogleCallbackRequest(BaseModel):
    code: str = Field(..., description="구글 OAuth 인가 코드")


    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "4/0AfJohXyZ_example_code_from_google",
            }
        }
    )

class GoogleCallbackResponse(BaseModel):

    redirect_url: str = Field(..., description="로그인 성공 후 이동할 프론트엔드 URL")
    last_login_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "redirect_url": "https://your-frontend-domain.com/auth/success",
                "last_login_at":"2025-09-30T08:13:45.123Z",
            }
        }
    )


class GoogleLoginErrorResponse(BaseModel):

    error: str = Field(..., description="오류 코드 또는 메시지")
    status_code: int = Field(..., description="HTTP 상태 코드")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "GOOGLE_TOKEN_INVALID",
                "status_code": 400
            }
        }
    )



KST = timezone(timedelta(hours=9))  # ✅ 한국시간 (UTC+9)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    birthday: date
    is_email_verified: bool
    is_active: bool
    is_superuser: bool
    is_google_user: bool = False
    last_login_at: Union[datetime, None] = None  # ✅ 변환 대상
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    # ✅ 마지막 로그인 시간만 한국시간으로 변환
    @field_serializer("last_login_at")
    def serialize_last_login(self, value: datetime | None, _info: Any) -> str | None:
        if not value:
            return None
        return value.astimezone(KST).strftime("%Y-%m-%d %H:%M")



class UserUpdateResponse(BaseModel):
    id: int
    username: str
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserDeleteResponse(BaseModel):
    success: bool

    model_config = {
        "json_schema_extra": {
            "example": {"success": True}
        }
    }
#관리자

class AdminUserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_email_verified: bool
    is_superuser: bool
    is_google_user: bool
    last_login_at: Union[datetime, None] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("last_login_at")
    def serialize_last_login_at(self, value: datetime | None) -> str | None:
        if value:
            return value.astimezone(KST).strftime("%Y-%m-%d %H:%M")
        return None


class AdminUserListResponse(BaseModel):
    users: List[AdminUserOut]
    total: int

    model_config = ConfigDict(from_attributes=True)


#  비밀번호 재설정 요청
class PasswordResetConfirm(BaseModel):
    email: EmailStr
    new_password: str
    new_password_check: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "old_password123",
                "new_password": "new_password123",
                "new_password_check": "new_password123"
            }
        }
    }

class PasswordResetRequest(BaseModel):
    email: EmailStr

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "test@test.com",
            }
        }
    }

#비밀번호 번경
class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str
    new_password_check: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "old_password": "old_password123",
                "new_password": "new_password123",
                "new_password_check": "new_password123"
            }
        }
    }

