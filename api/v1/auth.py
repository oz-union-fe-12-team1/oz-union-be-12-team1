from datetime import timezone, datetime, timedelta
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from typing import Dict

from repositories.user_repo import UserRepository
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
        error = result.get("error")
        if error == "EMAIL_ALREADY_EXISTS":
            raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")
        raise HTTPException(status_code=400, detail="인증번호 발송 중 오류가 발생했습니다.")
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
    result = await AuthService.verify_email_code(email=request.email, code=request.code)
    if not result.get("success"):
        error = result.get("error")
        if error == "TOKEN_EXPIRED":
            raise HTTPException(status_code=400, detail="인증번호가 만료되었습니다.")
        elif error == "TOKEN_INVALID":
            raise HTTPException(status_code=400, detail="인증번호가 올바르지 않습니다.")
        elif error == "ALREADY_VERIFIED":
            raise HTTPException(status_code=409, detail="이미 인증된 이메일입니다.")
        else:
            raise HTTPException(status_code=400, detail="인증번호 확인 중 오류가 발생했습니다.")
    return {"success": True}


# ---------------------------
# 비밀번호 재설정 요청 (/auth/password/reset-request)
# ---------------------------
@router.post(
    "/password/reset-request",
    response_model=UserVerifySuccessResponse,
    responses={404: {"model": UserVerifyErrorResponse}},
)
async def password_reset_request(request: PasswordResetRequest) -> dict[str, bool]:
    result = await AuthService.request_password_reset(request.email)

    if not result.get("success"):
        error = result.get("error")
        if error == "USER_NOT_FOUND":
            raise HTTPException(status_code=404, detail="이메일을 다시 확인해주세요.")
        else:
            raise HTTPException(status_code=400, detail="비밀번호 재설정 요청 중 오류가 발생했습니다.")

    return {"success": True}


# ---------------------------
# 비밀번호 재설정 확인 (/auth/password/reset-confirm)
# ---------------------------
@router.post(
    "/password/reset-confirm",
    response_model=UserVerifySuccessResponse,
    responses={
        400: {"model": UserVerifyErrorResponse},
        404: {"model": UserVerifyErrorResponse},
    },
)
async def password_reset_confirm(request: PasswordResetConfirm) -> dict[str, bool]:
    result = await AuthService.confirm_password_reset(
        request.email, request.new_password, request.new_password_check
    )

    if not result.get("success"):
        error = result.get("error")

        if error == "USER_NOT_FOUND":
            raise HTTPException(status_code=404, detail="이메일을 다시 한 번 확인해주세요.")
        elif error == "PASSWORD_MISMATCH":
            raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")
        else:
            raise HTTPException(status_code=400, detail="비밀번호 재설정 중 오류가 발생했습니다.")

    return {"success": True}


# ---------------------------
# 회원가입 (/auth/register)
# ---------------------------
@router.post("/register", response_model=UserCreateResponse)
async def register_user(request: UserCreateRequest) -> UserCreateResponse:
    """
    이메일 인증 성공 후 회원가입
    (이미 인증된 이메일만 요청되므로 실패 시 예외 처리 불필요)
    """
    user = await AuthService.register(request)
    return UserCreateResponse.model_validate(user)


# -----------------------------
# 로그인 (/auth/login)
# -----------------------------
@router.post("/login", response_model=UserLoginResponse)
async def login_user(request: UserLoginRequest, response: Response) -> UserLoginResponse:
    result = await AuthService.login(request.email, request.password)

    if "error" in result:
        error = result["error"]

        if error == "USER_NOT_FOUND":
            raise HTTPException(status_code=400, detail="이메일 또는 비밀번호를 다시 확인해주세요.")
        elif error == "INVALID_CREDENTIALS":
            raise HTTPException(status_code=400, detail="이메일 또는 비밀번호를 다시 확인해주세요.")
        elif error == "ACCOUNT_DISABLED":
            raise HTTPException(status_code=400, detail="로그인 중 오류가 발생했습니다. 고객센터로 문의해주세요.")
        else:
            raise HTTPException(status_code=400, detail="로그인 중 오류가 발생했습니다. 고객센터로 문의해주세요.")

    # ✅ JWT 쿠키 설정
    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=True,
        samesite="none"
    )
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=True,
        samesite="none"
    )

    # ✅ 로그인 시간 업데이트
    user = await UserRepository.get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=404, detail="등록되지 않은 이메일입니다.")

    user.last_login_at = datetime.now(timezone.utc)
    await user.save(update_fields=["last_login_at"])

    # ✅ 한국시간 변환
    KST = timezone(timedelta(hours=9))
    kst_time = user.last_login_at.astimezone(KST).strftime("%Y-%m-%d %H:%M")

    return UserLoginResponse(success=True, last_login_at=kst_time)


# -----------------------------
# 로그아웃 (/auth/logout)
# -----------------------------
@router.post("/logout")
async def logout_user(request: Request) -> Response:
    token: str | None = request.cookies.get("refresh_token")

    if token is None:
        raise HTTPException(status_code=401, detail="로그인 상태가 아닙니다.")

    revoked = await AuthService.logout(token)
    if not revoked:
        raise HTTPException(status_code=400, detail="로그아웃 중 오류가 발생했습니다.")

    # ✅ 쿠키 삭제
    response = JSONResponse({"success": True})
    response.delete_cookie(
        "refresh_token",
        httponly=True,
        secure=True,
        samesite="none",
        path="/"
    )
    response.delete_cookie(
        "access_token",
        httponly=True,
        secure=True,
        samesite="none",
        path="/"
    )

    return response