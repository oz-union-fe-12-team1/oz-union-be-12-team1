from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from enum import Enum
import httpx
import feedparser

# ✅ 네이버 뉴스 섹션 URL 매핑 (RSS 대신 네이버 섹션 그대로 사용)
NAVER_NEWS_SECTIONS = {
    "politics": "https://news.naver.com/section/100",  # 정치
    "economy": "https://news.naver.com/section/101",  # 경제
    "society": "https://news.naver.com/section/102",  # 사회
    "life_culture": "https://news.naver.com/section/103",  # 생활/문화
    "world": "https://news.naver.com/section/104",  # 세계
    "it_science": "https://news.naver.com/section/105",  # IT/과학
}

router = APIRouter(prefix="/news", tags=["news"])


# Enum 정의
class NewsCategory(str, Enum):
    politics = "politics"
    economy = "economy"
    society = "society"
    life_culture = "life_culture"
    it_science = "it_science"
    world = "world"


# RSS 피드 URL 매핑
# NEWS_RSS_FEEDS = {
#     "politics": "https://feeds.bbci.co.uk/news/politics/rss.xml",
#     "economy": "https://feeds.bbci.co.uk/news/business/rss.xml",
#     "society": "https://feeds.bbci.co.uk/news/world/rss.xml",
#     "life_culture": "https://www.nytimes.com/services/xml/rss/nyt/FashionandStyle.xml",
#     "it_science": "https://feeds.bbci.co.uk/news/technology/rss.xml",
#     "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
# }

# 스키마 정의
class NewsItem(BaseModel):
    """개별 뉴스 아이템"""
    title: str
    url: str
    published: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Breaking News: 중요한 뉴스 제목",
                "url": "https://example.com/news/123",
                "published": "2025-09-23T10:30:00Z"
            }
        }


class NewsResponse(BaseModel):
    """뉴스 API 응답"""
    success: bool
    category: str
    count: int
    data: List[NewsItem]  # ✅ dict → NewsItem 으로 변경

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "category": "politics",
                "count": 3,
                "data": [
                    {
                        "title": "정치 뉴스 제목 1",
                        "url": "https://example.com/politics/1",
                        "published": "2025-09-23T10:30:00Z"
                    },
                    {
                        "title": "정치 뉴스 제목 2",
                        "url": "https://example.com/politics/2",
                        "published": "2025-09-23T09:15:00Z"
                    },
                    {
                        "title": "정치 뉴스 제목 3",
                        "url": "https://example.com/politics/3",
                        "published": "2025-09-23T08:45:00Z"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """에러 응답"""
    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "잘못된 카테고리입니다"
            }
        }


# API 엔드포인트
@router.get(
    "/",
    response_model=NewsResponse,
    summary="뉴스 조회",
    description="카테고리별 뉴스를 조회합니다.",
    responses={
        200: {
            "description": "뉴스 조회 성공",
            "model": NewsResponse
        },
        400: {
            "description": "잘못된 요청",
            "model": ErrorResponse
        },
        500: {
            "description": "서버 오류",
            "model": ErrorResponse
        }
    }
)
async def get_news(
        category: NewsCategory = Query(
            NewsCategory.politics,
            description="뉴스 카테고리 (politics, economy, society, life_culture, it_science, world)"
        ),
        limit: int = Query(
            default=6,
            ge=1,
            le=20,
            description="가져올 뉴스 개수 (1~20)"
        )
) -> NewsResponse:
    """
    카테고리별 뉴스를 조회하는 API

    - **category**: 뉴스 카테고리 선택
    - **limit**: 조회할 뉴스 개수 (기본값: 6)
    """

    # 뉴스 요청
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(NAVER_NEWS_SECTIONS[category.value])
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"뉴스 요청 실패: {str(e)}")

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="뉴스 불러오기 실패")

    # ✅ feedparser 대신 BeautifulSoup 로 파싱하거나
    #    여기서는 단순히 제목만 보여주도록 수정 (임시 처리)
    feed = feedparser.parse(res.text)

    if not feed.entries:
        raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다")

    items = feed.entries[:limit]

    # 응답 데이터 구성
    news_items = [
        NewsItem(
            title=item.get("title", "N/A"),
            url=item.get("link", "N/A"),
            published=item.get("published", "N/A")
        )
        for item in items
    ]

    return NewsResponse(
        success=True,
        category=category.value,
        count=len(news_items),
        data=news_items
    )
