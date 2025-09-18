from fastapi import APIRouter, HTTPException
import gspread
import random
from google.oauth2.service_account import Credentials

router = APIRouter()

# 구글 서비스 계정 키 파일 (프로젝트 루트에 google-credentials.json 저장)
SERVICE_ACCOUNT_FILE = "google-credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

SPREADSHEET_ID = "1n6YYFyrLJBrPI7qwsdu6kjbSfWDTEEkbxiidKeBE-vs"
SHEET_NAME = "quiz"


def load_quizzes():
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_records()
    if not data:
        raise HTTPException(status_code=404, detail="퀴즈가 없습니다")
    return data


@router.get("/quiz")
async def get_quiz():
    quizzes = load_quizzes()
    quiz = random.choice(quizzes)
    return {
        "success": True,
        "data": {
            "id": quiz.get("id", 0),
            "question": quiz.get("question"),
            "options": [
                quiz.get("option1"),
                quiz.get("option2"),
                quiz.get("option3"),
                quiz.get("option4"),
            ],
            "answer": quiz.get("answer"),
        },
    }
