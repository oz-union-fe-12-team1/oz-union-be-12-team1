from fastapi import APIRouter, HTTPException
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
from services.auth_service import AuthService
from repositories.user_repo import UserRepository  # ✅ UserService 대신 직접 Repo 호출

router = APIRouter(prefix="/auth", tags=["auth"])


# -----------------------------
# 회원가입
# -----------------------------
@router.post("/register", response_model=UserCreateResponse)
async def register_user(request: UserCreateRequest):
    # ✅ 이메일 중복 확인
    existing_user = await UserRepository.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="EMAIL_ALREADY_EXISTS")

    user = await AuthService.register(request)
    if not user:
        raise HTTPException(status_code=500, detail="USER_CREATION_FAILED")

    return UserCreateResponse.model_validate(user, from_attributes=True)


# -----------------------------
# 이메일 인증 (코드 방식)
# -----------------------------
@router.post(
    "/email/verify",
    response_model=UserVerifySuccessResponse,
    responses={400: {"model": UserVerifyErrorResponse}},
)
async def verify_email(request: UserVerifyRequest):
    result = await AuthService.verify_email_token(email=request.email, code=request.code)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return UserVerifySuccessResponse(success=True)


# -----------------------------
# 로그인
# -----------------------------
@router.post("/login", response_model=UserLoginResponse)
async def login_user(request: UserLoginRequest):
    result = await AuthService.login(request.email, request.password)
    if not result or "error" in result:
        raise HTTPException(status_code=400, detail=result.get("error", "LOGIN_FAILED"))

    return UserLoginResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type="bearer",
    )


# -----------------------------
# 구글 로그인
# -----------------------------
@router.post("/google", response_model=GoogleLoginResponse)
async def google_login(request: GoogleLoginRequest):
    # 실제 구현에서는 request.access_token → 구글 API로 검증 후 google_id, email 추출
    result = await AuthService.google_login(
        google_id="dummy_google_id",   # TODO: 구글 OAuth로 교체
        email="goturkey@example.com",  # TODO: 구글 API로 교체
    )
    return GoogleLoginResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type="bearer",
    )


# -----------------------------
# 토큰 갱신
# -----------------------------
@router.post("/refresh", response_model=UserLoginResponse)
async def refresh_token(refresh_token: str):
    new_access = await AuthService.refresh_token(refresh_token)
    if not new_access:
        raise HTTPException(status_code=400, detail="TOKEN_INVALID_OR_EXPIRED")

    return UserLoginResponse(
        access_token=new_access,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# -----------------------------
# 로그아웃
# -----------------------------
@router.post("/logout")
async def logout_user(token: str):
    revoked = await AuthService.logout(token)
    if not revoked:
        raise HTTPException(status_code=400, detail="LOGOUT_FAILED")
    return {"success": True}
