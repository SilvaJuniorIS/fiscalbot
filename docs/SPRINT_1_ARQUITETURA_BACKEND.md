# Sprint 1 - Modelagem do banco e arquitetura backend

## Objetivo

Estabelecer a base tecnica do FiscalBot para sustentar o MVP de gestao contratual, alertas, documentos, dashboard e auditoria.

## Stack definida

- API: FastAPI
- ORM: SQLAlchemy 2
- Schemas: Pydantic
- Banco principal: PostgreSQL
- Migracoes: Alembic
- Jobs futuros: Redis + Celery
- Empacotamento local: `pyproject.toml`

## Estrutura backend

```text
app/
  api/v1/routes/      Endpoints REST por dominio
  core/               Configuracoes da aplicacao
  db/                 Engine, sessao e metadata
  models/             Entidades SQLAlchemy
  schemas/            Contratos de entrada/saida da API
  services/           Regras de negocio e agregacoes
  web/                Dashboard HTML inicial
migrations/           Historico Alembic
scripts/              Rotinas operacionais e seeds
tests/                Testes automatizados
```

## Modelo de dados inicial

```mermaid
erDiagram
    SECRETARIAS ||--o{ CONTRATOS : possui
    FORNECEDORES ||--o{ CONTRATOS : executa
    USERS ||--o{ CONTRATOS : fiscaliza
    USERS ||--o{ CONTRATOS : gere
    CONTRATOS ||--o{ ANEXOS : contem
    CONTRATOS ||--o{ ALERTAS : gera
    CONTRATOS ||--o{ OCORRENCIAS : registra
    USERS ||--o{ LOGS : executa

    USERS {
        int id
        string nome
        string email
        string role
        bool is_active
    }

    SECRETARIAS {
        int id
        string nome
        string sigla
        bool is_active
    }

    FORNECEDORES {
        int id
        string razao_social
        string cnpj
        string email
        string telefone
        bool is_active
    }

    CONTRATOS {
        int id
        string numero
        string orgao
        text objeto
        numeric valor
        date inicio
        date termino
        string status
        text tags
    }

    ANEXOS {
        int id
        int contrato_id
        string tipo
        string nome_arquivo
        string caminho_storage
        int versao
        text texto_ocr
    }

    ALERTAS {
        int id
        int contrato_id
        string tipo
        string titulo
        date data_referencia
        string status
        datetime enviado_em
    }

    OCORRENCIAS {
        int id
        int contrato_id
        string titulo
        text descricao
        date data_ocorrencia
        string status
        numeric latitude
        numeric longitude
    }

    LOGS {
        int id
        int user_id
        string entidade
        int entidade_id
        string acao
        json antes
        json depois
    }
```

## Endpoints iniciais

- `GET /health`
- `GET /api/v1/dashboard`
- CRUD de `secretarias`
- CRUD de `fornecedores`
- CRUD de `users`
- CRUD de `contratos`
- Listagem de `alertas`

## Regras estruturais da Sprint 1

- Contratos nao podem ter valor negativo.
- Contratos nao podem terminar antes da data de inicio.
- Indicadores nao podem ter valor negativo.
- Coordenadas de ocorrencias devem respeitar latitude entre -90 e 90 e longitude entre -180 e 180.
- Chaves unicas principais: numero do contrato, CNPJ do fornecedor, email do usuario e nome da secretaria.

## Proximas decisoes tecnicas

- Definir autenticacao JWT e politica de perfis.
- Separar regras de auditoria em middleware/service.
- Criar endpoints de upload para anexos.
- Implementar gerador de alertas com Celery.
- Adicionar testes com banco isolado para CRUD e migracoes.
