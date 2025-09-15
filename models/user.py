from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

# ========== 요청 스키마 ==========

class UserCreate(BaseModel):
    """회원가입 요청 데이터"""
    email: EmailStr
    password: str
    username: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if v and len(v) < 2:
            raise ValueError('사용자명은 최소 2자 이상이어야 합니다')
        return v

class UserLogin(BaseModel):
    """로그인 요청 데이터"""
    email: EmailStr
    password: str
    device_info: Optional[dict] = None  

class UserUpdate(BaseModel):
    """사용자 정보 수정 요청 데이터"""
    username: Optional[str] = None
    profile_image: Optional[str] = None

class PasswordUpdate(BaseModel):
    """비밀번호 변경 요청 데이터"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('새 비밀번호는 최소 8자 이상이어야 합니다')
        return v

# ========== 응답 스키마 ==========

class UserResponse(BaseModel):
    """사용자 정보 응답 데이터"""
    User_id: int
    email: str
    username: Optional[str]
    profile_image: Optional[str]
    is_active: bool
    is_email_verified: bool
    login_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    """사용자 프로필 응답 (간단한 정보)"""
    User_id: int
    username: Optional[str]
    email: str
    profile_image: Optional[str]

class Token(BaseModel):
    """토큰 응답 데이터"""
    access_token: str
    refresh_token: str  
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class UserSettings(BaseModel):
    """사용자 설정 데이터"""
    timezone: str = "Asia/Seoul"
    language: str = "ko-KR"
    date_format: str = "YYYY-MM-DD"
    time_format: str = "HH:mm"
    theme: str = "system"
    location_name: Optional[str] = None

class UserPermissions(BaseModel):
    """사용자 권한 데이터"""
    notification_permission: bool = False
    calendar_permission: bool = False
    microphone_permission: bool = False
    location_permission: bool = False

# ========== API 명세서 추가 스키마 ==========

class SocialLogin(BaseModel):
    """소셜 로그인 요청 데이터"""
    provider: str  # google|kakao|naver
    access_token: str

class RefreshToken(BaseModel):
    """토큰 갱신 요청 데이터"""
    refresh_token: str

class ForgotPassword(BaseModel):
    """비밀번호 재설정 요청 데이터"""
    email: EmailStr

class ResetPassword(BaseModel):
    """비밀번호 재설정 데이터"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('새 비밀번호는 최소 8자 이상이어야 합니다')
        return v

class UserSettingsUpdate(BaseModel):
    """사용자 설정 수정 요청 데이터"""
    language: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    default_location_lat: Optional[float] = None
    default_location_lon: Optional[float] = None
    location_name: Optional[str] = None

# ========== 응답 포맷 (API 명세서 형식) ==========

class APIResponse(BaseModel):
    """API 표준 응답 형식"""
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
    error: Optional[str] = None

class UserInDB(BaseModel):
    """데이터베이스에서 가져온 사용자 데이터 (비밀번호 포함)"""
    User_id: int
    email: str
    password_hash: str
    username: Optional[str]
    profile_image: Optional[str]
    is_active: bool
    is_email_verified: bool
    email_verified_at: Optional[datetime]
    last_login_at: Optional[datetime]
    login_count: int
    social_provider: Optional[str]
    social_id: Optional[str]
    created_at: datetime
    updated_at: datetime