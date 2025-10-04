from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import core.google_handler
from services.google_auth_service import GoogleAuthService
from core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/google/login")
async def google_login() -> RedirectResponse:
    params = {
        "response_type": "code",
        "client_id": core.google_handler.GOOGLE_CLIENT_ID,
        "redirect_uri": core.google_handler.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
    }
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_callback(code: str, response: Response) -> Response:

    # 구글 로그인 성공 시: 쿠키 저장 후 프론트로 redirect
    try:
        data = await GoogleAuthService.google_callback(code)

        # 쿠키로 저장 (httpOnly)
        response.set_cookie(
            key="access_token",
            value=data["access_token"],
            httponly=True,
            secure=True,
            samesite="none",
        )
        response.set_cookie(
            key="refresh_token",
            value=data["refresh_token"],
            httponly=True,
            secure=True,
            samesite="none",
        )

        # success:true 제거, Redirect 방식으로 응답
        redirect_url = f"{core.google_handler.GOOGLE_FRONTEND_URL}/auth/success"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        # 실패 시 redirect
        error_url = f"{core.google_handler.GOOGLE_FRONTEND_URL}/auth/error?reason=google_auth_failed"
        return RedirectResponse(url=error_url)
