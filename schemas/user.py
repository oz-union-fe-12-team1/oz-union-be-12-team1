from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime

# ========================
# 요청(Request)
# ========================

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    password_check: str
    username: str
    birthday: date
    profile_image: Optional[str] = None   

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "goturkey@example.com",
                "password": "password123!",
                "password_check": "password123!",
                "username": "고터키",
                "birthday": "1995-05-21",
                "profile_image": "https://nyangbucket.s3.ap-northeast-2.amazonaws.com/uploads/cat.png"
            }
        }
    }


class UserVerifyRequest(BaseModel):
    email: EmailStr
    code: str

    model_config = {
        "json_schema_extra": {
            "example": {"email": "goturkey@example.com", "code": "123456"}
        }
    }


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {"email": "goturkey@example.com", "password": "password123!"}
        }
    }


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    birthday: Optional[date] = None  
    bio: Optional[str] = None
    profile_image: Optional[str] = None   

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "고터키",
                "birthday": "1995-05-21",
                "bio": "안녕하세요!",
                "profile_image": "https://nyangbucket.s3.ap-northeast-2.amazonaws.com/uploads/cat.png"
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
    profile_image: Optional[str] = None   
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserCreateErrorResponse(BaseModel):
    errors: List[str]
    status: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "errors": ["EMAIL_ALREADY_EXISTS", "INVALID_PASSWORD_FORMAT"],
                "status": 400
            }
        }
    }


class UserVerifySuccessResponse(BaseModel):
    success: bool

    model_config = {"json_schema_extra": {"example": {"success": True}}}


class UserVerifyErrorResponse(BaseModel):
    errors: List[str]
    status: int

    model_config = {
        "json_schema_extra": {
            "example": {"errors": ["CODE_INVALID", "CODE_EXPIRED"], "status": 400}
        }
    }


class UserLoginResponse(BaseModel):
    success: bool

    model_config = {"json_schema_extra": {"example": {"success": True}}}


# 구글 로그인
class GoogleCallbackRequest(BaseModel):

    code: str = Field(..., description="구글 OAuth 인가 코드")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "4/0AfJohXyZ_example_code_from_google"
            }
        }
    )

class GoogleCallbackResponse(BaseModel):

    redirect_url: str = Field(..., description="로그인 성공 후 이동할 프론트엔드 URL")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "redirect_url": "https://your-frontend-domain.com/auth/success"
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

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    birthday: date
    profile_image: Optional[str] = None   
    is_email_verified: bool
    is_active: bool
    is_superuser: bool
    is_google_user: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateResponse(BaseModel):
    id: int
    username: str
    bio: Optional[str] = None
    profile_image: Optional[str] = None   
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserDeleteResponse(BaseModel):
    success: bool

    model_config = {"json_schema_extra": {"example": {"success": True}}}


# 관리자
class AdminUserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    profile_image: Optional[str] = None   
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
    is_superuser: bool = False

    model_config = {"from_attributes": True}


class AdminUserListResponse(BaseModel):
    users: List[AdminUserOut]
    total: int

model_config = {
            "json_schema_extra": {
                "example": {
                    "users": [
                        {
                            "id": 1,
                            "email": "admin@example.com",
                            "username": "관리자",
                            "is_active": True,
                            "is_email_verified": True,
                            "created_at": "2025-09-25T12:00:00",
                            "updated_at": "2025-09-25T12:00:00",
                            "is_superuser": True,
                        }
                    ],
                    "total": 1,
                }
            }
        }


# 비밀번호 재설정
class PasswordResetConfirm(BaseModel):
    email: EmailStr
    new_password: str
    new_password_check: str
    token: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "goturkey@example.com",
                "new_password": "new_password123",
                "new_password_check": "new_password123",
                "token": "abcdef123456"
            }
        }
    }


class PasswordResetRequest(BaseModel):
    email: EmailStr

    model_config = {"json_schema_extra": {"example": {"email": "test@test.com"}}}


# 비밀번호 변경
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
