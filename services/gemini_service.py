from datetime import datetime, date, timedelta, timezone
from typing import Optional, List


# ==================================================
# 🧭 브리핑 기준 날짜 계산
# ==================================================
def get_briefing_date() -> date:
    """
    자정~05시 사이는 전날 날짜를 반환,
    그 외 시간은 오늘 날짜를 반환.
    """
    KST = timezone(timedelta(hours=9))
    now = datetime.now(KST)
    if 0 <= now.hour < 5:
        target_date = now - timedelta(days=1)
    else:
        target_date = now
    return target_date.date()


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

    schedules = list(dict.fromkeys(map(str, schedules)))
    todos = list(dict.fromkeys(map(str, todos)))

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
async def get_briefing_prompt(
    period: str,
    schedules: Optional[List[str]] = None,
    todos: Optional[List[str]] = None,
    target_date: Optional[date] = None,
) -> str:
    target_date = target_date or get_briefing_date()

    schedules = [s for s in (schedules or []) if str(s).strip()]
    todos = [t for t in (todos or []) if str(t).strip()]

    schedule_text = "\n".join(schedules) if schedules else "없음"
    todo_text = "\n".join(todos) if todos else "없음"

    # ✅ 날짜 포맷 지정
    today_str = target_date.strftime("%m월 %d일")
    tomorrow_str = (target_date + timedelta(days=1)).strftime("%m월 %d일")

    base_notice = "⚠️ 반드시 한국어로만 작성하세요. 영어 사용 금지."

    if period == "아침":
        content = f"""
# 아침 브리핑

- {today_str}의 날씨를 간단히 요약
- {today_str} 주요 일정 ({schedule_text}) 정리
- 오늘 할 일 목록 ({todo_text}) 기반으로 동기부여 문장 작성
- 운세를 한 문장으로 포함
- 전체 3~4문장, 마지막에 **짧은 조언** 추가
        """

    elif period == "점심":
        content = f"""
# 점심 브리핑

- 오전에 완료된 {today_str} 일정 또는 진행 중인 작업 요약
- 남은 {today_str} 일정 ({schedule_text}) 과 할 일 ({todo_text}) 간단히 정리
- 주요 뉴스나 흥미 요소 포함
- 전체 3~4문장, 마지막에 **짧은 조언** 추가
        """

    else:  # 저녁
        content = f"""
# 저녁 브리핑

- {today_str} 일정 완료율을 요약
- {today_str} 일정이 없으면 '{today_str} 일정 없음'으로만 작성
- {tomorrow_str} 일정을 미리보기 형태로 정리
- 하루를 돌아보는 간단한 정리
- 전체를 3~4문장으로 작성
- 마지막에 **짧은 조언** 추가
- {tomorrow_str} 일정이 없을 경우 '{tomorrow_str} 일정 없음'이라고만 작성
- 허구의 내용은 절대 생성하지 마세요.
        """

    return f"{content}\n\n{base_notice}\n"