# FiscalBot — Prompts Sequenciais para o Codex

Execute cada bloco **em ordem**, um por vez, esperando o Codex concluir antes de passar ao próximo.
Cada prompt é autossuficiente — cole exatamente como está.

---

## SPRINT 0 — Estrutura base do projeto

```
Crie um projeto Python chamado "fiscalbot" com a seguinte estrutura de pastas:

fiscalbot/
  app/
    models/
    schemas/
    routes/
    services/
    repositories/
    core/
    __init__.py
    main.py
  tests/
  .env.example
  .gitignore
  requirements.txt
  docker-compose.yml
  Dockerfile

Requisitos:
- Framework: FastAPI
- Banco de dados: PostgreSQL com SQLAlchemy (async) e Alembic para migrações
- Autenticação: JWT com python-jose e passlib[bcrypt]
- Variáveis de ambiente: pydantic-settings
- Servidor: uvicorn

No requirements.txt inclua:
fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic,
python-jose[cryptography], passlib[bcrypt], pydantic-settings,
python-multipart, aiofiles, redis, celery

No .env.example inclua as variáveis:
DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,
REDIS_URL, FRONTEND_URL

No docker-compose.yml suba três serviços: api, postgres e redis.

No main.py configure o app FastAPI com título "FiscalBot API", versão "1.0.0",
inclua CORS liberado para o FRONTEND_URL do .env, e importe todos os routers
dos módulos que vamos criar a seguir.
```

---

## SPRINT 1 — Banco de dados: modelos e migrações

```
No projeto fiscalbot, crie os modelos SQLAlchemy em app/models/ com os seguintes arquivos:

1. base.py
   - Classe Base com coluna id (UUID, primary key, default uuid4),
     created_at e updated_at (DateTime, com timezone, auto-gerenciados)

2. user.py — modelo User
   Campos: id, name, email (único), hashed_password, role (enum: admin, gestor, fiscal, viewer),
   secretaria_id (FK opcional), is_active (bool, default True),
   created_at, updated_at

3. secretaria.py — modelo Secretaria
   Campos: id, name, sigla, created_at

4. fornecedor.py — modelo Fornecedor
   Campos: id, razao_social, cnpj (único), email, telefone, created_at

5. contrato.py — modelo Contrato
   Campos: id, numero (único, string), objeto, valor (Numeric 14,2),
   data_inicio (Date), data_termino (Date), secretaria_id (FK),
   fornecedor_id (FK), fiscal_id (FK → User), gestor_id (FK → User),
   status (enum: rascunho, ativo, alerta, critico, encerrado),
   created_by (FK → User), created_at, updated_at

6. anexo.py — modelo Anexo
   Campos: id, contrato_id (FK), filename, filepath, tipo
   (enum: contrato, aditivo, nota_fiscal, relatorio, foto, notificacao, ata),
   versao (string), uploaded_by (FK → User), created_at

7. alerta.py — modelo Alerta
   Campos: id, contrato_id (FK), tipo
   (enum: vencimento_180, vencimento_90, vencimento_60, vencimento_30,
   reajuste_anual, certidao_vencendo, sla_descumprido, pendencia_documental),
   descricao, lido (bool, default False), resolvido (bool, default False),
   criado_em (DateTime)

8. ocorrencia.py — modelo Ocorrencia
   Campos: id, contrato_id (FK), fiscal_id (FK → User), descricao,
   tipo (enum: vistoria, notificacao, pendencia, aceite_parcial),
   status (enum: aberta, em_andamento, concluida),
   data_registro, created_at

9. log.py — modelo Log
   Campos: id, user_id (FK → User), acao, tabela, registro_id (UUID),
   dados_anteriores (JSON), dados_novos (JSON), criado_em (DateTime)

Configure todas as relações com back_populates.
Crie app/models/__init__.py importando todos os modelos.
Configure o engine async em app/core/database.py com get_db como dependency.
Inicialize o Alembic com alembic init alembic e configure alembic.ini
para usar o DATABASE_URL do .env.
Gere a primeira migração: alembic revision --autogenerate -m "initial_schema"
```

---

## SPRINT 2 — Autenticação e usuários

