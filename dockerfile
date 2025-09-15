# ---- Base image --------------------------------------------------------------
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_SYSTEM_PYTHON=1

# 시스템 패키지 (빌드/런타임용)
# - libpq: psycopg 사용 시 필요(바이너리 사용하면 대부분은 OK지만 안전하게 포함)
# - curl/ca-certificates: uv 설치 스크립트 및 HTTPS 필요
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# uv 설치 (공식 스크립트)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# 비루트 유저
RUN useradd -ms /bin/bash appuser
WORKDIR /app

# ---- Dependency layer (캐시 최적화) -----------------------------------------
# 프로젝트 메타만 먼저 복사 → 의존성 캐시
COPY pyproject.toml uv.lock* ./

# venv를 /opt/venv 로 만들고 동결된 버전으로 설치
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv sync --frozen --no-dev

# 실행 시 venv가 우선되도록 PATH 구성
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# ---- App layer ---------------------------------------------------------------
# 실제 애플리케이션 코드 복사
COPY app ./app

# 포트 공개
EXPOSE 8000

# 권한 전환
USER appuser

# 헬스체크(선택)
# HEALTHCHECK CMD curl -fsS http://localhost:8000/health || exit 1

# 실행 커맨드: uv를 통해 uvicorn 실행
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
