from fastapi import APIRouter, Query, HTTPException
import httpx
from datetime import datetime

router = APIRouter()
GEMINI_API_KEY = "AIzaSyDi45K31HZwyinwytEV3_GmtCgQwKrh2dk"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"


async def gemini_request(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.post(
            GEMINI_URL,
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)
    data = res.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


@router.get("/fortune")
async def get_fortune(birthday: str = Query(..., description="YYYY-MM-DD")):
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


@router.get("/briefings")
async def get_briefings(type: str = Query("morning", description="morning/evening")):
    prompt = f"""
    당신은 개인 비서입니다.
    사용자의 {type} 브리핑을 작성하세요.
    조건:
    - 300자 이내
    - 아침: 오늘 날씨 + 일정 시작 + 동기부여
    - 저녁: 오늘 일정/투두 회고 + 내일 준비
    - 친근한 한국어, 이모지 포함
    """
    briefing = await gemini_request(prompt)
    return {"success": True, "data": {"type": type, "summary": briefing}}


@router.get("/conversations")
async def get_conversations(message: str = Query(..., description="사용자 요청 메시지")):
    prompt = f"""
    사용자가 요청: "{message}"
    사용자의 일정과 할 일을 요약하는 대화를 작성하세요.
    조건:
    - 간단한 한국어
    - 2~3문장 이내 요약
    - 완료/미완료 개수나 진행 상황 강조
    """
    summary = await gemini_request(prompt)
    return {
        "success": True,
        "data": {"type": "conversation", "summary": summary, "generated_at": datetime.now().isoformat()},
    }
