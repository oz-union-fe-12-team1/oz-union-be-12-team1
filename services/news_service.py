import httpx
from typing import List, Optional
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from fastapi import HTTPException

# ✅ 더 이상 api.v1.news.NewsItem 불러오지 않음 (순환참조 방지)
# 서비스 계층에서는 dict만 다루고, 스키마 변환은 라우터에서
# from schemas.news import NewsItem   # ❌ 빼기

# ==============================
# 기사 목록 추출 (섹션 뉴스)
# ==============================
ARTICLE_SELECTORS = [
    ".sa_list .sa_item",
    ".list_body .cluster_item",
    ".newsnow_wrap .newsnow_item",
    "li.sa_item",
    'a[href*="/article/"]',
]


def extract_articles(soup: BeautifulSoup, limit: int) -> List[Tag]:
    """네이버 뉴스 기사 태그들을 추출하는 범용 함수"""
    for selector in ARTICLE_SELECTORS:
        articles = soup.select(selector)
        if articles:
            return articles[: limit * 2]  # limit보다 조금 더 가져와서 필터링
    return []


def parse_article(article: Tag) -> Optional[dict]:
    """기사 1개 파싱 → dict 반환"""
    try:
        # 제목
        title_elem = article.select_one(".sa_text_title, .sa_text_strong")
        title = title_elem.get_text(strip=True) if title_elem else None

        # 링크
        link_tag = article.select_one("a")
        raw_link = link_tag.get("href") if link_tag else None
        link: Optional[str] = raw_link if isinstance(raw_link, str) else None

        if link and link.startswith("/"):
            link = "https://news.naver.com" + link

        # 언론사
        source_elem = article.select_one(".sa_text_press")
        source = source_elem.get_text(strip=True) if source_elem else None

        # 요약
        summary_elem = article.select_one(".sa_text_lede")
        summary = summary_elem.get_text(strip=True) if summary_elem else None

        # 시간
        time_elem = article.select_one(".sa_text_datetime")
        published = (
            time_elem.get_text(strip=True)
            if time_elem
            else datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        if title and link:
            return {
                "title": title,
                "url": link,
                "source": source,
                "summary": summary,
                "published": published,
            }
        return None
    except Exception:
        return None


async def scrape_naver_news(section_url: str, limit: int = 6) -> List[dict]:
    """네이버 뉴스 목록 스크래핑"""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(section_url, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        articles = extract_articles(soup, limit)

        news_items: List[dict] = []
        for article in articles:
            if len(news_items) >= limit:
                break
            parsed = parse_article(article)
            if parsed:
                news_items.append(parsed)

        return news_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 스크래핑 실패: {str(e)}")
