# FiscalBot

Plataforma GovTech para gestao, fiscalizacao e inteligencia de contratos publicos.

## Pre-requisitos

- Docker e Docker Compose **ou**
- Python 3.11+, PostgreSQL 15, Redis 7 (para desenvolvimento local)

## Inicio rapido (Windows)

Duplo clique em **`iniciar-fiscalbot.bat`** (sobe Docker, migra, seed, frontend e abre o navegador).

Para parar: **`parar-fiscalbot.bat`**

Requisitos: [Docker Desktop](https://www.docker.com/products/docker-desktop/) em execucao e [Node.js](https://nodejs.org/) para o frontend.

## Inicio rapido (Docker / terminal)

```bash
cp .env.example .env
make dev
make migrate
make seed
```

| Servico | URL |
|---------|-----|
| API | http://localhost:8000 |
| Documentacao OpenAPI | http://localhost:8000/docs |
| Frontend (opcional) | http://localhost:5173 |

### Credenciais padrao (apos `make seed`)

| Perfil | E-mail | Senha |
|--------|--------|-------|
| Admin | admin@fiscalbot.gov.br | fiscalbot123 |
| Gestor | gestor@fiscalbot.local | fiscalbot123 |
| Fiscal | fiscal@fiscalbot.local | fiscalbot123 |

## Frontend React

```bash
make frontend
# ou: cd fiscalbot-web && npm install && npm run dev
```

Configure `fiscalbot-web/.env` com `VITE_API_URL=http://localhost:8000`.

## Desenvolvimento local (sem Docker)

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e ".[dev]"
# Suba Postgres e Redis, ajuste DATABASE_URL no .env
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

## Perfis de usuario

- **admin** — acesso total, usuarios, auditoria, exclusao de contratos
- **gestor** — contratos da secretaria, edita contratos onde e responsavel
- **fiscal** — fiscalizacao e visualizacao no escopo da secretaria
- **auditor** — leitura ampla e trilha de auditoria

## Comandos Make

| Comando | Descricao |
|---------|-----------|
| `make dev` | Sobe postgres, redis, api, worker e beat |
| `make migrate` | Aplica migracoes Alembic |
| `make seed` | Dados de demonstracao |
| `make test` | Executa pytest no container |
| `make logs` | Logs da API |
| `make down` | Para os containers |

## Testes

```bash
pytest tests/ -v
```

## Modulos

- Contratos com status automatico por vencimento
- Alertas (Celery + endpoint manual `/alertas/gerar-vencimentos`)
- Documentos (upload PDF, imagens, ZIP, DOCX)
- Fiscalizacao (ocorrencias por contrato)
- Auditoria (logs — apenas admin)

## Producao

```bash
cp .env.example .env.prod   # ajuste segredos
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```
