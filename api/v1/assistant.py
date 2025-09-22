from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from tortoise.expressions import Q
from datetime import date
from typing import Optional, List
from models.todos import Todo
from models.schedules import Schedule
import re

router = APIRouter()

#  부적절 단어 목록 (실제 운영 시 더 확장 가능)
BAD_WORDS = [
    "욕설", "비속어", "혐오", "차별", "폭력", "테러", "자살", "마약", "불법",
    "바보", "멍청", "죽어", "꺼져", "시발", "개새", "병신", "미친",
]


class ChatRequest(BaseModel):
    message: str

    @validator("message")
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("메시지를 입력해주세요.")
        
        if len(v) > 200:
            raise ValueError("메시지는 200자 이내여야 합니다.")
        
        #  부적절 단어 검사 (정규식)
        for bad in BAD_WORDS:
            if re.search(rf"\b{bad}\b", v.lower()):
                raise ValueError("부적절한 단어가 포함되어 있습니다.")
        
        #  코드 입력 방지
        if "```" in v or "import " in v.lower():
            raise ValueError("코드 입력은 허용되지 않습니다.")
        
        return v.strip()


class ChatResponse(BaseModel):
    reply: str
    data: Optional[dict] = None


@router.post("/assistant", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """AI 어시스턴트와의 대화 처리"""
    user_message = request.message.lower()
    today = date.today()

    try:
        #  오늘 할 일 조회
        if any(keyword in user_message for keyword in ["오늘 할일", "오늘 할 일", "투두", "todo"]):
            todos = await Todo.filter(
                Q(due_date=today) & Q(is_completed=False)
            ).all()

            schedules = await Schedule.filter(
                Q(start_time__date__lte=today) & Q(end_time__date__gte=today)
            ).all()

            todo_list = "\n".join([f"• {t.title}" for t in todos]) if todos else "할 일이 없어요 "
            schedule_list = "\n".join([f"• {s.title}" for s in schedules]) if schedules else "일정이 없어요 📅"

            reply = f" 오늘의 할 일:\n{todo_list}\n\n 오늘의 일정:\n{schedule_list}"
            
            return ChatResponse(
                reply=reply,
                data={
                    "todos": [t.title for t in todos],
                    "schedules": [s.title for s in schedules],
                    "todos_count": len(todos),
                    "schedules_count": len(schedules),
                    "date": today.isoformat()
                }
            )

        #  완료된 할 일 조회
        elif any(keyword in user_message for keyword in ["완료된 할일", "완료된 할 일", "끝난 일"]):
            completed_todos = await Todo.filter(
                Q(due_date=today) & Q(is_completed=True)
            ).all()

            if completed_todos:
                completed_list = "\n".join([f"✔ {t.title}" for t in completed_todos])
                reply = f"🎉 오늘 완료한 일들:\n{completed_list}\n\n수고하셨어요!"
            else:
                reply = "아직 완료한 일이 없네요. 화이팅! 💪"

            return ChatResponse(
                reply=reply,
                data={
                    "completed": [t.title for t in completed_todos],
                    "completed_count": len(completed_todos),
                    "date": today.isoformat()
                }
            )

        #  인사말 응답
        elif any(keyword in user_message for keyword in ["안녕", "hello", "hi", "헬로"]):
            return ChatResponse(
                reply="안녕하세요!  무엇을 도와드릴까요?\n\n 예시 질문:\n• '오늘 할일이 있나요?'\n• '완료된 할일을 보여주세요'"
            )

        #  도움말
        elif any(keyword in user_message for keyword in ["도움", "help", "명령어", "기능"]):
            help_text = """
 AI 어시스턴트 기능:

 할 일 관리
• "오늘 할일" - 오늘의 할 일과 일정 확인
• "완료된 할일" - 완료한 작업 확인

 기본 대화
• 간단한 인사말과 대화 가능

 도움말
• "도움말" - 가능한 기능 안내
            """
            return ChatResponse(reply=help_text.strip())

        #  감사 인사
        elif any(keyword in user_message for keyword in ["고마워", "감사", "thank"]):
            return ChatResponse(reply="천만에요! 언제든지 도와드릴게요! 🙌")

        #  기본 응답
        else:
            return ChatResponse(
                reply=(
                    "죄송해요, 아직 그 요청은 이해하지 못했어요. \n\n"
                    " 이렇게 물어보실 수 있어요:\n"
                    "• '오늘 할일이 있나요?'\n"
                    "• '완료된 할일을 보여주세요'\n"
                    "• '도움말'"
                )
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"처리 중 오류가 발생했습니다: {str(e)}"
        )
