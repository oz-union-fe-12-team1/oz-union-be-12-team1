from typing import Any, cast
import httpx
from fastapi import HTTPException
from core.config import settings


async def gemini_request(prompt: str) -> dict[str, Any]:
    """Gemini API 호출 담당"""
    if not settings.GEMINI_URL:
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

    # 🔑 여기서 타입을 dict[str, Any]로 명시
    data: dict[str, Any] = cast(dict[str, Any], res.json())
    return data
