from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from enum import Enum
import httpx
from bs4 import BeautifulSoup
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

# ✅ 네이버 뉴스 섹션 URL 매핑
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
    data: List[NewsItem]

async def scrape_naver_news(section_url: str, limit: int = 6) -> List[dict]:
    """네이버 뉴스 섹션 페이지를 스크래핑"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://news.naver.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(section_url, headers=headers)
            response.raise_for_status()
            
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        
        # 네이버 뉴스 리스트 선택자 (실제 구조에 맞게 조정 필요)
        # 방법 1: 메인 뉴스 아이템들
        articles = soup.select('.sa_list .sa_item')
        
        if not articles:
            # 방법 2: 다른 선택자 시도
            articles = soup.select('.list_body .cluster_item')
            
        if not articles:
            # 방법 3: 가장 일반적인 뉴스 링크들
            articles = soup.select('a[href*="/article/"]')[:limit * 2]  # 여유있게 가져오기
            
        for article in articles:
            if len(news_items) >= limit:
                break
                
            try:
                # 제목과 링크 추출
                if article.name == 'a':
                    # 직접 링크인 경우
                    title_elem = article
                    link = article.get('href', '')
                    title = article.get_text(strip=True)
                else:
                    # 컨테이너인 경우
                    title_elem = article.select_one('.sa_text_title, .cluster_text_headline a, .sa_text_strong')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '') if title_elem.name == 'a' else title_elem.find_parent('a').get('href', '') if title_elem.find_parent('a') else ''
                
                # 링크 정리 (상대 링크면 절대 링크로 변환)
                if link.startswith('/'):
                    link = 'https://news.naver.com' + link
                elif link.startswith('//'):
                    link = 'https:' + link
                    
                if not link or not title or len(title) < 10:
                    continue
                    
                # 언론사 추출
                source = ""
                source_elem = article.select_one('.sa_text_press, .cluster_text_press')
                if source_elem:
                    source = source_elem.get_text(strip=True)
                
                # 요약 추출 (있다면)
                summary = ""
                summary_elem = article.select_one('.sa_text_lede, .cluster_text_lede')
                if summary_elem:
                    summary = summary_elem.get_text(strip=True)
                
                # 시간 추출
                published = ""
                time_elem = article.select_one('.sa_text_datetime, .cluster_text_datetime')
                if time_elem:
                    published = time_elem.get_text(strip=True)
                else:
                    published = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                news_items.append({
                    "title": title,
                    "url": link,
                    "published": published,
                    "source": source,
                    "summary": summary
                })
                
            except Exception as e:
                # 개별 아이템 파싱 실패시 건너뛰기
                continue
        
        return news_items
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"네이버 뉴스 스크래핑 실패: {str(e)}")



@router.get("/", response_model=NewsResponse)
async def get_news(
    category: NewsCategory = Query(..., description="뉴스 카테고리"),
    limit: int = Query(default=6, ge=1, le=20, description="가져올 뉴스 개수 (1~20)")
):
    """네이버 뉴스를 스크래핑으로 가져옵니다."""
    
    try:
        section_url = NAVER_NEWS_SECTIONS[category.value]
        news_items = await scrape_naver_news(section_url, limit)
        
        if not news_items:
            raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다")
        
        return {
            "success": True,
            "category": category.value,
            "count": len(news_items),
            "data": news_items,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 조회 실패: {str(e)}")