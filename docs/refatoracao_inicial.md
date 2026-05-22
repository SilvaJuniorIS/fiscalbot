# Refatoracao inicial do FiscalBot

## Objetivo

Auditar e padronizar a base fullstack antes da evolucao funcional, mantendo a arquitetura atual com FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, Celery, React, Vite, TypeScript e Docker Compose.

## Correcoes aplicadas

- `requirements.txt` foi recriado para refletir dependencias reais usadas pelo backend em container.
- `docker-compose.yml` agora sobe banco, Redis, API, worker, beat e frontend.
- Dependencias do Docker alinhadas ao `pyproject.toml`, incluindo `email-validator`, `bcrypt`, `psycopg[binary]`, `sqlalchemy` e `uvicorn[standard]`.
- `app.models.__init__` passou a exportar todos os modelos declarados, incluindo `Indicador` e `LogAuditoria`.
- Relacionamentos SQLAlchemy foram completados com `back_populates` para ocorrencias fiscalizadas, anexos enviados e logs de auditoria.
- Schemas de contrato passaram a aceitar aliases legados (`fiscal_id`, `gestor_id`, `data_inicio`, `data_termino`) sem abandonar os nomes padronizados em portugues (`fiscal_responsavel_id`, `gestor_responsavel_id`, `inicio`, `termino`).
- Filtro de contratos foi padronizado internamente para `fiscal_responsavel_id`, mantendo compatibilidade da rota com o parametro `fiscal_id`.
- API recebeu handlers globais para registrar erros de validacao e excecoes inesperadas com contexto de metodo e rota.
- Docker Compose passou a executar `alembic upgrade head` antes de iniciar API, worker e beat, evitando tarefas Celery contra tabelas ainda inexistentes.
- Docker Compose passou a incluir o frontend Vite em `http://localhost:5173`, com `node_modules` isolado em volume nomeado.
- Scripts de seed passaram a incluir a raiz do projeto no `sys.path`, permitindo execucao direta com `python scripts/seed.py`.
- Textos corrompidos por encoding em alerta/e-mail/detalhe de contrato foram normalizados.

## Padrao adotado

- Datas de contrato: `inicio` e `termino`.
- Responsaveis do contrato: `fiscal_responsavel_id` e `gestor_responsavel_id`.
- Compatibilidade externa: aliases antigos continuam aceitos em payloads para evitar quebra de clientes existentes.

## Pontos de atencao

- A primeira migracao cria `users.hashed_password` apenas na revisao seguinte como coluna inicialmente nullable; isso preserva compatibilidade com bancos ja migrados.
- O frontend ja consome `inicio` e `termino`; os tipos foram mantidos nesse padrao.
- Os textos ainda podem receber uma rodada posterior de acentuacao completa, mas a base tecnica foi normalizada sem alterar funcionalidades.

## Validacao recomendada

```bash
docker compose up --build
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed.py
curl http://localhost:8000/health
```

Tambem validar:

- `http://localhost:8000/docs`
- Login com usuario seed.
- Dashboard.
- Listagem e detalhe de contratos.

## Validacao executada

- `docker compose up --build -d --force-recreate`: containers subiram.
- `docker compose exec -T api alembic upgrade head`: sem erros.
- `docker compose exec -T api alembic current`: `20260519_0003 (head)`.
- `docker compose exec -T api python scripts/seed.py`: seed concluido.
- `GET /health`: 200.
- `GET /docs`: 200.
- `GET http://localhost:5173`: 200.
- `docker compose exec -T frontend npm run build`: TypeScript e Vite build sem erro.
- Login admin + `GET /api/v1/contratos/dashboard`: 200.
- Login admin + `GET /api/v1/contratos`: 200, retornando 24 contratos.
- Logs do ciclo atual pesquisados por `Traceback`, `ERROR`, `UndefinedTable` e `ModuleNotFoundError`: nenhuma ocorrencia.

## Arquivos corrigidos

- `app/api/v1/routes/contratos.py`
- `app/main.py`
- `app/models/__init__.py`
- `app/models/anexo.py`
- `app/models/log_auditoria.py`
- `app/models/ocorrencia.py`
- `app/models/user.py`
- `app/repositories/contrato_repository.py`
- `app/schemas/contrato.py`
- `app/services/alerta_service.py`
- `app/services/email_service.py`
- `docker-compose.yml`
- `fiscalbot-web/src/pages/ContratoDetalhe.tsx`
- `requirements.txt`
- `scripts/seed.py`
- `scripts/seed_demo_data.py`
