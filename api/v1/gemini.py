import os
from fastapi import APIRouter, Query, HTTPException
import httpx
from datetime import datetime

router = APIRouter()

# ===== Gemini API 설정 =====
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"


async def gemini_request(prompt: str) -> str:
    """Gemini API 요청 함수"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.post(
                GEMINI_URL,
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
        res.raise_for_status()
        data = res.json()

        if "candidates" not in data or not data["candidates"]:
            raise HTTPException(status_code=500, detail="Gemini API 응답 없음")

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Gemini API 요청 시간 초과")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"API 요청 오류: {str(e)}")


# ======================
# 운세 API
# ======================
@router.get("/fortune")
async def get_fortune(birthday: str = Query(..., description="YYYY-MM-DD 형식")):
    """사용자 생년월일 기반 운세 제공"""
    try:
        datetime.strptime(birthday, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="생년월일은 YYYY-MM-DD 형식이어야 합니다")

    prompt = f"""
    당신은 전문 운세가입니다.
    생년월일 {birthday} 사용자의 오늘 운세를 작성하세요.
    조건:
    - 300자 이내
    - 긍정적이고 희망적인 메시지
    - 일/학업, 금전, 연애, 건강 중 최소 2가지 언급
    - 마지막에 ✨오늘의 한 줄 조언✨ 포함
    """

    fortune = await gemini_request(prompt)
    return {
        "success": True,
        "data": {
            "birthday": birthday,
            "fortune": fortune,
            "created_at": datetime.now().isoformat(),
        },
    }


# ======================
# 브리핑 API (아침/저녁/하루)
# ======================
@router.post("/briefings")
async def get_briefings(
    type: str = Query("morning", description="morning / evening / daily"),
    schedules: list[str] = None,
    todos: list[str] = None,
    weather: str = None,
):
    """아침/저녁/하루 브리핑 제공"""
    if type not in ["morning", "evening", "daily"]:
        raise HTTPException(status_code=400, detail="type은 'morning' | 'evening' | 'daily' 중 하나여야 합니다")

    schedules_text = "\n".join(schedules) if schedules else "오늘은 일정이 없습니다."
    todos_text = "\n".join(todos) if todos else "오늘은 할 일이 없습니다."
    weather_text = weather or "날씨 정보 없음"

    if type == "morning":
        prompt = f"""
        🌅 아침 브리핑을 작성하세요.
        조건:
        - 날씨: {weather_text}
        - 오늘 일정: {schedules_text}
        - 투두리스트: {todos_text}
        - 300자 이내, 친근한 한국어, 이모지 포함, 동기부여 멘트 추가
        """
    elif type == "evening":
        prompt = f"""
        🌙 저녁 브리핑을 작성하세요.
        조건:
        - 오늘 진행된 일정: {schedules_text}
        - 오늘 투두리스트 결과: {todos_text}
        - 내일 준비 멘트 포함
        - 300자 이내, 친근한 한국어, 이모지 포함
        """
    else:  # daily
        prompt = f"""
        하루 요약 브리핑을 작성하세요.
        조건:
        - 오늘 일정 결과: {schedules_text}
        - 오늘 투두리스트 결과: {todos_text}
        - 내일 일정/날씨: {weather_text}
        - 300자 이내, 친근한 한국어, 이모지 포함
        """

    briefing = await gemini_request(prompt)
    return {
        "success": True,
        "data": {
            "type": type,
            "summary": briefing,
            "created_at": datetime.now().isoformat(),
        },
    }


# ======================
# 대화 요약 API
# ======================
@router.get("/conversations")
async def get_conversations(message: str = Query(..., description="사용자 요청 메시지")):
    """사용자 메시지 기반 대화형 응답"""
    if not message.strip():
        raise HTTPException(status_code=400, detail="메시지가 비어있습니다")
    if len(message) > 500:
        raise HTTPException(status_code=400, detail="메시지는 500자 이내여야 합니다")

    prompt = f"""
    사용자가 요청: "{message}"
    일정/투두 상황을 요약하는 대화를 작성하세요.
    조건:
    - 간단한 한국어
    - 2~3문장 이내
    - 완료/미완료 개수나 진행 상황 강조
    - 친근한 톤
    """

    summary = await gemini_request(prompt)
    return {
        "success": True,
        "data": {
            "type": "conversation",
            "summary": summary,
            "generated_at": datetime.now().isoformat(),
        },
    }
