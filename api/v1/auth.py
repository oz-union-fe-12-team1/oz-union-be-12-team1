from fastapi import APIRouter, HTTPException, Response,Request
from fastapi.responses import JSONResponse
from typing import Dict, Union

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
    UserCreateErrorResponse
)
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
    responses={400: {"model": UserCreateErrorResponse}},
)
async def register_user(request: UserCreateRequest) -> UserCreateResponse:
    """
    이메일 인증 성공 후 회원가입
    """
    user = await AuthService.register(request)

    if not user:
        # 실패 시
        raise HTTPException(
            status_code=400,
            detail="EMAIL_NOT_VERIFIED_OR_ALREADY_EXISTS"
        )

    # 성공 시
    return UserCreateResponse.model_validate(user)
# -----------------------------
# 로그인
# -----------------------------
@router.post("/login", response_model=UserLoginResponse)
async def login_user(request: UserLoginRequest, response: Response) -> UserLoginResponse:
    result = await AuthService.login(request.email, request.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        # 로컬 테스트용
        # http 환경에서는 secure=True + samesite="none" 불가능
        # 배포 시(https 환경)에는 반드시 secure=True, samesite="none" 으로 되돌릴 것
    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=False,     # 로컬에서는 False
        samesite="lax"    # 로컬에서는 lax
    )
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,     # 로컬에서는 False
        samesite="lax"    # 로컬에서는 lax
    )
    return UserLoginResponse(success=True)

# 로그아웃
# -----------------------------
@router.post("/logout")
async def logout_user(request: Request) -> Response:
    token: str | None = request.cookies.get("refresh_token")
    if token is None:
        raise HTTPException(status_code=401, detail="NOT_AUTHENTICATED")

    revoked = await AuthService.logout(token)
    if not revoked:
        raise HTTPException(status_code=400, detail="LOGOUT_FAILED")

    response = JSONResponse({"success": True})
    response.delete_cookie("refresh_token")
    return response

