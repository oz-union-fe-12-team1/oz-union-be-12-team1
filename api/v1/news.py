from bs4.element import AttributeValueList
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, cast, Any
from enum import Enum
import httpx
from bs4 import BeautifulSoup, Tag, ResultSet
from datetime import datetime
import re

router = APIRouter(prefix="/news", tags=["news"])

class NewsCategory(str, Enum):
    politics = "politics"
    economy = "economy"
    society = "society"
    life_culture = "life_culture"
    it_science = "it_science"
    world = "world"

#  네이버 뉴스 섹션 URL 매핑
NAVER_NEWS_SECTIONS = {
    "politics": "https://news.naver.com/section/100",      # 정치
    "economy": "https://news.naver.com/section/101",       # 경제
    "society": "https://news.naver.com/section/102",       # 사회
    "life_culture": "https://news.naver.com/section/103",  # 생활/문화
    "world": "https://news.naver.com/section/104",         # 세계
    "it_science": "https://news.naver.com/section/105",    # IT/과학
}

# Pydantic 스키마 정의
class NewsItem(BaseModel):
    title: str
    url: str
    published: str
    source: str = ""
    summary: str = ""

class NewsResponse(BaseModel):
    success: bool
    category: str
    count: int
    data: List[dict]

async def scrape_naver_news(section_url: str, limit: int = 6) -> List[dict]:
    headers = {
        'User-Agent': 'Mozilla/5.0 ...',
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(section_url, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        news_items: List[dict] = []

        articles: list[Tag] = list(soup.select('.sa_list .sa_item'))
        if not articles:
            articles = list(soup.select('.list_body .cluster_item'))
        if not articles:
            articles = list(soup.select('a[href*="/article/"]'))[:limit * 2]

        for article in articles:
            if len(news_items) >= limit:
                break

            try:
                link: str = ""
                if article.name == 'a':
                    title = article.get_text(strip=True)
                    link_attr: Optional[Any] = article.get('href')
                    if isinstance(link_attr, str):
                        link = link_attr
                else:
                    title_elem: Optional[Tag] = cast(Optional[Tag], article.select_one(
                        '.sa_text_title, .cluster_text_headline a, .sa_text_strong'
                    ))

                    if title_elem is None:
                        continue

                    # 이제 title_elem은 안전하게 Tag로 취급 가능
                    title = title_elem.get_text(strip=True)
                    parent_a: Optional[Tag] = cast(Optional[Tag], title_elem.find_parent('a'))
                    link_attr = parent_a.get('href') if parent_a else None
                    if isinstance(link_attr, str):
                        link = link_attr if link_attr else ""

                # 링크 보정
                if link.startswith('/'):
                    link = 'https://news.naver.com' + link
                elif link.startswith('//'):
                    link = 'https:' + link

                if not title or not link:
                    continue

                # 언론사
                source_elem: Optional[Tag] = article.select_one('.sa_text_press, .cluster_text_press')
                source: str = source_elem.get_text(strip=True) if source_elem else ""

                # 요약
                summary_elem: Optional[Tag] = article.select_one('.sa_text_lede, .cluster_text_lede')
                summary: str = summary_elem.get_text(strip=True) if summary_elem else ""

                # 시간
                time_elem: Optional[Tag] = article.select_one('.sa_text_datetime, .cluster_text_datetime')
                published: str = time_elem.get_text(strip=True) if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M")

                news_items.append({
                    "title": title,
                    "url": link,
                    "published": published,
                    "source": source,
                    "summary": summary
                })

            except Exception:
                continue

        return news_items

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 스크래핑 실패: {str(e)}")



@router.get("/", response_model=NewsResponse)
async def get_news(
    category: NewsCategory = Query(..., description="뉴스 카테고리"),
    limit: int = Query(default=6, ge=1, le=20, description="가져올 뉴스 개수 (1~20)")
) -> NewsResponse:
    """네이버 뉴스를 스크래핑으로 가져옵니다."""

    try:
        section_url = NAVER_NEWS_SECTIONS[category.value]
        news_items = await scrape_naver_news(section_url, limit)

        if not news_items:
            raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다")

        return NewsResponse(
            success=True,
            category=category.value,
            count=len(news_items),
            data=news_items,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 조회 실패: {str(e)}")