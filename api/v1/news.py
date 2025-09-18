from fastapi import APIRouter, HTTPException
import httpx
import feedparser

router = APIRouter()


@router.get("/news")
async def get_news():
    rss_url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(rss_url)

    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="뉴스 불러오기 실패")

    feed = feedparser.parse(res.text)
    items = feed.entries[:6]

    return {
        "success": True,
        "data": [
            {"title": item.title, "url": item.link, "source": "Google News"}
            for item in items
        ],
    }
