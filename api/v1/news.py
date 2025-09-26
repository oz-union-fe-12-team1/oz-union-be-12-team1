from fastapi import APIRouter, HTTPException, Query
from enum import Enum
from typing import List

from services.news_service import scrape_naver_news
from schemas.news import NewsItem, NewsResponse   # ✅ 여기서만 스키마 import

router = APIRouter(prefix="/news", tags=["news"])

class NewsCategory(str, Enum):
    politics = "politics"
    economy = "economy"
    society = "society"
    life_culture = "life_culture"
    world = "world"
    it_science = "it_science"

NAVER_NEWS_SECTIONS = {
    "politics": "https://news.naver.com/section/100",
    "economy": "https://news.naver.com/section/101",
    "society": "https://news.naver.com/section/102",
    "life_culture": "https://news.naver.com/section/103",
    "world": "https://news.naver.com/section/104",
    "it_science": "https://news.naver.com/section/105",
}

@router.get("/", response_model=NewsResponse, summary="네이버 뉴스 조회")
async def get_news(
    category: NewsCategory = Query(..., description="뉴스 카테고리"),
) -> NewsResponse:
    section_url = NAVER_NEWS_SECTIONS[category.value]

    try:
        raw_items = await scrape_naver_news(section_url, limit=6)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 스크래핑 실패: {e}")

    if not raw_items:
        raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다")

    # dict → Pydantic 모델 변환
    news_items = [NewsItem(**item) for item in raw_items]

    return NewsResponse(
        success=True,
        category=category.value,
        count=len(news_items),
        data=news_items,
    )

