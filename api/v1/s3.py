from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.s3_service import S3Service

router = APIRouter(prefix="/s3", tags=["S3"])

# ==========================
# 요청 스키마
# ==========================
class PresignedRequest(BaseModel):
    filename: str
    content_type: str

# ==========================
# 응답 스키마
# ==========================
class PresignedResponse(BaseModel):
    upload_url: str
    file_url: str


# Presigned URL 발급 API
@router.post("/presigned-url", response_model=dict[str, Any])
async def get_presigned_url(req: PresignedRequest) -> dict[str, Any]:
    """
    S3 Presigned URL 발급 API
    - 입력: 파일명, Content-Type
    - 출력: 업로드용 URL(upload_url), 최종 접근 URL(file_url)
    """
    try:
        result = S3Service.create_presigned_url(
            filename=req.filename,
            content_type=req.content_type
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
