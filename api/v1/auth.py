from fastapi import APIRouter, HTTPException, Depends
from schemas.user import (
    UserCreateRequest,
    UserCreateResponse,
    UserVerifyRequest,
    UserVerifySuccessResponse,
    UserVerifyErrorResponse,
    UserLoginRequest,
    UserLoginResponse,
    GoogleLoginRequest,
    GoogleLoginResponse,
)
from services.user_service import UserService
from services.auth_service import AuthService
from passlib.hash import bcrypt

router = APIRouter(prefix="/auth", tags=["auth"])


# -----------------------------
# 회원가입
# -----------------------------
@router.post("/register", response_model=UserCreateResponse)
async def register_user(request: UserCreateRequest):

    # 이메일 중복 확인
    if await UserService.get_user_by_email(request.email):
        raise HTTPException(status_code=400, detail="EMAIL_ALREADY_EXISTS")


    # 비밀번호 해싱
    password_hash = bcrypt.hash(request.password)

    # 유저 생성
    user = await UserService.create_user(
        email=request.email,
        password_hash=password_hash,
        username=request.username,
        birthday=request.birthday
    )
    if not user:
        raise HTTPException(status_code=500, detail="USER_CREATION_FAILED")

    return user


# -----------------------------
# 이메일 인증
# -----------------------------
@router.post("/email/verify", response_model=UserVerifySuccessResponse, responses={400: {"model": UserVerifyErrorResponse}})
async def verify_email(request: UserVerifyRequest):
    result = await AuthService.verify_email_token(email=None, token=request.token)  # email은 토큰 안에서 꺼내옴
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return {"success": True}


# -----------------------------
# 로그인
# -----------------------------
@router.post("/login", response_model=UserLoginResponse)
async def login_user(request: UserLoginRequest):
    result = await AuthService.login(request.email, request.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": "bearer",
    }


# -----------------------------
# 구글 로그인
# -----------------------------
@router.post("/google", response_model=GoogleLoginResponse)
async def google_login(request: GoogleLoginRequest):
    # ⚠️ 실제 구글 OAuth 검증은 생략. access_token 값만 전달받아 처리.
    result = await AuthService.google_login(
        google_id="dummy_google_id",  # 실제 구현 시 구글 토큰에서 추출
        email="goturkey@example.com",  # 실제 구현 시 구글 API에서 추출
        nickname="고터키",
    )
    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": "bearer",
    }


# -----------------------------
# 토큰 갱신
# -----------------------------
@router.post("/refresh", response_model=UserLoginResponse)
async def refresh_token(refresh_token: str):
    new_access = await AuthService.refresh_token(refresh_token)
    if not new_access:
        raise HTTPException(status_code=400, detail="TOKEN_INVALID_OR_EXPIRED")
    return {
        "access_token": new_access,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# -----------------------------
# 로그아웃
# -----------------------------
@router.post("/logout")
async def logout_user(token: str):
    revoked = await AuthService.logout(token)
    if not revoked:
        raise HTTPException(status_code=400, detail="LOGOUT_FAILED")
    return {"success": True}
