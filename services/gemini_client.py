from typing import Any, cast
import httpx
from fastapi import HTTPException
from core.config import settings


async def gemini_request(prompt: str) -> str:
    """Gemini API 호출 담당"""
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "GEMINI_KEY_ERROR",
                "message": "GEMINI_API_KEY가 설정되지 않았습니다"
            }
        )

    GEMINI_URL = (
        "https://generativelanguage.googleapis.com/v1/models/"
        f"gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    )

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.post(
                GEMINI_URL,
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "GEMINI_REQUEST_ERROR",
                "message": f"Gemini API 요청 실패: {e}"
            }
        )

    if res.status_code != 200:
        raise HTTPException(
            status_code=res.status_code,
            detail={
                "error_code": "GEMINI_RESPONSE_ERROR",
                "message": f"Gemini API 응답 실패: {res.text}"
            }
        )

    data: dict[str, Any] = cast(dict[str, Any], res.json())

    try:
        text: str = str(data["candidates"][0]["content"]["parts"][0]["text"])
        return text
    except (KeyError, IndexError):
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "GEMINI_PARSE_ERROR",
                "message": f"Gemini 응답 파싱 실패: {data}"
            }
        )

    return ""
