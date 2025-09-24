from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


# 👉 뉴스 카테고리 Enum
class NewsCategory(str, Enum):
    politics = "politics"
    economy = "economy"
    society = "society"
    life_culture = "life_culture"
    it_science = "it_science"
    world = "world"


# 👉 개별 뉴스 아이템
class NewsItem(BaseModel):
    title: str = Field(..., example="Breaking News: 중요한 뉴스 제목")
    url: str = Field(..., example="https://example.com/news/123")
    published: Optional[str] = Field(None, example="2025-09-23T10:30:00Z")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Breaking News: 중요한 뉴스 제목",
                "url": "https://example.com/news/123",
                "published": "2025-09-23T10:30:00Z"
            }
        }
    }


# 👉 뉴스 응답
class NewsResponse(BaseModel):
    success: bool = Field(..., example=True)
    category: NewsCategory = Field(..., example="politics")
    count: int = Field(..., example=3)
    data: List[NewsItem]

    model_config = {
        "json_schema_extra": {
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
    }


# 👉 에러 응답
class ErrorResponse(BaseModel):
    detail: str = Field(..., example="잘못된 카테고리입니다")

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "잘못된 카테고리입니다"
            }
        }
    }
