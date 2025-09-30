import httpx
from datetime import date

from core.config import settings
from repositories.user_repo import UserRepository
from .auth_service import AuthService

# ---------------------------
# 구글 로그인 (/auth/google/callback)
# ---------------------------
class GoogleAuthService(AuthService):

    @staticmethod
    async def google_callback(code: str) -> dict[str, str]:
        print(f"=== AuthService.google_callback 시작: code={code[:30]}...")  # ⭕
        try:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            print("Google token request data:", data)

            print(">>> httpx.AsyncClient 생성 중...")  # ⭕
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(">>> POST 요청 시작...")  # ⭕
                resp = await client.post(token_url, data=data)
                print(f">>> 응답 받음! status_code={resp.status_code}")  # ⭕
                print("Google token raw response:", resp.text)

                token_data = resp.json()
                if "error" in token_data:
                    print(f">>> 구글 토큰 오류: {token_data}")  # ⭕
                    raise Exception(f"Google token error: {token_data}")

                access_token = token_data["access_token"]
                print(f">>> access_token 획득 성공: {access_token[:20]}...")  # ⭕

                # (2) userinfo 가져오기
                userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
                headers = {"Authorization": f"Bearer {access_token}"}
                print(">>> userinfo 요청 중...")  # ⭕
                user_response = await client.get(userinfo_url, headers=headers)
                print(f">>> userinfo 응답: status={user_response.status_code}")  # ⭕

                if user_response.status_code != 200:
                    raise Exception(f"userinfo error: {user_response.text}")

                info = user_response.json()
                print("Google userinfo response:", info)

                name = info.get("name")
                email = info.get("email")
                google_id = info.get("sub")

            print(">>> DB 작업 시작...")  # ⭕
            # (3) DB 조회 또는 신규 생성
            user = await UserRepository.get_user_by_email(email)
            if not user:
                print(f">>> 신규 사용자 생성: {email}")  # ⭕
                user = await UserRepository.create_user(
                    email=email,
                    password_hash="",
                    username=name or "구글사용자",
                    birthday=date(2000, 1, 1),
                )
                user.google_id = google_id
                user.is_email_verified = True
                await user.save()

            print(">>> JWT 발급 중...")  # ⭕
            # (4) JWT 발급
            access_token = AuthService.create_access_token(user.id)
            refresh_token = AuthService.create_refresh_token(user.id)

            result = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
            print(f">>> 완료! 반환값: {result.keys()}")  # ⭕
            return result

        except httpx.TimeoutException as e:
            print(f"❌ 타임아웃: {e}")
            raise Exception(f"Google API timeout: {e}")
        except httpx.RequestError as e:
            print(f"❌ 네트워크 오류: {e}")
            raise Exception(f"Network error: {e}")
        except Exception as e:
            print(f"❌ Google OAuth error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise