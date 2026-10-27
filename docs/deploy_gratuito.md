# Demonstracao gratuita: Vercel + Render + Neon

Configuracao preparada para demonstracao; publicacao e acesso real aos provedores ainda precisam
ser realizados. Confira nos provedores a oferta, elegibilidade e limites atuais antes de criar recursos.
Nao ative planos pagos, upgrade automatico ou recursos cobrados para seguir este roteiro.

## Limites desta versao

- A API gratuita pode suspender por inatividade; a primeira requisicao pode demorar ou precisar ser repetida.
- Contratos, usuarios e demais registros ficam no PostgreSQL externo, dentro dos limites do Neon.
- PDFs, anexos e relatorios locais sao temporarios: podem desaparecer apos reinicio ou deploy.
  Nao use para documentos reais ou dados sem copia. Armazenamento duravel externo fica pendente.
- Sem Redis, worker ou beat: importacoes executam na requisicao, adequadas a planilhas pequenas.
  Alertas de vencimento podem ser gerados por administrador em POST /api/v1/alertas/gerar-vencimentos;
  nao existe agendamento diario nesta configuracao. A importacao XLS/XLSX da tela tambem e sincrona.
- Envio de e-mails nao esta configurado. Nao ha garantia de disponibilidade para uso operacional.

## 1. Banco no Neon

Em https://neon.tech crie um projeto no plano gratuito. Copie a connection string PostgreSQL
com SSL exigido (sslmode=require). Guarde-a apenas nas variaveis privadas do Render; nao publique
em chat, Git ou no frontend. URLs postgres:// e postgresql:// sao convertidas para o driver psycopg.

## 2. API no Render

As alteracoes deste checkout precisam estar no GitHub antes de importar o Blueprint.
Em https://dashboard.render.com use New > Blueprint e selecione SilvaJuniorIS/fiscalbot.
O render.yaml define somente um Web Service Docker no plano free; nenhum banco pago ou worker.
Se o plano free nao estiver disponivel para sua conta, interrompa em vez de contratar outro.

Preencha no painel seguro:

| Variavel | Valor |
| --- | --- |
| DATABASE_URL | Connection string privada do Neon, com SSL |
| ADMIN_EMAIL | Seu e-mail de administrador |
| ADMIN_PASSWORD | Senha exclusiva de 12 a 72 bytes; nao use a senha demo |
| SECRET_KEY | Gerada automaticamente pelo Blueprint |
| FRONTEND_URL | https://fiscalbot-isj.vercel.app (ajuste se o dominio mudar) |

O inicio aplica migracoes e cria somente o administrador, sem dados/senhas demo.
Reinicios preservam a senha de um administrador existente; mudar ADMIN_PASSWORD nao a redefine.
A rota publica /run-seed foi removida. Nao execute scripts/seed.py nesse banco publico.

Copie o dominio HTTPS gerado pelo Render. Verifique /health: deve retornar status ok.
Nao coloque /api/v1 no final de VITE_API_URL; as chamadas do frontend ja incluem esse prefixo.

## 3. Frontend na Vercel

No projeto fiscalbot-isj, Root Directory = fiscalbot-web, Build Command = npm run build,
Output Directory = dist. Em Environment Variables defina VITE_API_URL com a URL HTTPS da API
do Render, sem barra final e sem /api/v1. Selecione Production e faca Redeploy.
VITE_API_URL e publica: nunca inclua a conexao do banco, SECRET_KEY ou senha nela.

## 4. Validacao apos publicar

Abra https://fiscalbot-isj.vercel.app e entre com ADMIN_EMAIL e a senha escolhida.
Confira listagem/cadastro de contrato, importacao de planilha pequena e geracao manual de alertas.
Teste upload/download somente com arquivos descartaveis. Recarregue uma rota React diretamente.
Se login falhar, confira logs do Render, URL da API e FRONTEND_URL antes de mudar credenciais.

## Verificacao local

Na raiz, com dependencias de desenvolvimento instaladas:

```bash
STORAGE_PATH=/tmp/fiscalbot-test-storage .venv/bin/python -m pytest tests/ -q
```

As contas dos provedores e publicacao externa nao sao validadas por esses testes.