```
No projeto fiscalbot, implemente autenticação completa:

1. app/core/security.py
   - Funções: hash_password, verify_password, create_access_token, decode_token
   - Token JWT com expiração configurável via .env

2. app/schemas/user.py
   - UserCreate: name, email, password, role, secretaria_id
   - UserOut: id, name, email, role, secretaria_id, is_active (sem senha)
   - UserUpdate: name, role, secretaria_id, is_active (todos opcionais)
   - Token: access_token, token_type
   - TokenData: email

3. app/repositories/user_repository.py
   - get_by_id, get_by_email, create, update, deactivate, list_all

4. app/services/auth_service.py
   - authenticate_user(email, password) → User | None
   - get_current_user(token) → User (dependency FastAPI)
   - require_role(*roles) → dependency que verifica se o usuário tem o perfil exigido

5. app/routes/auth.py
   - POST /auth/login → retorna JWT (form com username e password)
   - GET  /auth/me    → retorna o usuário autenticado

6. app/routes/users.py
   - GET    /users         → lista usuários (apenas admin)
   - POST   /users         → cria usuário (apenas admin)
   - GET    /users/{id}    → detalhe (admin ou próprio usuário)
   - PUT    /users/{id}    → edita perfil (apenas admin)
   - DELETE /users/{id}    → desativa conta (apenas admin)

Implemente a lógica de escopo por secretaria:
fiscais e gestores só veem contratos da sua secretaria_id.
Administradores veem tudo.
Crie a dependency get_scoped_secretaria_ids(current_user) que retorna
a lista de secretaria_ids permitidas para o usuário.

Escreva testes em tests/test_auth.py cobrindo:
login com credenciais válidas, login inválido,
acesso com token expirado, acesso sem token.
```

---

## SPRINT 3 — Módulo de Contratos

```
No projeto fiscalbot, implemente o módulo de contratos completo:

1. app/schemas/contrato.py
   - ContratoCreate: todos os campos obrigatórios do modelo
   - ContratoUpdate: todos os campos opcionais
   - ContratoOut: todos os campos + relações aninhadas
     (fornecedor: FornecedorOut, fiscal: UserOut, gestor: UserOut,
      secretaria: SecretariaOut, alertas_ativos: int)
   - ContratoFiltros: numero, status, secretaria_id,
     fornecedor_id, fiscal_id, vencendo_em_dias

2. app/repositories/contrato_repository.py
   - get_by_id, create, update, delete
   - list_with_filters(filtros, secretaria_ids_permitidas)
     — aplica filtro de escopo automaticamente
   - count_by_status() → dict com contagens por status
   - get_vencendo(dias: int) → contratos com data_termino
     nos próximos N dias

3. app/services/contrato_service.py
   - Toda regra de negócio: ao salvar, calcular status automático
     baseado na data_termino:
     · > 60 dias → ativo
     · 31–60 dias → alerta
     · ≤ 30 dias → critico
     · passado → encerrado
   - Ao criar ou editar, registrar log via log_service.registrar()

4. app/routes/contratos.py
   - GET    /contratos           → lista com filtros e paginação (page, limit)
   - POST   /contratos           → cria (gestor, admin)
   - GET    /contratos/{id}      → detalhe completo
   - PUT    /contratos/{id}      → edita (gestor dono ou admin)
   - DELETE /contratos/{id}      → remove (apenas admin)
   - GET    /contratos/dashboard → retorna:
       { ativos, vencendo_30, valor_total, em_risco,
         por_secretaria: [{nome, total}],
         por_status: [{status, total}] }

Escreva testes em tests/test_contratos.py cobrindo:
criar contrato, listar com filtros, calcular status automático,
tentar editar contrato de outra secretaria (deve retornar 403).
```

---

## SPRINT 4 — Motor de Alertas

```
No projeto fiscalbot, implemente o motor de alertas com Celery:

1. app/core/celery_app.py
   - Configure o Celery com Redis como broker e backend
   - Configure beat_schedule com as tasks abaixo rodando diariamente às 07:00

2. app/services/alerta_service.py
   - verificar_vencimentos(): varre todos contratos ativos e cria alertas
     para os que vencem em 180, 90, 60 e 30 dias (sem duplicar alertas)
   - verificar_reajustes(): cria alerta se data_inicio + 1 ano < hoje
     e não houve aditivo de reajuste registrado
   - marcar_como_lido(alerta_id, user_id)
   - resolver_alerta(alerta_id, user_id)

3. app/tasks/alertas.py
   - task: checar_vencimentos — chama alerta_service.verificar_vencimentos()
   - task: checar_reajustes   — chama alerta_service.verificar_reajustes()
   Ambas logam início, fim e quantidade de alertas gerados.

4. app/routes/alertas.py
   - GET  /alertas              → lista alertas do usuário (com filtro lido/resolvido)
   - GET  /alertas/resumo       → { urgentes, atencao, info, total_nao_lidos }
   - PUT  /alertas/{id}/lido    → marca como lido
   - PUT  /alertas/{id}/resolver → marca como resolvido

5. Notificações por e-mail (app/services/email_service.py)
   - Função send_alert_email(user_email, alerta) usando smtplib
   - Template simples em texto com: contrato, tipo do alerta, dias restantes
   - Configurar SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS no .env

Escreva testes em tests/test_alertas.py cobrindo:
geração correta de alerta para contrato vencendo em 25 dias,
não duplicação de alerta já existente,
marcar alerta como lido.
```

