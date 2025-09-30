import os
from typing import Any
from datetime import datetime, date

from fastapi import APIRouter, HTTPException

from models.schedules import Schedule
from models.todo import Todo
from services import gemini_service
from services.gemini_client import gemini_request  # 실제 API 호출 담당

router = APIRouter(prefix="/gemini", tags=["gemini"])


# ==================================================
# 1️ 운세 API
# ==================================================
@router.get("/fortune")
async def get_fortune(birthday: str) -> dict[str, Any]:
    prompt = await gemini_service.get_fortune_prompt(birthday)
    fortune = await gemini_request(prompt)
    return {
        "success": True,
        "data": {
            "type": "fortune",
            "birthday": birthday,
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
        schedules = await Schedule.filter(
            start_time__date=today
        )
        todos = await Todo.filter(
            created_at__date=today
        )

        schedule_list = [f"{s.start_time.strftime('%H:%M')} {s.title}" for s in schedules]
        todo_list = [f"- [{'x' if t.is_completed else ' '}] {t.title}" for t in todos]

        prompt = await gemini_service.get_conversation_summary_prompt(schedule_list, todo_list)
        summary = await gemini_request(prompt)

        return {
            "success": True,
            "data": {
                "summary": [summary],
                "generated_at": datetime.now().isoformat(),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 조회 실패: {e}")


# ==================================================
# 3️ 아침/점심/저녁 브리핑 API
# ==================================================
@router.get("/briefings")
async def get_briefings(period: str = "아침") -> dict[str, Any]:
    """아침/점심/저녁 브리핑"""
    prompt = await gemini_service.get_briefing_prompt(period)
    briefing = await gemini_request(prompt)
    return {
        "success": True,
        "data": {
            "type": "briefing",
            "period": period,
            "briefing": briefing,
            "generated_at": datetime.now().isoformat(),
        },
    }
