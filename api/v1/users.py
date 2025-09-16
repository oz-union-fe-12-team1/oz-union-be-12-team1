from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from typing import Optional

from app.models.user import (
    UserCreate, UserLogin, UserUpdate, UserResponse, 
    Token, SocialLogin, RefreshToken, ForgotPassword, 
    ResetPassword, UserSettingsUpdate, APIResponse
)
from app.services.user_service import user_service
from app.core.security import create_access_token, verify_token
from app.core.config import settings

# 라우터 생성
router = APIRouter()

# 현재 사용자 가져오기 (의존성)
def get_current_user(token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = user_service.get_user_by_id(int(token["user_id"]))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

# ========== 인증 관련 API ==========

@router.post("/auth/register", response_model=APIResponse)
def register(user_data: UserCreate):
    """회원가입"""
    # 이메일 중복 체크
    existing_user = user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 사용자명 중복 체크 (있는 경우)
    if user_data.username:
        existing_username = user_service.get_user_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    new_user = user_service.create_user(user_data)
    
    return APIResponse(
        success=True,
        data={
            "user_id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "is_email_verified": new_user.is_email_verified
        }
    )

@router.post("/auth/login", response_model=APIResponse)
def login(user_data: UserLogin):
    """로그인"""
    user = user_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated"
        )
    
    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    
    # 리프레시 토큰 생성 (더 긴 만료시간)
    refresh_token_expires = timedelta(days=7)  # 7일
    refresh_token = create_access_token(
        data={"sub": str(user.id), "type": "refresh"}, 
        expires_delta=refresh_token_expires
    )
    
    # 디바이스 정보 저장 (세션 관리용)
    if user_data.device_info:
        user_service.create_session(user.id, access_token, user_data.device_info)
    
    return APIResponse(
        success=True,
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    )

@router.post("/auth/social/login", response_model=APIResponse)
def social_login(social_data: SocialLogin):
    """소셜 로그인"""
    # TODO: 소셜 로그인 구현
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Social login not implemented yet"
    )

@router.post("/auth/refresh", response_model=APIResponse)
def refresh_token(token_data: RefreshToken):
    """토큰 갱신"""
    # TODO: 리프레시 토큰 검증 및 새 토큰 발급
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented yet"
    )

@router.post("/auth/forgot-password", response_model=APIResponse)
def forgot_password(email_data: ForgotPassword):
    """비밀번호 재설정 요청"""
    # TODO: 이메일 발송 구현
    user = user_service.get_user_by_email(email_data.email)
    if not user:
        
        pass
    
    return APIResponse(
        success=True,
        data={"message": "Reset email sent if account exists"}
    )

@router.post("/auth/reset-password", response_model=APIResponse)
def reset_password(reset_data: ResetPassword):
    """비밀번호 재설정"""
    # TODO: 토큰 검증 및 비밀번호 변경
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset not implemented yet"
    )

# ========== 사용자 프로필 관련 API ==========

@router.get("/users/me", response_model=APIResponse)
def get_my_profile(current_user = Depends(get_current_user)):
    """내 프로필 조회"""
    # 사용자 설정도 함께 조회
    settings = user_service.get_user_settings(current_user.id)
    
    return APIResponse(
        success=True,
        data={
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "profile_image": current_user.profile_image,
            "is_email_verified": current_user.is_email_verified,
            "created_at": current_user.created_at.isoformat(),
            "settings": settings.dict() if settings else {}
        }
    )

@router.put("/users/me", response_model=APIResponse)
def update_my_profile(
    user_data: UserUpdate,
    current_user = Depends(get_current_user)
):
    """프로필 수정"""
    updated_user = user_service.update_user(current_user.id, user_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    return APIResponse(
        success=True,
        data=updated_user.dict()
    )

@router.put("/users/me/settings", response_model=APIResponse)
def update_my_settings(
    settings_data: UserSettingsUpdate,
    current_user = Depends(get_current_user)
):
    """사용자 설정 수정"""
    updated_settings = user_service.update_user_settings(current_user.id, settings_data)
    
    if not updated_settings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update settings"
        )
    
    return APIResponse(
        success=True,
        data=updated_settings.dict()
    )

@router.delete("/users/me", response_model=APIResponse)
def deactivate_my_account(current_user = Depends(get_current_user)):
    """계정 비활성화"""
    success = user_service.deactivate_user(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to deactivate account"
        )
    
    return APIResponse(
        success=True,
        data={"message": "Account deactivated successfully"}
    )