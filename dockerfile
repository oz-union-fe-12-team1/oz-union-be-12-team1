# ---- Base image --------------------------------------------------------------
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_SYSTEM_PYTHON=1

# 기본 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# -------------------------
# 1. 의존성 정의 파일 먼저 복사
# -------------------------
COPY pyproject.toml uv.lock* ./
COPY README.md ./

# -------------------------
# 2. 최소한 setup에 필요한 소스 디렉토리 복사
# -------------------------
COPY api ./api
COPY core ./core
COPY models ./models
COPY services ./services
COPY repositories ./repositories
COPY schemas ./schemas

# -------------------------
# 3. 가상환경 생성 + 의존성 설치
# -------------------------
RUN uv venv /opt/venv \
&& . /opt/venv/bin/activate \
&& uv sync --frozen --no-dev

ENV PATH="/opt/venv/bin:${PATH}"

# -------------------------
# 4. 나머지 애플리케이션 전체 복사
# -------------------------
COPY . .

EXPOSE 8000

# 엔트리포인트 (main.py 안에 FastAPI app 가정)
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
