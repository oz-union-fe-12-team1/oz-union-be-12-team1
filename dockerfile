# ---- Base image --------------------------------------------------------------
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_SYSTEM_PYTHON=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# 의존성 먼저 복사/설치 (캐시 최적화)
COPY pyproject.toml uv.lock* ./
RUN uv venv /opt/venv && . /opt/venv/bin/activate && uv sync --frozen --no-dev
ENV PATH="/opt/venv/bin:${PATH}"

# 애플리케이션 전체 복사 (✅ 루트의 모든 폴더/파일)
COPY . .

EXPOSE 8000

# 엔트리포인트: 네 트리 기준으로 main.py 안의 FastAPI 인스턴스 이름이 app 이라고 가정
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
