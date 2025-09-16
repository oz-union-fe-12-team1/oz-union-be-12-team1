## 시작하기 (Docker + Tortoise ORM + Aerich)

### 1) 저장소 클론
```bash
git clone <REPO_URL>
cd oz-union-be-12-team1
```

### 3) Docker로 서비스 기동
```bash
docker compose up -d --build
```

### 4) DB 마이그레이션 (Aerich)
컨테이너 안에서 Tortoise ORM 설정(`core.db.TORTOISE_ORM`)을 사용해 Aerich을 초기화하고 마이그레이션을 적용합니다.
```bash
docker compose exec api uv run aerich init -t core.db.TORTOISE_ORM
docker compose exec api uv run aerich init-db
docker compose exec api uv run aerich migrate
docker compose exec api uv run aerich upgrade
```

### 5) 서버 접속
- 로컬 브라우저: `http://localhost:8000/`
- 문서: `http://localhost:8000/docs`

### 6) 참고 사항
- Tortoise ORM 연결 및 라이프사이클은 `core/db.py`, `main.py`에 구성되어 있습니다.
- 모델이 Tortoise 기반으로 정리되는 중입니다. 마이그레이션 전, 변경된 모델을 반영하세요.
