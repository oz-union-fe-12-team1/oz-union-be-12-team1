from fastapi import APIRouter, HTTPException
from schemas.user import (
    UserCreateRequest,
    UserCreateResponse,
    UserVerifyRequest,
    UserVerifySuccessResponse,
    UserLoginRequest,
    UserLoginResponse,
    GoogleLoginRequest,
    GoogleLoginResponse,
)
from schemas.auth import LogoutResponse   # ✅ 새로 추가된 스키마
from services.auth_service import AuthService
from repositories.user_repo import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


# -----------------------------
# 회원가입
# -----------------------------
@router.post("/register", response_model=UserCreateResponse)
async def register_user(request: UserCreateRequest):
    existing_user = await UserRepository.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="EMAIL_ALREADY_EXISTS")

    user = await AuthService.register(request)
    if not user:
        raise HTTPException(status_code=500, detail="USER_CREATION_FAILED")

    return user


# -----------------------------
# 이메일 인증
# -----------------------------
@router.post("/email/verify", response_model=UserVerifySuccessResponse)
async def verify_email(request: UserVerifyRequest):
    result = await AuthService.verify_email_token(email=request.email, code=request.code)
    if not result.success:
        raise HTTPException(status_code=400, detail="EMAIL_VERIFICATION_FAILED")
    return result


# -----------------------------
# 로그인
# -----------------------------
@router.post("/login", response_model=UserLoginResponse)
async def login_user(request: UserLoginRequest):
    result = await AuthService.login(request.email, request.password)
    if not result:
        raise HTTPException(status_code=400, detail="LOGIN_FAILED")
    return result


# -----------------------------
# 구글 로그인
# -----------------------------
@router.post("/google", response_model=GoogleLoginResponse)
async def google_login(request: GoogleLoginRequest):
    result = await AuthService.google_login(
        google_id="dummy_google_id",   # TODO: 구글 OAuth 연동
        email="goturkey@example.com",  # TODO: 실제 구글 API 응답으로 교체
    )
    return result


# -----------------------------
# 토큰 갱신
# -----------------------------
@router.post("/refresh", response_model=UserLoginResponse)
async def refresh_token(refresh_token: str):
    new_tokens = await AuthService.refresh_token(refresh_token)
    if not new_tokens:
        raise HTTPException(status_code=400, detail="TOKEN_INVALID_OR_EXPIRED")
    return new_tokens


# -----------------------------
# 로그아웃
# -----------------------------
@router.post("/logout", response_model=LogoutResponse)
async def logout_user(token: str):
    revoked = await AuthService.logout(token)
    if not revoked:
        raise HTTPException(status_code=400, detail="LOGOUT_FAILED")
    return LogoutResponse(success=True)   # ✅ 스키마 통일
