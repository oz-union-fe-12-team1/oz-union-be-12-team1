import os, random, gspread
from fastapi import APIRouter, HTTPException
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/quiz", tags=["quiz"])

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "quiz")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Google 인증 (앱 실행 시 실패해도 서버 전체가 죽지 않도록 Lazy 로딩 방식으로 변경)
def get_gspread_client():
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Sheets 인증 실패: {e}")


def load_quizzes():
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        return sheet.get_all_records()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"퀴즈 로드 실패: {e}")


@router.get("/")
async def get_quiz():
    quizzes = load_quizzes()
    if not quizzes:
        raise HTTPException(status_code=404, detail="퀴즈가 없습니다")

    quiz = random.choice(quizzes)
    return {
        "success": True,
        "data": {
            "id": quiz.get("id", 0),
            "question": quiz.get("question"),
            "options": [quiz.get(f"option{i}") for i in range(1, 5) if quiz.get(f"option{i}")],
            "answer": quiz.get("answer"),
        },
    }
