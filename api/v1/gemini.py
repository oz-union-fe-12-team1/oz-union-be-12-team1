import os, httpx
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, date, timedelta
from tortoise.expressions import Q
from models.schedules import Schedule
from models.todo import Todo

router = APIRouter(prefix="/gemini", tags=["gemini"])

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    if GEMINI_API_KEY
    else None
)

async def gemini_request(prompt: str) -> str:
    """Gemini API 호출"""
    if not GEMINI_URL:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY가 설정되지 않았습니다")

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.post(
                GEMINI_URL,
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Gemini API 요청 실패: {e}")

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    try:
        data = res.json()
        return (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Gemini API 응답 파싱 실패")

# ✅ 운세 API
@router.get("/fortune")
async def get_fortune(birthday: str = Query(..., description="YYYY-MM-DD")):
    prompt = f"""
    🌅 오늘의 전반 운세
    생년월일 {birthday} 기준으로 작성하세요.
    - 일/학업, 금전, 연애, 건강 포함
    - 300자 이내
    - 마지막에 ✨오늘의 한 줄 조언✨ 추가
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

#  아침/저녁 브리핑 (자동 판별 추가)
@router.get("/briefings")
async def get_briefings(
    type: str = Query(None, description="morning/evening (없으면 자동 판별)")
):
    now = datetime.now().hour

    # 자동 판별: 06~17시는 morning, 18~05시는 evening
    if not type:
        if 6 <= now < 18:
            type = "morning"
        else:
            type = "evening"

    today = date.today()
    tomorrow = today + timedelta(days=1)

    try:
        # 날짜 범위 설정
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
        tomorrow_end = datetime.combine(tomorrow, datetime.max.time())
        
        # DB 조회
        schedules = await Schedule.filter(
            start_time__gte=today_start,
            start_time__lte=today_end
        )
        todos = await Todo.filter(
            created_at__gte=today_start,
            created_at__lte=today_end
        )
        tomorrow_schedules = await Schedule.filter(
            start_time__gte=tomorrow_start,
            start_time__lte=tomorrow_end
        )
        
    except Exception as e:
        print(f"DB Query Error: {e}")
        schedules, todos, tomorrow_schedules = [], [], []

    schedule_text = "\n".join([f"{s.start_time.strftime('%H:%M')} {s.title}" for s in schedules]) or "일정 없음"
    todo_text = "\n".join([f"{'✔' if t.is_completed else '☐'} {t.title}" for t in todos]) or "투두 없음"
    tomorrow_text = "\n".join([f"{s.start_time.strftime('%H:%M')} {s.title}" for s in tomorrow_schedules]) or "내일 일정 없음"

    if type == "morning":
        prompt = f"""
        🌅 아침 브리핑
        오늘 일정:
        {schedule_text}

        오늘 투두리스트:
        {todo_text}

        👉 오늘 목표는 "작은 습관 지키기"! 힘내서 출발해볼까요? 🚀
        """
    else:
        prompt = f"""
        🌙 저녁 브리핑
        오늘 일정:
        {schedule_text}

        오늘 투두리스트:
        {todo_text}

        내일 일정 미리보기:
        {tomorrow_text}

        오늘도 수고 많으셨어요. 내일은 더 가볍게 시작해 보죠 ✨
        """

    briefing = await gemini_request(prompt)
    return {
        "success": True,
        "data": {
            "type": type,
            "summary": briefing,
            "schedules": schedule_text,
            "todos": todo_text,
        },
        "generated_at": datetime.now().isoformat(),
    }

#  대화 요약
@router.get("/conversations")
async def get_conversations(message: str = Query(..., description="사용자 요청 메시지")):
    prompt = f"""
    사용자가 요청: "{message}"
    사용자의 일정과 할 일을 요약하는 대화를 작성하세요.
    - 2~3문장 이내
    - 완료/미완료 개수 강조
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
