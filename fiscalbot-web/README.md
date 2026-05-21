# FiscalBot Web

Frontend React (Vite + TypeScript + Tailwind) para a API FiscalBot.

## Desenvolvimento

```bash
npm install
cp .env.example .env   # ou use .env com VITE_API_URL=http://localhost:8000
npm run dev
```

Acesse http://localhost:5173 — o proxy encaminha `/api` para a API em `:8000`.

## Login demo

Use as credenciais criadas por `make seed` na raiz do monorepo (ex.: `admin@fiscalbot.gov.br` / `fiscalbot123`).
