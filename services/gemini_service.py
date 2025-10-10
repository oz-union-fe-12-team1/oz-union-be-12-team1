from datetime import datetime

# ==================================================
# 1️⃣ 오늘의 운세 프롬프트
# ==================================================
async def get_fortune_prompt(birthday: str) -> str:
    """Gemini에 전달할 오늘의 운세 프롬프트"""
    return f"""
# 오늘의 전반 운세

- 생년월일: {birthday}
- 항목: 일/학업, 금전, 연애, 건강 포함
- 분량: 300자 이내
- 마지막에 **오늘의 한 줄 조언** 추가

⚠️ 반드시 한국어로만 작성하세요. 영어를 사용하지 마세요.
    """


# ==================================================
# 2️⃣ 일정 & 투두 요약 프롬프트
# ==================================================
async def get_conversation_summary_prompt(schedules: list[str], todos: list[str]) -> str:
    """Gemini에 전달할 일정 및 투두 요약 프롬프트"""

    schedules = [s for s in schedules if s and str(s).strip()]
    todos = [t for t in todos if t and str(t).strip()]

    schedules = [str(s) for s in schedules]
    todos = [str(t) for t in todos]

    schedules = list(dict.fromkeys(schedules))
    todos = list(dict.fromkeys(todos))

    schedule_text = "\n".join(schedules) if schedules else "일정 없음"
    todo_text = "\n".join(todos) if todos else "투두 없음"

    return f"""
# 일정 & 투두 요약

## 오늘 일정
{schedule_text}

## 오늘 투두리스트
{todo_text}

- 실제 일정과 투두의 개수를 정확히 반영하세요.
- 항목이 중복되어도 **하나로 계산하세요.**
- 2~3문장 이내로 자연스럽게 요약하세요.
- 완료/미완료 개수를 명확히 구분하세요.
- 대화하듯 부드럽게 정리하세요.

⚠️ 반드시 한국어로만 작성하세요. 영어를 사용하지 마세요.
    """


# ==================================================
# 3️⃣ 시간대별 브리핑 프롬프트
# ==================================================
async def get_briefing_prompt(period: str) -> str:
    """Gemini에 전달할 시간대별 브리핑 프롬프트"""
    base_notice = "⚠️ 반드시 한국어로 작성하세요. 영어를 사용하지 마세요."

    if period == "아침":
        content = """
# 아침 브리핑

- 오늘 날씨를 간단히 요약
- 오늘 일정을 간단히 정리
- 오늘의 운세 포함
- 전체를 3~4문장으로 작성
- 마지막에 **짧은 조언** 추가
        """

    elif period == "점심":
        content = """
# 점심 브리핑

- 남은 일정을 간단히 요약
- 주요 뉴스나 퀴즈 추천 포함
- 전체를 3~4문장으로 작성
- 마지막에 **짧은 조언** 추가
        """

    else:  # 저녁
        content = """
# 저녁 브리핑

- 오늘 일정 완료율 요약
- 내일 일정을 미리보기 형태로 정리
- 하루를 돌아보는 간단한 정리
- 전체를 3~4문장으로 작성
- 마지막에 **짧은 조언** 추가
        """

    return f"{content}\n\n{base_notice}\n"
