import os
import random
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/quiz", tags=["quiz"])

#  환경변수에서 엑셀 경로 불러오기 (없으면 기본값 quiz.xlsx)
EXCEL_FILE = os.getenv("QUIZ_FILE", "quiz.xlsx")

#  엑셀 로드 함수
def load_quizzes() -> Any:
    try:
        # pandas로 엑셀 읽기
        df = pd.read_excel(EXCEL_FILE)
        # DataFrame → 리스트[dict]
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"퀴즈 로드 실패: {e}")

#  랜덤 퀴즈 API
@router.get("/")
async def get_quiz() -> dict[str, Any]:
    quizzes = load_quizzes()
    if not quizzes:
        raise HTTPException(status_code=404, detail="퀴즈가 없습니다")

    quiz = random.choice(quizzes)

    options = [
        quiz.get(f"option{i}")
        for i in range(1, 5)
        if quiz.get(f"option{i}") not in (None, "", " ")
    ]

    return {
        "success": True,
        "data": {
            "id": quiz.get("id", 0),
            "question": quiz.get("question"),
            "options": options,  # ← 수정된 부분
            "answer": quiz.get("answer"),
        },
    }
