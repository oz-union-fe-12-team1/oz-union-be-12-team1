from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator
from tortoise.expressions import Q
from datetime import date
from models.todos import Todo
from models.schedules import Schedule

router = APIRouter()


#  요청 스키마
class ChatRequest(BaseModel):
    message: str

    @validator("message")
    def validate_message(cls, v):
        if len(v) > 200:
            raise ValueError("메시지는 200자 이내여야 합니다.")
        if any(bad in v.lower() for bad in BAD_WORDS):
            raise ValueError("부적절한 단어가 포함되어 있습니다.")
        if "```" in v or "import " in v.lower():
            raise ValueError("코드 입력은 허용되지 않습니다.")
        return v


class ChatResponse(BaseModel):
    reply: str


@router.post("/assistant", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    user_message = request.message.strip()

    #  오늘 할 일 조회
    if "오늘 할일" in user_message or "오늘 할 일" in user_message:
        today = date.today()

        # DB에서 오늘 할 일/일정 가져오기
        todos = await Todo.filter(
            Q(created_at__date=today) & Q(is_completed=False)
        ).all()

        schedules = await Schedule.filter(
            Q(start_time__date=today)
        ).all()

        # 결과 문자열 생성
        todo_list = "\n".join([f"- {t.title}" for t in todos]) or "할 일이 없어요 ✅"
        schedule_list = "\n".join([f"- {s.title}" for s in schedules]) or "일정이 없어요 📅"

        reply = f" 오늘의 할 일:\n{todo_list}\n\n🗓 오늘의 일정:\n{schedule_list}"
        return ChatResponse(reply=reply)

    # ✅ 기본 인삿말
    if "안녕하세요" in user_message:
        return ChatResponse(reply="안녕하세요! 무엇을 도와드릴까요?")

    # ✅ 기본 응답 (지원하지 않는 요청)
    return ChatResponse(reply="죄송해요, 그 요청은 이해하지 못했어요. 😅 '오늘 할일이 있나요?'라고 물어보실 수 있어요.")
