from datetime import datetime, date, timedelta, timezone
from typing import Any
from fastapi import APIRouter, HTTPException, Depends

from models.schedules import Schedule
from models.todo import Todo
from models.user import User
from services import gemini_service
from services.gemini_client import gemini_request
from core.security import get_current_user

router = APIRouter(prefix="/gemini", tags=["Gemini"])

# ✅ 한국 표준시 (KST)
KST = timezone(timedelta(hours=9))


# ==================================================
# 1️⃣ 오늘의 운세 API
# ==================================================
@router.get("/fortune")
async def get_fortune(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Gemini 기반 오늘의 운세 조회"""
    if not current_user.birthday:
        raise HTTPException(status_code=400, detail="생년월일 정보가 없습니다.")

    try:
        prompt = await gemini_service.get_fortune_prompt(str(current_user.birthday))
        fortune = await gemini_request(prompt)

        return {
            "success": True,
            "data": {
                "type": "fortune",
                "birthday": str(current_user.birthday),
                "fortune": fortune,
                "generated_at": datetime.now(KST).isoformat(),
            },
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"운세 생성 실패: {e}")


# ==================================================
# 2️⃣ 일정 & 투두 요약 API
# ==================================================
@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Gemini 기반 오늘의 일정 & 투두 요약"""
    try:
        now_kst = datetime.now(KST)
        today = now_kst.date()

        # ✅ KST 하루 범위 계산
        start_of_day_kst = datetime.combine(today, datetime.min.time(), tzinfo=KST)
        end_of_day_kst = datetime.combine(today, datetime.max.time(), tzinfo=KST)

        # ✅ UTC 변환 (DB 저장 기준)
        start_of_day_utc = start_of_day_kst.astimezone(timezone.utc)
        end_of_day_utc = end_of_day_kst.astimezone(timezone.utc)

        # ✅ 일정 & 투두 조회
        schedules = await Schedule.filter(
            user=current_user,
            start_time__gte=start_of_day_utc,
            start_time__lte=end_of_day_utc,
        ).all()

        todos = await Todo.filter(
            user=current_user,
            created_at__gte=start_of_day_utc,
            created_at__lte=end_of_day_utc,
        ).all()

        schedule_list = [
            f"{s.start_time.astimezone(KST).strftime('%H:%M')} {s.title}"
            for s in schedules
        ] or ["일정 없음"]

        todo_list = [
            f"- [{'x' if t.is_completed else ' '}] {t.title}" for t in todos
        ] or ["투두 없음"]

        # ✅ Gemini 요약 프롬프트 생성
        prompt = await gemini_service.get_conversation_summary_prompt(
            schedule_list, todo_list
        )
        summary = await gemini_request(prompt)

        return {
            "success": True,
            "data": {
                "type": "conversation_summary",
                "summary": summary,
                "generated_at": datetime.now(KST).isoformat(),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대화 요약 실패: {e}")


# ==================================================
# 3️⃣ 아침/점심/저녁 브리핑 API
# ==================================================
@router.get("/briefings")
async def get_briefings(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Gemini 기반 시간대별 브리핑"""
    try:
        now_kst = datetime.now(KST)
        hour = now_kst.hour

        # ✅ 시간대 분기
        if 6 <= hour < 12:
            period = "아침"
        elif 12 <= hour < 18:
            period = "점심"
        else:
            period = "저녁"

        # ✅ 브리핑 기준 날짜 (자정~05시는 전날)
        target_date = gemini_service.get_briefing_date()

        # ✅ KST 하루 범위 계산 (target_date 기준)
        start_of_day_kst = datetime.combine(target_date, datetime.min.time(), tzinfo=KST)
        end_of_day_kst = datetime.combine(target_date, datetime.max.time(), tzinfo=KST)

        # ✅ UTC로 변환
        start_of_day_utc = start_of_day_kst.astimezone(timezone.utc)
        end_of_day_utc = end_of_day_kst.astimezone(timezone.utc)

        # ✅ 오늘 일정 / 투두
        schedules = await Schedule.filter(
            user=current_user,
            start_time__gte=start_of_day_utc,
            start_time__lte=end_of_day_utc,
        ).all()

        todos = await Todo.filter(
            user=current_user,
            created_at__gte=start_of_day_utc,
            created_at__lte=end_of_day_utc,
        ).all()

        schedule_list = [
            f"{s.start_time.astimezone(KST).strftime('%H:%M')} {s.title}"
            for s in schedules
        ] or ["일정 없음"]

        todo_list = [
            f"- [{'x' if t.is_completed else ' '}] {t.title}" for t in todos
        ] or ["투두 없음"]

        # ✅ 저녁일 경우: 내일 일정도 함께 조회
        next_day_schedules = []
        if period == "저녁":
            next_date = target_date + timedelta(days=1)
            next_start_kst = datetime.combine(next_date, datetime.min.time(), tzinfo=KST)
            next_end_kst = datetime.combine(next_date, datetime.max.time(), tzinfo=KST)
            next_start_utc = next_start_kst.astimezone(timezone.utc)
            next_end_utc = next_end_kst.astimezone(timezone.utc)

            next_schedules = await Schedule.filter(
                user=current_user,
                start_time__gte=next_start_utc,
                start_time__lte=next_end_utc,
            ).all()

            next_day_schedules = [
                f"{s.start_time.astimezone(KST).strftime('%H:%M')} {s.title}"
                for s in next_schedules
            ] or ["내일 일정 없음"]

        # ✅ Gemini 프롬프트 생성
        prompt = await gemini_service.get_briefing_prompt(
            period=period,
            schedules=schedule_list,
            todos=todo_list,
            target_date=target_date,
        )

        # ✅ 저녁 프롬프트에는 내일 일정도 포함
        if period == "저녁":
            next_text = "\n".join(next_day_schedules)
            prompt += f"\n\n# 내일 일정 미리보기\n{next_text}\n"

        # ✅ Gemini 호출
        briefing = await gemini_request(prompt)

        return {
            "success": True,
            "data": {
                "type": "briefing",
                "period": period,
                "date": str(target_date),
                "briefing": briefing,
                "generated_at": datetime.now(KST).isoformat(),
            },
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"브리핑 생성 실패: {e}")