---

## SPRINT 5 — Gestão Documental

```
No projeto fiscalbot, implemente o módulo de documentos:

1. app/core/storage.py
   - Função save_file(file: UploadFile, subfolder: str) → filepath
     salva em /storage/{subfolder}/{uuid}_{filename}
   - Função delete_file(filepath: str)
   - Função get_file_url(filepath: str) → URL relativa para download

2. app/schemas/anexo.py
   - AnexoOut: id, filename, tipo, versao, uploaded_by (UserOut), created_at, url

3. app/services/anexo_service.py
   - upload(contrato_id, file, tipo, versao, user) → AnexoOut
     Valida extensão permitida: pdf, jpg, jpeg, png, zip, docx
     Registra log após upload
   - delete(anexo_id, user)
   - list_by_contrato(contrato_id, secretaria_ids_permitidas)

4. app/routes/documentos.py
   - GET    /contratos/{id}/documentos       → lista documentos do contrato
   - POST   /contratos/{id}/documentos       → upload (multipart/form-data)
     campos: file (UploadFile), tipo, versao (opcional)
   - GET    /documentos/{id}/download        → StreamingResponse do arquivo
   - DELETE /documentos/{id}                 → remove arquivo e registro

Escreva testes em tests/test_documentos.py cobrindo:
upload de PDF válido, rejeição de extensão inválida (.exe),
download retorna bytes corretos, deleção remove arquivo do disco.
```

---

## SPRINT 6 — Fiscalização Operacional

```
No projeto fiscalbot, implemente o módulo de fiscalização:

1. app/schemas/ocorrencia.py
   - OcorrenciaCreate: contrato_id, descricao, tipo, anexos (lista de IDs opcional)
   - OcorrenciaUpdate: descricao, status
   - OcorrenciaOut: todos os campos + fiscal (UserOut) + contrato (ContratoOut resumido)

2. app/services/ocorrencia_service.py
   - criar(data, fiscal_id)
   - atualizar_status(ocorrencia_id, novo_status, user)
   - listar_por_contrato(contrato_id, secretaria_ids)
   - resumo_fiscalizacao() → { vistorias_mes, ocorrencias_abertas,
       conformes, com_ressalva, com_pendencia }

3. app/routes/fiscalizacao.py
   - GET  /fiscalizacao/resumo              → indicadores gerais
   - GET  /contratos/{id}/ocorrencias       → lista ocorrências do contrato
   - POST /contratos/{id}/ocorrencias       → registra nova (fiscal, gestor, admin)
   - PUT  /ocorrencias/{id}                 → atualiza status (gestor, admin)
   - GET  /ocorrencias/{id}                 → detalhe com anexos

Escreva testes em tests/test_fiscalizacao.py cobrindo:
fiscal registra ocorrência no próprio contrato,
fiscal não consegue registrar em contrato de outra secretaria (403),
gestor atualiza status para concluída.
```

---

## SPRINT 7 — Logs de Auditoria

```
No projeto fiscalbot, implemente o módulo de auditoria:

1. app/services/log_service.py
   - registrar(user_id, acao, tabela, registro_id, dados_anteriores, dados_novos)
     Cria registro na tabela logs de forma assíncrona (não bloqueia a request)
   - Integre chamadas a log_service.registrar() em todos os services
     já criados: ao criar/editar/excluir contrato, ao fazer upload,
     ao resolver alerta, ao mudar status de ocorrência, ao editar usuário

2. app/schemas/log.py
   - LogOut: id, user (UserOut), acao, tabela, registro_id,
     dados_anteriores, dados_novos, criado_em

3. app/routes/auditoria.py
   - GET /auditoria → lista logs com filtros:
     user_id, tabela, registro_id, data_inicio, data_fim, page, limit
     (apenas admin)
   - GET /auditoria/{registro_id} → histórico completo de um registro específico

Escreva testes em tests/test_auditoria.py cobrindo:
criar contrato gera log com dados corretos,
editar contrato gera log com dados_anteriores preenchidos,
endpoint de auditoria retorna 403 para não-admin.
```

---

## SPRINT 8 — Frontend React

