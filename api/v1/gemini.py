import os
from fastapi import APIRouter, Query, HTTPException
import httpx
from datetime import datetime

router = APIRouter()

#  보안: 환경변수에서 API 키 가져오기
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"


async def gemini_request(prompt: str) -> str:
    """Gemini API 요청 함수"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.post(
                GEMINI_URL,
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
        
        if res.status_code != 200:
            raise HTTPException(
                status_code=res.status_code,
                detail=f"Gemini API 오류: {res.text}"
            )
        
        data = res.json()
        
        if "candidates" not in data or not data["candidates"]:
            raise HTTPException(
                status_code=500,
                detail="Gemini API 응답 형식이 올바르지 않습니다"
            )
        
        return data["candidates"][0]["content"]["parts"][0]["text"]
    
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Gemini API 요청 시간 초과")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"API 요청 오류: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예상치 못한 오류: {str(e)}")


# ======================
# 운세 API
# ======================
@router.get("/fortune")
async def get_fortune(birthday: str = Query(..., description="YYYY-MM-DD 형식")):
    """사용자 생년월일 기반 운세 제공"""
    try:
        datetime.strptime(birthday, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="생년월일은 YYYY-MM-DD 형식이어야 합니다")
    
    prompt = f"""
    당신은 전문 운세가입니다.
    생년월일 {birthday} 사용자의 오늘 운세를 작성하세요.
    조건:
    - 300자 이내
    - 긍정적이고 희망적인 메시지
    - 일/학업, 금전, 연애, 건강 중 최소 2가지 언급
    - 마지막에 ✨오늘의 한 줄 조언✨ 포함
    """
    
    fortune = await gemini_request(prompt)
    return {
        "success": True,
        "data": {
            "birthday": birthday,
            "fortune": fortune,
            "created_at": datetime.now().isoformat(),
        },
    }


# ======================
# 브리핑 API (아침/저녁/하루)
# ======================
@router.get("/briefings")
async def get_briefings(type: str = Query("morning", description="morning / evening / daily")):
    """아침/저녁/하루 브리핑 제공"""
    if type not in ["morning", "evening", "daily"]:
        raise HTTPException(status_code=400, detail="type은 'morning' | 'evening' | 'daily' 중 하나여야 합니다")
    
    if type == "morning":
        prompt = """
        당신은 개인 비서입니다.
        아침 브리핑을 작성하세요.
        조건:
        - 300자 이내
        - 오늘 날씨 + 일정 시작 안내 + 동기부여
        - 친근한 한국어, 이모지 포함
        """
    elif type == "evening":
        prompt = """
        당신은 개인 비서입니다.
        저녁 브리핑을 작성하세요.
        조건:
        - 300자 이내
        - 오늘 일정/투두 회고 + 내일 준비
        - 친근한 한국어, 이모지 포함
        """
    else:  # daily
        prompt = """
        당신은 개인 비서입니다.
        하루 요약 브리핑을 작성하세요.
        조건:
        - 300자 이내
        - 오늘 일정/투두 결과 요약 + 내일 일정 미리보기
        - 친근한 한국어, 이모지 포함
        """
    
    briefing = await gemini_request(prompt)
    return {
        "success": True,
        "data": {
            "type": type,
            "summary": briefing,
            "created_at": datetime.now().isoformat()
        }
    }


# ======================
# 대화 요약 API
# ======================
@router.get("/conversations")
async def get_conversations(message: str = Query(..., description="사용자 요청 메시지")):
    """사용자 메시지 기반 대화형 응답"""
    if not message or len(message.strip()) == 0:
        raise HTTPException(status_code=400, detail="메시지가 비어있습니다")
    
    if len(message) > 500:
        raise HTTPException(status_code=400, detail="메시지는 500자 이내여야 합니다")
    
    prompt = f"""
    사용자가 요청: "{message}"
    사용자의 일정과 할 일을 요약하는 대화를 작성하세요.
    조건:
    - 간단한 한국어
    - 2~3문장 이내 요약
    - 완료/미완료 개수나 진행 상황 강조
    - 친근하고 도움이 되는 톤
    """
    
    summary = await gemini_request(prompt)
    return {
        "success": True,
        "data": {
            "type": "conversation",
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        },
    }
