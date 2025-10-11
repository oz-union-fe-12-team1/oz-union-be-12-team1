from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import core.google_handler
from repositories.user_repo import UserRepository
from services.google_auth_service import GoogleAuthService
from models import user
from core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/google/login")
async def google_login() -> RedirectResponse:
    params = {
        "response_type": "code",
        "client_id": core.google_handler.GOOGLE_CLIENT_ID,
        "redirect_uri": core.google_handler.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return RedirectResponse(url=google_auth_url)

# used_code : 계속 중복 호출로 인한 코드 중복 사용으로 문제가 발생했음, 해당 부분으로 중복 호출 시 이미 사용된 코드는 무시하게 처리함
@router.get("/google/callback")
async def google_callback(code: str) -> Response:
    # ✅ 동일한 code 재사용 방지
    if not hasattr(GoogleAuthService, "_used_codes"):  # type: ignore[attr-defined]
        GoogleAuthService._used_codes = set()  # type: ignore[attr-defined]

    if code in GoogleAuthService._used_codes:  # type: ignore[attr-defined]
        print(f"⚠️ 이미 사용된 code: {code[:20]}... 중복 요청 무시")
        error_url = (
            f"{core.google_handler.GOOGLE_FRONTEND_URL}"
            f"/auth/error?reason=duplicate_code"
        )
        return RedirectResponse(url=error_url, status_code=302)

    GoogleAuthService._used_codes.add(code)  # type: ignore[attr-defined]

    try:
        # ✅ 구글 로그인 처리
        data = await GoogleAuthService.google_callback(code)

        KST = timezone(timedelta(hours=9))

        # ✅ 구글 로그인 성공한 사용자 정보 가져오기
        email = data.get("email")  # google_callback()이 email 반환해야 함
        if email:
            user = await UserRepository.get_user_by_email(email)
            if user:
                user.last_login_at = datetime.now(timezone.utc)
                await user.save(update_fields=["last_login_at"])

                kst_time = user.last_login_at.astimezone(KST).strftime("%Y-%m-%d %H:%M")
                print(f"🕒 last_login_at 갱신 완료 (KST): {kst_time}")

        # ✅ 프론트엔드로 리디렉트 (경로 유지)
        redirect_url = f"{core.google_handler.GOOGLE_FRONTEND_URL}/auth/google/callback"
        response = RedirectResponse(url=redirect_url, status_code=302)

        # ✅ 쿠키 세팅 (HTTPS 환경 대응)
        response.set_cookie(
            key="access_token",
            value=data["access_token"],
            httponly=True,
            secure=True,
            samesite="none",
            domain=".nyangbiseo.store",
            path="/",
        )
        response.set_cookie(
            key="refresh_token",
            value=data["refresh_token"],
            httponly=True,
            secure=True,
            samesite="none",
            domain=".nyangbiseo.store",
            path="/",
        )

        print("✅ Google 로그인 완료, 프론트로 리디렉트:", redirect_url)
        return response

    except Exception as e:
        print(f"❌ Google OAuth Error: {e}")
        error_url = (
            f"{core.google_handler.GOOGLE_FRONTEND_URL}"
            f"/auth/error?reason=google_auth_failed"
        )
        return RedirectResponse(url=error_url, status_code=302)