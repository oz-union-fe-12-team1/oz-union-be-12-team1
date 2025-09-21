from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from tortoise.expressions import Q
from datetime import date
from typing import Optional
from models.todos import Todo
from models.schedules import Schedule

router = APIRouter()

#  수정: BAD_WORDS 정의 추가
BAD_WORDS = [
    "욕설", "비속어", "혐오", "차별", "폭력", "테러", "자살", "마약", "불법",
    "바보", "멍청", "죽어", "꺼져", "시발", "개새", "병신", "미친",
    # 실제 운영시에는 더 세밀한 필터링 목록 필요
]


class ChatRequest(BaseModel):
    message: str

    @validator("message")
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("메시지를 입력해주세요.")
        
        if len(v) > 200:
            raise ValueError("메시지는 200자 이내여야 합니다.")
        
        # 부적절한 단어 검사
        if any(bad in v.lower() for bad in BAD_WORDS):
            raise ValueError("부적절한 단어가 포함되어 있습니다.")
        
        # 코드 입력 방지
        if "```" in v or "import " in v.lower():
            raise ValueError("코드 입력은 허용되지 않습니다.")
        
        return v.strip()


class ChatResponse(BaseModel):
    reply: str
    data: Optional[dict] = None


@router.post("/assistant", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """AI 어시스턴트와의 대화 처리"""
    user_message = request.message.lower()  # 대소문자 구분 없이 처리
    
    try:
        # 🔍 오늘 할 일 조회
        if any(keyword in user_message for keyword in ["오늘 할일", "오늘 할 일", "투두", "todo"]):
            today = date.today()

            # DB에서 오늘 할 일/일정 가져오기
            todos = await Todo.filter(
                Q(created_at__date=today) & Q(is_completed=False)
            ).all()

            schedules = await Schedule.filter(
                Q(start_time__date=today)
            ).all()

            # 결과 문자열 생성
            todo_list = "\n".join([f"• {t.title}" for t in todos]) if todos else "할 일이 없어요 "
            schedule_list = "\n".join([f"• {s.title}" for s in schedules]) if schedules else "일정이 없어요 📅"

            reply = f" 오늘의 할 일:\n{todo_list}\n\n 오늘의 일정:\n{schedule_list}"
            
            return ChatResponse(
                reply=reply,
                data={
                    "todos_count": len(todos),
                    "schedules_count": len(schedules),
                    "date": today.isoformat()
                }
            )

        # 🔍 완료된 할 일 조회
        elif any(keyword in user_message for keyword in ["완료된 할일", "완료된 할 일", "끝난 일"]):
            today = date.today()
            completed_todos = await Todo.filter(
                Q(created_at__date=today) & Q(is_completed=True)
            ).all()

            if completed_todos:
                completed_list = "\n".join([f" {t.title}" for t in completed_todos])
                reply = f"🎉 오늘 완료한 일들:\n{completed_list}\n\n수고하셨어요!"
            else:
                reply = "아직 완료한 일이 없네요. 화이팅! 💪"

            return ChatResponse(reply=reply)

        # 🔍 인사말 응답
        elif any(keyword in user_message for keyword in ["안녕", "hello", "hi", "헬로"]):
            return ChatResponse(reply="안녕하세요! 😊 무엇을 도와드릴까요?\n\n💡 다음과 같이 물어보세요:\n• '오늘 할일이 있나요?'\n• '완료된 할일을 보여주세요'")

        # 🔍 도움말
        elif any(keyword in user_message for keyword in ["도움", "help", "명령어", "기능"]):
            help_text = """
 AI 어시스턴트 기능:

 **할 일 관리**
• "오늘 할일" - 오늘의 할 일과 일정 확인
• "완료된 할일" - 완료한 작업 확인

**기본 대화**
• 간단한 인사말과 대화 가능

 **도움이 필요하시면** "도움말"이라고 말씀해주세요!
            """
            return ChatResponse(reply=help_text.strip())

        # 🔍 감사 인사
        elif any(keyword in user_message for keyword in ["고마워", "감사", "thank"]):
            return ChatResponse(reply="천만에요!  언제든지 도와드릴게요!")

        # 🔍 기본 응답
        else:
            return ChatResponse(
                reply="죄송해요, 아직 그 요청은 이해하지 못했어요. \n\n 다음과 같이 말해보세요:\n• '오늘 할일이 있나요?'\n• '완료된 할일을 보여주세요'\n• '도움말'"
            )

    except Exception as e:
        # 데이터베이스 오류나 기타 예외 처리
        raise HTTPException(
            status_code=500, 
            detail=f"처리 중 오류가 발생했습니다: {str(e)}"
        )