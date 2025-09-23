from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from enum import Enum
import httpx
import feedparser

router = APIRouter(prefix="/news", tags=["news"])

class NewsCategory(str, Enum):
    politics = "politics"
    economy = "economy"
    society = "society"
    life_culture = "life_culture"
    it_science = "it_science"
    world = "world"

NEWS_RSS_FEEDS = {
    "politics": "https://feeds.bbci.co.uk/news/politics/rss.xml",
    "economy": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "society": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "life_culture": "https://www.nytimes.com/services/xml/rss/nyt/FashionandStyle.xml",
    "it_science": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
}

# Pydantic 스키마 정의
class NewsItem(BaseModel):
    title: str
    url: str
    published: str

class NewsResponse(BaseModel):
    success: bool
    category: str
    count: int
    data: List[NewsItem]

@router.get("/", response_model=NewsResponse)
async def get_news(
    category: NewsCategory = NewsCategory.politics,
    limit: int = Query(default=6, ge=1, le=20, description="가져올 뉴스 개수 (1~20)")
):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(NEWS_RSS_FEEDS[category.value])
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"뉴스 요청 실패: {str(e)}")

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="뉴스 불러오기 실패")

    feed = feedparser.parse(res.text)
    
    # RSS 파싱 실패 체크 추가
    if not feed.entries:
        raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다")
    
    items = feed.entries[:limit]

    return {
        "success": True,
        "category": category.value,
        "count": len(items),
        "data": [
            {
                "title": i.title,
                "url": i.link,
                "published": i.get("published", "N/A")
            }
            for i in items
        ],
    }