from typing import Any, cast
import httpx
from fastapi import HTTPException
from core.config import settings


async def gemini_request(prompt: str) -> str:
    """Gemini API 호출 담당"""
    if not settings.GEMINI_URL or not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "GEMINI_KEY_ERROR",
                "message": "GEMINI_API_KEY 또는 GEMINI_URL이 설정되지 않았습니다"
            }
        )

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.post(
                settings.GEMINI_URL,
                headers={"Authorization": f"Bearer {settings.GEMINI_API_KEY}"},
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

    #  응답에서 실제 텍스트 추출 (mypy 에러도 해결)
    try:
        text: str = str(data["candidates"][0]["content"]["parts"][0]["text"])
    except (KeyError, IndexError):
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "GEMINI_PARSE_ERROR",
                "message": f"Gemini 응답 파싱 실패: {data}"
            }
        )

    return text
