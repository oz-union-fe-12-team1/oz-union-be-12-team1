from datetime import datetime


async def get_fortune_prompt(birthday: str) -> str:
    return f"""
# 오늘의 전반 운세

- 생년월일: {birthday}
- 항목: 일/학업, 금전, 연애, 건강 포함
- 분량: 300자 이내
- 마지막에 **오늘의 한 줄 조언** 추가

⚠️ 반드시 한국어로만 작성하세요. 영어를 사용하지 마세요.
    """


async def get_conversation_summary_prompt(schedules: list, todos: list) -> str:
    schedule_text = "\n".join(schedules) or "일정 없음"
    todo_text = "\n".join(todos) or "투두 없음"

    return f"""
# 일정 & 투두 요약

## 오늘 일정
{schedule_text}

## 오늘 투두리스트
{todo_text}

- 2~3문장 이내 요약
- 완료/미완료 개수 강조
- 간단히 대화하듯 정리

⚠️ 반드시 한국어로만 작성하세요. 영어를 사용하지 마세요.
    """


async def get_briefing_prompt(period: str) -> str:
    return f"""
# {period} 브리핑

- 오늘 뉴스/할 일/날씨를 요약해서 3~4문장으로 정리
- 마지막에 짧은 조언 추가
- 반드시 한국어로 작성
    """
