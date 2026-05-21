# Manual do FiscalBot

## 1. Objetivo

O FiscalBot é uma plataforma para gestão, fiscalização e inteligência de contratos públicos.
Nesta versão inicial, o sistema entrega:

- painel executivo de contratos;
- API de cadastro e consulta de contratos;
- base de dados modelada para fornecedores, secretarias, alertas, anexos, ocorrências e logs;
- documentação técnica automática via Swagger;
- ambiente local com PostgreSQL e Redis via Docker.

## 2. Como acessar

Com o servidor iniciado, acesse:

- Dashboard: `http://127.0.0.1:8010/`
- Documentação da API: `http://127.0.0.1:8010/docs`
- Status da aplicação: `http://127.0.0.1:8010/health`
- Dados do dashboard: `http://127.0.0.1:8010/api/v1/dashboard`

## 3. Como iniciar o ambiente

No PowerShell, dentro de `C:\FiscalBot`:

```powershell
.\.venv\Scripts\activate
docker compose up -d postgres redis
.\.venv\Scripts\alembic upgrade head
.\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Se a porta `8010` estiver ocupada, use outra porta:

```powershell
.\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8020
```

## 4. Dashboard

O dashboard mostra os principais indicadores do MVP:

- contratos cadastrados;
- contratos ativos;
- contratos vencendo em 30 dias;
- contratos vencendo em 90 dias;
- valor total contratado;
- alertas pendentes;
- ocorrências abertas;
- fornecedores cadastrados;
- contratos por secretaria;
- próximos vencimentos.

Quando o banco ainda não está acessível, o dashboard entra em modo demonstração. Isso permite apresentar a tela sem depender de dados reais.

## 5. Cadastro de contratos pela API

Acesse `http://127.0.0.1:8010/docs` e abra o grupo `contratos`.

Endpoints disponíveis:

- `GET /api/v1/contratos`: listar contratos;
- `POST /api/v1/contratos`: cadastrar contrato;
- `GET /api/v1/contratos/{contrato_id}`: consultar contrato;
- `PATCH /api/v1/contratos/{contrato_id}`: atualizar contrato;
- `DELETE /api/v1/contratos/{contrato_id}`: excluir contrato.

Cadastros auxiliares disponíveis:

- `GET/POST/PATCH/DELETE /api/v1/secretarias`;
- `GET/POST/PATCH/DELETE /api/v1/fornecedores`;
- `GET/POST/PATCH/DELETE /api/v1/users`.
- `GET/PATCH /api/v1/alertas`;
- `POST /api/v1/alertas/gerar-vencimentos`.

Exemplo de payload para criação:

```json
{
  "numero": "001/2026",
  "orgao": "Prefeitura Municipal",
  "objeto": "Prestação de serviços de limpeza predial",
  "valor": 250000.00,
  "inicio": "2026-01-01",
  "termino": "2026-12-31",
  "status": "ativo",
  "tags": "limpeza,servicos-continuados",
  "secretaria_id": 1,
  "fornecedor_id": 1,
  "fiscal_responsavel_id": 1,
  "gestor_responsavel_id": 1
}
```

Antes de criar contratos, é necessário existir secretaria, fornecedor e usuários relacionados no banco. Esses cadastros já estão disponíveis na API.

## 6. Dados de demonstração

Com o PostgreSQL ativo e as migrations aplicadas, rode:

```powershell
.\.venv\Scripts\python scripts\seed_demo_data.py
```

O script cria secretarias, fornecedores, usuários, contratos e alertas de vencimento. Ele é idempotente: pode ser executado mais de uma vez sem duplicar os registros principais.

## 7. Motor de alertas

O primeiro motor de alertas gera avisos automáticos de vencimento para contratos ativos nas janelas:

- 180 dias;
- 90 dias;
- 60 dias;
- 30 dias.

Para executar manualmente:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8010/api/v1/alertas/gerar-vencimentos
```

Para listar pendências:

```powershell
Invoke-RestMethod http://127.0.0.1:8010/api/v1/alertas?status=pendente
```

## 8. Estrutura técnica

Principais diretórios:

- `app/api`: rotas da API;
- `app/core`: configurações centrais;
- `app/db`: conexão com banco;
- `app/models`: modelos SQLAlchemy;
- `app/schemas`: schemas Pydantic;
- `app/services`: regras de negócio e consultas agregadas;
- `app/web`: páginas HTML servidas pelo backend;
- `migrations`: migrações Alembic;
- `docs`: documentação operacional.

## 9. Próxima sprint recomendada

A próxima etapa lógica é completar o fluxo operacional mínimo:

1. agendamento recorrente do motor de alertas via Celery;
2. gestão documental com upload;
3. autenticação e perfis de acesso;
4. histórico de auditoria para alterações críticas;
5. tela de cadastro de contratos no frontend.

Com isso, o FiscalBot deixa de ser apenas base técnica e passa a operar o ciclo completo de cadastro, acompanhamento e alerta.
