import os, httpx
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, date, timedelta
from models.schedules import Schedule
from models.todo import Todo

router = APIRouter(prefix="/gemini", tags=["gemini"])

# ================= Gemini API 설정 =================
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

# ==================================================
# 1️⃣ 운세 API
# ==================================================
@router.get("/fortune")
async def get_fortune(birthday: str = Query(..., description="YYYY-MM-DD")):
    prompt = f"""
    🌅 오늘의 전반 운세
    생년월일 {birthday} 기준으로 작성하세요.
    - 일/학업, 금전, 연애, 건강 포함
    - 300자 이내
    - 마지막에 ✨오늘의 한 줄 조언✨ 추가
    반드시 한국어로만 작성하세요. 영어를 사용하지 마세요.
    """
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
async def get_conversations(message: str = Query(..., description="사용자 요청 메시지")):
    prompt = f"""
    사용자가 요청: "{message}"
    사용자의 일정과 할 일을 요약하는 대화를 작성하세요.
    - 2~3문장 이내
    - 완료/미완료 개수 강조
    반드시 한국어로만 작성하세요. 영어를 사용하지 마세요.
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

# ==================================================
# 3️⃣ 아침/점심/저녁 브리핑 (자동 판별 + 어제 미완료 이월 + 중복 방지)
# ==================================================
@router.get("/briefings")
async def get_briefings():
    now = datetime.now().hour

    # 자동 판별: 06~14 = morning, 14~22 = afternoon, 22~06 = evening
    if 6 <= now < 14:
        type = "morning"
    elif 14 <= now < 22:
        type = "afternoon"
    else:
        type = "evening"

    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    try:
        # 날짜 범위
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        yesterday_start = datetime.combine(yesterday, datetime.min.time())
        yesterday_end = datetime.combine(yesterday, datetime.max.time())
        tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
        tomorrow_end = datetime.combine(tomorrow, datetime.max.time())

        #  어제 일정/투두 (rolled_over=False 조건)
        yesterday_schedules = await Schedule.filter(
            start_time__gte=yesterday_start, start_time__lte=yesterday_end, rolled_over=False
        )
        yesterday_todos = await Todo.filter(
            created_at__gte=yesterday_start, created_at__lte=yesterday_end, rolled_over=False
        )

        #  미완료 항목 오늘로 이월
        for s in yesterday_schedules:
            if not getattr(s, "is_completed", False):
                await Schedule.create(
                    title=f"[이월] {s.title}",
                    start_time=datetime.combine(today, s.start_time.time()),
                    rolled_over=False  # 새 항목은 다시 이월 가능
                )
                s.rolled_over = True
                await s.save()

        for t in yesterday_todos:
            if not t.is_completed:
                await Todo.create(
                    title=f"[이월] {t.title}",
                    is_completed=False,
                    rolled_over=False
                )
                t.rolled_over = True
                await t.save()

        #  오늘/내일 일정 조회
        schedules = await Schedule.filter(
            start_time__gte=today_start, start_time__lte=today_end
        )
        todos = await Todo.filter(
            created_at__gte=today_start, created_at__lte=today_end
        )
        tomorrow_schedules = await Schedule.filter(
            start_time__gte=tomorrow_start, start_time__lte=tomorrow_end
        )

        schedule_text = "\n".join(
            [f"{s.start_time.strftime('%H:%M')} {s.title}" for s in schedules]
        ) or "일정 없음"

        todo_text = "\n".join(
            [f"{'✔' if t.is_completed else '☐'} {t.title}" for t in todos]
        ) or "투두 없음"

        tomorrow_text = "\n".join(
            [f"{s.start_time.strftime('%H:%M')} {s.title}" for s in tomorrow_schedules]
        ) or "내일 일정 없음"

    except Exception as e:
        print(f"DB Query Error: {e}")
        schedule_text, todo_text, tomorrow_text = "일정 없음", "투두 없음", "내일 일정 없음"

    # 프롬프트 구분
    if type == "morning":
        prompt = f"""
        🌅 아침 브리핑
        오늘 일정:
        {schedule_text}

        오늘 투두리스트:
        {todo_text}

        👉 어제 완료하지 못한 일정과 투두는 오늘로 이월했습니다.
        오늘 목표는 "작은 습관 지키기"! 힘내서 출발해볼까요? 🚀
        반드시 한국어로만 작성하세요. 영어를 사용하지 마세요.
        """
    elif type == "afternoon":
        prompt = f"""
        🌞 점심 브리핑
        지금까지 진행된 일정:
        {schedule_text}

        남은 투두리스트:
        {todo_text}

        👉 어제 완료하지 못한 일정과 투두는 오늘로 이월했습니다.
        오후에도 힘내세요 💪
        반드시 한국어로만 작성하세요. 영어를 사용하지 마세요.
        """
    else:  # evening
        prompt = f"""
        🌙 저녁 브리핑
        오늘 일정 요약:
        {schedule_text}

        오늘 투두리스트 요약:
        {todo_text}

        내일 일정 미리보기:
        {tomorrow_text}

        👉 오늘 완료하지 못한 일정과 투두는 내일로 이월됩니다.
        내일은 비가 내릴 수 있어요. 기온은 최저 20도, 최고 26도이니 외출 준비에 참고하세요.
        오늘도 고생 많으셨어요. 내일 다시 힘차게 출발합시다 🌞
        반드시 한국어로만 작성하세요. 영어를 사용하지 마세요.
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