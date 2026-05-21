.PHONY: dev build migrate seed test logs down frontend

dev:
	docker compose up --build -d

build:
	docker compose build

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python scripts/seed.py

test:
	docker compose exec api pytest tests/ -q

logs:
	docker compose logs -f api

down:
	docker compose down

frontend:
	cd fiscalbot-web && npm install && npm run dev
