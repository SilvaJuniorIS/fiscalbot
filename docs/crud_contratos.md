# CRUD de contratos

## Endpoints finais

- `GET /api/v1/contratos`
- `GET /api/v1/contratos/{id}`
- `POST /api/v1/contratos`
- `PUT /api/v1/contratos/{id}`
- `DELETE /api/v1/contratos/{id}`

## Listagem

Suporta:

- `page`
- `limit`
- `numero`
- `q`
- `status`
- `secretaria_id`
- `fornecedor_id`
- `fiscal_id`
- `vencendo_em_dias`
- `order_by`
- `order_dir`
- `formato=lista|pagina`

Por padrao, retorna lista para manter compatibilidade. Tambem envia `X-Total-Count`, `X-Page` e `X-Limit`.

## Permissoes

- `admin`: cria, edita, exclui e visualiza todos os contratos.
- `gestor`: cria e edita contratos da propria secretaria quando e o gestor responsavel.
- `fiscal` e `auditor`: visualizam conforme escopo.

## Fluxo frontend

1. Usuario acessa `Contratos`.
2. Usa filtros rapidos, busca textual, ordenacao e paginacao.
3. Clica em `Novo Contrato` para criar.
4. Clica em um contrato para visualizar detalhes.
5. Clica em `Editar` para atualizar.
6. Admin pode excluir com modal de confirmacao.
7. Operacoes exibem toast de sucesso ou erro e atualizam a lista automaticamente.
