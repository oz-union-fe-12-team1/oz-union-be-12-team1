import os
from typing import Any
from datetime import datetime, date

from fastapi import APIRouter, HTTPException, Depends
from models.schedules import Schedule
from models.todo import Todo
from services import gemini_service
from services.gemini_client import gemini_request
from models.users import User
from api.dependencies import get_current_user

router = APIRouter(prefix="/gemini", tags=["gemini"])


# ==================================================
# 1️ 운세 API
# ==================================================
@router.get("/fortune")
async def get_fortune(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """오늘의 운세 (유저 DB의 birthday 사용)"""
    if not current_user.birthday:
        raise HTTPException(status_code=400, detail="생년월일 정보가 없습니다.")

    prompt = await gemini_service.get_fortune_prompt(str(current_user.birthday))
    fortune: str = await gemini_request(prompt)

    return {
        "success": True,
        "data": {
            "type": "fortune",
            "birthday": str(current_user.birthday),
            "fortune": fortune,
            "created_at": datetime.now().isoformat(),
        },
    }


# ==================================================
# 2️ 대화 요약 API
# ==================================================
@router.get("/conversations")
async def get_conversations() -> dict[str, Any]:
    """오늘 일정과 투두를 요약"""
    try:
        today = date.today()
        schedules = await Schedule.filter(start_time__date=today)
        todos = await Todo.filter(created_at__date=today)

        schedule_list = [f"{s.start_time.strftime('%H:%M')} {s.title}" for s in schedules]
        todo_list = [f"- [{'x' if t.is_completed else ' '}] {t.title}" for t in todos]

        prompt = await gemini_service.get_conversation_summary_prompt(schedule_list, todo_list)
        summary: str = await gemini_request(prompt)

        return {
            "success": True,
            "data": {
                "summary": summary,  # 문자열 그대로 반환
                "generated_at": datetime.now().isoformat(),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 조회 실패: {e}")


# ==================================================
# 3️ 아침/점심/저녁 브리핑 API
# ==================================================
@router.get("/briefings")
async def get_briefings() -> dict[str, Any]:
    """시간대 자동 분기 아침/점심/저녁 브리핑"""
    now = datetime.now().hour
    if 6 <= now < 12:
        period = "아침"
    elif 12 <= now < 18:
        period = "점심"
    else:
        period = "저녁"

    prompt = await gemini_service.get_briefing_prompt(period)
    briefing: str = await gemini_request(prompt)

    return {
        "success": True,
        "data": {
            "type": "briefing",
            "period": period,
            "briefing": briefing,
            "generated_at": datetime.now().isoformat(),
        },
    }
