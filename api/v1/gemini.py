#  아침/저녁 브리핑 (자동 판별 + 추천 활동)
@router.get("/briefings")
async def get_briefings(
    type: str = Query(None, description="morning/evening (없으면 자동 판별)")
):
    now = datetime.now().hour

    # 자동 판별: 06~17시는 morning, 18~05시는 evening
    if not type:
        type = "morning" if 6 <= now < 18 else "evening"

    today = date.today()
    tomorrow = today + timedelta(days=1)

    try:
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
        tomorrow_end = datetime.combine(tomorrow, datetime.max.time())

        schedules = await Schedule.filter(
            start_time__gte=today_start, start_time__lte=today_end
        )
        todos = await Todo.filter(
            created_at__gte=today_start, created_at__lte=today_end
        )
        tomorrow_schedules = await Schedule.filter(
            start_time__gte=tomorrow_start, start_time__lte=tomorrow_end
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

        👉 오늘 목표는 "작은 습관 지키기"! 🚀

        추가로, 아래 형식의 JSON 배열로 오늘 추천 활동 3~5개를 작성해줘:
        [
        {{"category": "🧘 건강 & 생활 습관", "item": "물 2컵 마시기"}},
        {{"category": "📚 학습 & 자기계발", "item": "책 10분 읽기"}}
        ]
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

        오늘도 수고 많으셨어요 ✨

        추가로, 아래 형식의 JSON 배열로 저녁 추천 활동 3~5개를 작성해줘:
        [
        {{"category": "💌 관계 & 감정 관리", "item": "오늘 기분 한 줄 기록하기"}},
        {{"category": "🛌 휴식", "item": "명상 5분 하기"}}
        ]
        """

    briefing_text = await gemini_request(prompt)

    # JSON 파싱 시도
    import json
    recommendations = []
    try:
        recommendations = json.loads(briefing_text)
        summary = None
    except Exception:
        summary = briefing_text

    return {
        "success": True,
        "data": {
            "type": type,
            "summary": summary,
            "schedules": schedule_text,
            "todos": todo_text,
            "recommendations": recommendations,
        },
        "generated_at": datetime.now().isoformat(),
    }
