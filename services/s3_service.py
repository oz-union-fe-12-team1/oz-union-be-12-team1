import boto3
from datetime import datetime
from typing import Dict
from botocore.config import Config
from core.config import settings


class S3Service:
    @staticmethod
    def create_presigned_url(filename: str, content_type: str) -> Dict[str, str]:
        """
        S3에 업로드할 수 있는 Presigned URL을 생성합니다.
        :param filename: 원본 파일명 (예: "cat.png")
        :param content_type: MIME 타입 (예: "image/png")
        :return: {"upload_url": str, "file_url": str}
        """
        # ✅ Signature Version 4 강제 설정
        s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),  # ⭐ 핵심
        )

        # ✅ 업로드 경로 (고유한 파일명)
        key = f"uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"

        # ✅ presigned URL 생성 (ContentType 포함 — 프론트와 반드시 일치해야 함)
        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_S3_BUCKET,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=3600,  # 1시간 유효
        )

        # ✅ 실제 S3 접근 가능한 파일 경로
        file_url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"

        return {"upload_url": presigned_url, "file_url": file_url}
