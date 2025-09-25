import os
import httpx
from fastapi import HTTPException

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_SECRET")
GOOGLE_CALLBACK_URI = os.getenv("GOOGLE_CALLBACK_URI", "http://localhost:8000/auth/google/callback")


async def auth_google(code: str) -> dict[str, str]:
    """
    원래는 request 방식으로 하려고 했으나 조금 더 비동기, fastAPI에 더 친화적이고 현대적인 httpx 변경
    """
    #토큰 요청 클라이언트 아이디, 시크릿키를 이용해 보내기
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_url,
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": GOOGLE_CALLBACK_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="GOOGLE_TOKEN_REQUEST_FAILED")

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="GOOGLE_ACCESS_TOKEN_NOT_FOUND")
        # 구글 토근 이용하여 사용자 정보 가져오기 / 대신 생년월일 같은 경우는 추후 마이페이지에서 설정하게 하기
        user_response = await client.get(
            userinfo_url,
            params={"access_token": access_token},
        )

        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="GOOGLE_USERINFO_REQUEST_FAILED")

        user_info = user_response.json()

    return {
        "google_id": user_info.get("id"),
        "email": user_info.get("email"),
        "username": user_info.get("name"),
    }
