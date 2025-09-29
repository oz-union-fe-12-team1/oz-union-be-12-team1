from fastapi import APIRouter, HTTPException, Response
from typing import Dict, Union
from urllib.parse import urlencode

import core.google_handler
from schemas.user import (
    UserCreateRequest,
    UserCreateResponse,
    UserVerifyRequest,
    UserVerifySuccessResponse,
    UserVerifyErrorResponse,
    UserLoginRequest,
    UserLoginResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    GoogleCallbackResponse,
    GoogleLoginErrorResponse,
)
from fastapi.responses import RedirectResponse
from services.user_service import UserService
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------
# 이메일 인증번호 발송 (/auth/email/verify_code)
# ---------------------------
@router.post(
    "/email/verify_code",
    response_model=UserVerifySuccessResponse,
    responses={400: {"model": UserVerifyErrorResponse}},
)
async def send_verification_code(email: str) -> Dict[str, bool]:
    """
    이메일 중복 확인 후 인증번호 발송
    """
    result = await AuthService.send_verification_email_code(email)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return {"success": True}


# ---------------------------
# 이메일 인증번호 검증 (/auth/email/verify)
# ---------------------------
@router.post(
    "/email/verify",
    response_model=UserVerifySuccessResponse,
    responses={
        400: {"model": UserVerifyErrorResponse},
        409: {"model": UserVerifyErrorResponse},
        429: {"model": UserVerifyErrorResponse},
    },
)
async def verify_email(request: UserVerifyRequest) -> Dict[str, bool]:
    """
    사용자가 입력한 인증번호 검증
    """
    result = await AuthService.verify_email_code(
        email=request.email,
        code=request.code,
    )
    if not result.get("success"):
        error = result.get("error")
        if error == "ALREADY_VERIFIED":
            raise HTTPException(status_code=409, detail=error)
        elif error == "RATE_LIMITED":
            raise HTTPException(status_code=429, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)
    return {"success": True}

#----------------------------
# 비밀번호 재설정(분실)
#----------------------------
@router.post(
    "/password/reset-request",
    response_model=UserVerifySuccessResponse,
    responses={404: {"model": UserVerifyErrorResponse}},
)
async def password_reset_request(
    request: PasswordResetRequest,   # ✅ request body를 Pydantic 모델로 받음
) -> dict[str, bool]:

    result = await AuthService.request_password_reset(request.email)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return {"success": True}

@router.post(
    "/password/reset-confirm",
    response_model=UserVerifySuccessResponse,
    responses={
        400: {"model": UserVerifyErrorResponse},
        404: {"model": UserVerifyErrorResponse},
    },
)
async def password_reset_confirm(
    request: PasswordResetConfirm,  # ✅ 이메일 + 새 비밀번호를 JSON body로 받음
) -> dict[str, bool]:
    result = await AuthService.confirm_password_reset(
        request.email,
        request.new_password,
        request.new_password_check,
    )
    if not result.get("success"):
        error = result.get("error")
        if error == "USER_NOT_FOUND":
            raise HTTPException(status_code=404, detail=error)
        elif error == "PASSWORD_MISMATCH":
            raise HTTPException(status_code=400, detail=error)
    return {"success": True}

# ---------------------------
# 회원가입 (/auth/register)
# ---------------------------
@router.post(
    "/register",
    response_model=UserCreateResponse,
    responses={400: {"model": UserVerifyErrorResponse}},
)
async def register_user(request: UserCreateRequest) -> UserCreateResponse:
    """
    이메일 인증 성공 후 회원가입
    """
    user = await AuthService.register(request)
    if not user:
        raise HTTPException(status_code=400, detail="EMAIL_NOT_VERIFIED_OR_ALREADY_EXISTS")
    return UserCreateResponse.model_validate(user)
# -----------------------------
# 로그인
# -----------------------------
@router.post("/login", response_model=UserLoginResponse)
async def login_user(request: UserLoginRequest, response: Response) -> UserLoginResponse:
    result = await AuthService.login(request.email, request.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=True,
        samesite="None"
    )
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=True,
        samesite="None"
    )
    return UserLoginResponse(success=True)
# -----------------------------
# 구글 로그인 관련
# -----------------------------

@router.get("/google/login")
async def google_login() -> RedirectResponse:
    # google_auth_url = (
    #     "https://accounts.google.com/o/oauth2/v2/auth"
    #     "?response_type=code"
    #     f"&client_id={core.google_handler.GOOGLE_CLIENT_ID}"
    #     f"&redirect_uri={core.google_handler.GOOGLE_REDIRECT_URI}"
    #     "&scope=openid%20email%20profile"
    # )

    params = {
        "response_type": "code",
        "client_id": core.google_handler.GOOGLE_CLIENT_ID,
        "redirect_uri": core.google_handler.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
    }

    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

    print(google_auth_url)
    return RedirectResponse(url=google_auth_url)


@router.get(
    "/google/callback",
    response_model=GoogleCallbackResponse,
    responses={400: {"model": GoogleLoginErrorResponse}},
)
async def google_callback(code: str) -> GoogleCallbackResponse:
    try:
        data = await AuthService.google_callback(code)  # dict
        return GoogleCallbackResponse(**data)           # 스키마 변환
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="GOOGLE_TOKEN_INVALID"
        )
# # -----------------------------
# # 토큰 갱신
# # -----------------------------
# @router.post("/refresh", response_model=UserLoginResponse)
# async def refresh_token(response: Response, refresh_token: str) -> UserLoginResponse:
#     new_access = await AuthService.refresh_token(refresh_token)
#     if not new_access:
#         raise HTTPException(status_code=400, detail="TOKEN_INVALID_OR_EXPIRED")
#
#     #새 access_token을 쿠키에 갱신
#     response.set_cookie(
#         key="access_token",
#         value=new_access,
#         httponly=True,
#         secure=True,
#         samesite="lax"
#     )
#     # refresh_token도 그대로 갱신(선택)
#     response.set_cookie(
#         key="refresh_token",
#         value=refresh_token,
#         httponly=True,
#         secure=True,
#         samesite="lax"
#     )
#
#     return UserLoginResponse(success=True)
#

# --------------------------
# 로그아웃
# -----------------------------
@router.post("/logout")
async def logout_user(token: str) -> dict[str, bool]:
    revoked = await AuthService.logout(token)
    if not revoked:
        raise HTTPException(status_code=400, detail="LOGOUT_FAILED")
    return {"success": True}