```
Crie um projeto React chamado "fiscalbot-web" usando Vite com TypeScript e Tailwind CSS.

Estrutura de pastas:
src/
  components/
    layout/   (Navbar, Sidebar, Layout)
    ui/       (Button, Badge, Card, Table, Modal, Input)
  pages/
    Login.tsx
    Dashboard.tsx
    Contratos.tsx
    ContratoDetalhe.tsx
    Alertas.tsx
    Fiscalizacao.tsx
    Documentos.tsx
    Usuarios.tsx
  services/
    api.ts       (axios com interceptor de JWT)
    auth.ts
    contratos.ts
    alertas.ts
    documentos.ts
  hooks/
    useAuth.ts
    useContratos.ts
    useAlertas.ts
  store/
    auth.ts      (zustand)
  types/
    index.ts     (interfaces TypeScript de todos os modelos)

Implemente:
1. api.ts: axios com baseURL do VITE_API_URL, interceptor que injeta
   Authorization: Bearer {token} em toda request,
   interceptor de resposta que redireciona para /login em 401

2. useAuth.ts: hook com login(email, password), logout(), user atual,
   isAuthenticated, hasRole(role)

3. Dashboard.tsx: consome GET /contratos/dashboard e exibe:
   4 cards de métricas (ativos, vencendo, valor total, em risco),
   gráfico de barras por secretaria (recharts BarChart),
   gráfico de rosca por status (recharts PieChart),
   tabela com últimos 5 contratos

4. Contratos.tsx: tabela com paginação, filtros por status/secretaria,
   busca por número ou fornecedor, botão de cadastrar novo

5. Alertas.tsx: lista priorizada (urgente → atenção → info),
   botão de marcar como lido, botão de resolver

6. ContratoDetalhe.tsx: todos os campos do contrato, lista de documentos
   com upload inline, lista de ocorrências

Configure .env com VITE_API_URL=http://localhost:8000
```

---

## SPRINT 9 — Docker e deploy final

```
No projeto fiscalbot, finalize a infraestrutura de produção:

1. Atualize o docker-compose.yml para ter 4 serviços:
   - api: FastAPI com uvicorn, porta 8000
   - worker: Celery worker (mesma imagem da api, comando diferente)
   - beat: Celery beat para tasks agendadas
   - postgres: PostgreSQL 15, volume persistente
   - redis: Redis 7, volume persistente

2. Crie docker-compose.prod.yml sobrescrevendo:
   - api com 2 replicas e restart: always
   - variáveis de ambiente vindas de .env.prod (não commitado)

3. Crie um Makefile com os comandos:
   make dev        → sobe docker-compose em modo desenvolvimento
   make build      → rebuild de todas as imagens
   make migrate    → roda alembic upgrade head dentro do container
   make seed       → cria usuário admin padrão (email/senha do .env)
   make test       → roda pytest dentro do container
   make logs       → tail dos logs da api
   make down       → derruba tudo

4. Crie scripts/seed.py que cria:
   - 1 usuário admin: admin@fiscalbot.gov.br / senha do ADMIN_PASSWORD no .env
   - 5 secretarias de exemplo
   - 2 fornecedores de exemplo
   - 3 contratos de exemplo com status variados

5. Crie um README.md completo com:
   - Pré-requisitos (Docker, Docker Compose)
   - Passos de instalação (clone → cp .env.example .env → make dev → make migrate → make seed)
   - Como acessar: API em localhost:8000, docs em localhost:8000/docs
   - Descrição de cada perfil de usuário
   - Como rodar os testes
```

---

## Ordem de execução resumida

| Sprint | O que gera | Tempo estimado |
|--------|-----------|---------------|
| 0 | Estrutura de pastas + Docker base | 5 min |
| 1 | Modelos do banco + migrações | 10 min |
| 2 | Auth JWT + usuários + permissões | 15 min |
| 3 | CRUD de contratos + dashboard | 15 min |
| 4 | Motor de alertas + Celery + e-mail | 15 min |
| 5 | Upload e gestão de documentos | 10 min |
| 6 | Fiscalização e ocorrências | 10 min |
| 7 | Logs de auditoria | 5 min |
| 8 | Frontend React completo | 20 min |
| 9 | Docker produção + Makefile + seed | 10 min |

**Total estimado com Codex:** 1h30–2h de geração supervisionada.

---

## Dicas de uso no Codex

- Cole um bloco de cada vez e aguarde a conclusão antes do próximo.
- Se o Codex perguntar por confirmações, responda "sim, prossiga".
- Após o Sprint 2, rode `make migrate` e `make seed` para testar antes de continuar.
- Após o Sprint 3, acesse `localhost:8000/docs` para ver a API gerada automaticamente pelo FastAPI.
- Se alguma parte falhar, peça: *"corrija os erros do sprint X mantendo a estrutura definida"*.
