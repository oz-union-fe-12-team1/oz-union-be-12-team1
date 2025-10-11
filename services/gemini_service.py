from datetime import datetime, date
import httpx
from typing import Any, Optional, List
from core.config import settings


# ==================================================
# 🌐 Gemini Client
# ==================================================
class GeminiClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    MODEL = "gemini-1.5-flash-latest"

    async def generate_text(self, prompt: str) -> str:
        """
        Gemini API를 호출하여 텍스트 생성
        """
        url = f"{self.BASE_URL}/{self.MODEL}:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    params={"key": settings.GEMINI_API_KEY},
                )
                response.raise_for_status()
                data: dict[str, Any] = response.json()
                text: str = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
        except Exception as e:
            # 예외 발생 시 문자열을 반환하도록 보장 (Any → str)
            return f"Gemini API 호출 실패: {e}"


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
    """
        period (str): '아침', '점심', '저녁'
        schedules (list[str] | None): 일정 목록
        todos (list[str] | None): 할 일 목록
        target_date (date | None): 기준 날짜 (예: 오늘 날짜)
    """

    schedules = [s for s in (schedules or []) if str(s).strip()]
    todos = [t for t in (todos or []) if str(t).strip()]

    schedule_text = "\n".join(schedules) if schedules else "없음"
    todo_text = "\n".join(todos) if todos else "없음"

    # -------------------------------
    # 날짜 및 공통 지침
    # -------------------------------
    base_notice = "⚠️ 반드시 한국어로만 작성하세요. 영어 사용 금지."
    if target_date:
        base_notice += f"\n📅 기준 날짜: {target_date.strftime('%Y-%m-%d')}"

    # -------------------------------
    # 시간대별 프롬프트 템플릿
    # -------------------------------
    if period == "아침":
        content = f"""
# 아침 브리핑

- 오늘({target_date})의 날씨를 간단히 요약
- 오늘 예정된 주요 일정 ({schedule_text}) 을 정리
- 오늘 할 일 목록 ({todo_text}) 기반으로 짧은 동기 부여 문장
- 오늘의 운세를 한 문장으로 포함
- 전체를 3~4문장으로 작성
- 마지막에 **짧은 조언** 추가
        """

    elif period == "점심":
        content = f"""
# 점심 브리핑

- 오전에 완료된 일정 또는 진행 중인 작업 요약
- 남은 일정 ({schedule_text}) 과 할 일 ({todo_text}) 을 간단히 정리
- 주요 뉴스나 퀴즈 추천을 포함해 흥미 요소 추가
- 전체를 3~4문장으로 작성
- 마지막에 **짧은 조언** 추가
        """

    else:  # 저녁
        content = f"""
# 저녁 브리핑

- 오늘({target_date}) 일정 완료율을 실제 데이터 기반으로 요약
- 오늘 일정이 없으면 '오늘 일정 없음'이라고만 작성
- 내일 일정을 미리보기 형태로 정리
- 하루를 돌아보는 간단한 정리
- 전체를 3~4문장으로 작성
- 마지막에 **짧은 조언** 추가
- 내일 일정이 없을 경우 '내일 일정 없음'이라고만 작성
- 절대 허구의 수치를 생성하지 마세요. 없는 내용은 지어내지 마세요.
        """

    return f"{content}\n\n{base_notice}\n"