from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from tortoise.expressions import Q
from datetime import date, datetime
from models.todo import Todo
from models.schedules import Schedule

router = APIRouter()

BAD_WORDS = ["fuck", "shit", "바보", "멍청이"]

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


@router.post("/assistant")
async def chat_with_assistant(request: ChatRequest):
    """AI 어시스턴트 기본 대화"""
    user_message = request.message.strip()

    if "오늘 할일" in user_message or "오늘 할 일" in user_message:
        today = date.today()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())

        todos = await Todo.filter(created_at__gte=start, created_at__lte=end, is_completed=False).all()
        schedules = await Schedule.filter(start_time__gte=start, start_time__lte=end).all()

        return {
            "success": True,
            "data": {
                "type": "assistant",
                "todos": [t.title for t in todos],
                "schedules": [s.title for s in schedules],
                "generated_at": datetime.now().isoformat(),
            },
        }

    if "안녕하세요" in user_message:
        return {
            "success": True,
            "data": {"type": "assistant", "reply": "안녕하세요! 무엇을 도와드릴까요?", "generated_at": datetime.now().isoformat()},
        }

    return {"success": False, "error": {"code": "UNSUPPORTED_REQUEST", "message": "지원하지 않는 요청입니다."}}
