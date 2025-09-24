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
from services.user_service import UserService
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


# -----------------------------
# 회원가입
# -----------------------------
@router.post("/register", response_model=UserCreateResponse)
async def register_user(request: UserCreateRequest) -> UserCreateResponse:

    # 이메일 중복 확인
    if await UserService.get_user_by_email(request.email):
        raise HTTPException(status_code=400, detail="EMAIL_ALREADY_EXISTS")

    # ✅ 수정됨: request 객체 그대로 전달
    user = await AuthService.register(request)
    if not user:
        raise HTTPException(status_code=500, detail="USER_CREATION_FAILED")

    # ✅ 응답 스키마에 맞게 변환
    return UserCreateResponse.model_validate(user)


# -----------------------------
# 이메일 인증 (코드 방식)
# -----------------------------
@router.post(
    "/email/verify",
    response_model=UserVerifySuccessResponse,
    responses={400: {"model": UserVerifyErrorResponse}},
)
async def verify_email(request: UserVerifyRequest) -> dict[str, bool]:
    result = await AuthService.verify_email_token(email=request.email, code=request.code)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return {"success": True}


# -----------------------------
# 로그인
# -----------------------------
@router.post("/login", response_model=UserLoginResponse)
async def login_user(request: UserLoginRequest) -> UserLoginResponse:
    result = await AuthService.login(request.email, request.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return UserLoginResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type="bearer",
    )


# -----------------------------
# 구글 로그인
# -----------------------------
@router.post("/google", response_model=GoogleLoginResponse)
async def google_login(request: GoogleLoginRequest) -> GoogleLoginResponse:
    result = await AuthService.google_login(
        google_id="dummy_google_id",   # 실제 구현 시 구글 토큰에서 추출
        email="goturkey@example.com",  # 실제 구현 시 구글 API에서 추출
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
async def refresh_token(refresh_token: str) -> UserLoginResponse:
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
async def logout_user(token: str) -> dict[str, bool]:
    revoked = await AuthService.logout(token)
    if not revoked:
        raise HTTPException(status_code=400, detail="LOGOUT_FAILED")
    return {"success": True}
