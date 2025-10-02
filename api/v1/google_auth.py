from fastapi import APIRouter, HTTPException, Response
from urllib.parse import urlencode

from schemas.user import (
    GoogleCallbackResponse,
    GoogleLoginErrorResponse,
)
from fastapi.responses import RedirectResponse
import core.google_handler
from services.google_auth_service import GoogleAuthService

router = APIRouter(prefix="/auth", tags=["auth"])

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
async def google_callback(code: str, response: Response) -> GoogleCallbackResponse:
    try:
        data = await GoogleAuthService.google_callback(code)  # dict

        #소셜로그인도 쿠키방식으로 받을 경우는 리스폰쿠키 넣어야 함

        response.set_cookie(
            key="access_token",
            value=data["access_token"],
            httponly=True,
            secure=True,
            samesite="none"
        )
        response.set_cookie(
            key="refresh_token",
            value=data["refresh_token"],
            httponly=True,
            secure=True,
            samesite="none"
        )
        return GoogleCallbackResponse(success=True)            # 스키마 변환
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="GOOGLE_TOKEN_INVALID"
        )