from pydantic import BaseModel, EmailStr, Field
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


class GoogleLoginRequest(BaseModel):
    access_token: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "ya29.A0ARrdaM...",
            }
        }
    }


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "고터키",
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

    model_config = {"from_attributes": True}   # ✅ Pydantic v2


class UserVerifySuccessResponse(BaseModel):
    success: bool

    model_config = {
        "json_schema_extra": {"example": {"success": True}}
    }


class UserVerifyErrorResponse(BaseModel):
    errors: List[str]
    status: List[int]

    model_config = {
        "json_schema_extra": {
            "example": {
                "errors": ["CODE_INVALID", "CODE_EXPIRED"],
                "status": [400],
            }
        }
    }


class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
            }
        }
    }


class GoogleLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
            }
        }
    }


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    birthday: date
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminUserOut(UserOut):
    is_superuser: bool = False

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: List[UserOut]
    total: int

    model_config = {"from_attributes": True}


class AdminUserListResponse(BaseModel):
    users: List[AdminUserOut]
    total: int

    model_config = {"from_attributes": True}


class UserUpdateResponse(BaseModel):
    id: int
    username: str
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserDeleteResponse(BaseModel):
    message: str = "User deleted successfully"

    model_config = {
        "json_schema_extra": {
            "example": {"message": "User deleted successfully"}
        }
    }