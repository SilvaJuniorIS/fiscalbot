# Importacao massiva de contratos

## Formato aceito

Arquivos `.csv` e `.xlsx` com as colunas:

```text
numero
orgao
objeto
valor
inicio
termino
secretaria
fornecedor
cnpj
fiscal_email
gestor_email
status
```

As colunas `fiscal_email`, `gestor_email` e `status` sao opcionais. Datas aceitam `YYYY-MM-DD`, `DD/MM/YYYY` ou `DD-MM-YYYY`.

## Endpoint

```http
POST /api/v1/importacao/contratos?modo=append
Content-Type: multipart/form-data
```

Modos:

- `append`: ignora contratos duplicados pelo numero.
- `overwrite`: atualiza contratos existentes pelo numero.

Resposta:

```json
{
  "task_id": "uuid-da-task",
  "status": "queued"
}
```

## Consulta de status

```http
GET /api/v1/importacao/contratos/{task_id}
```

Quando finalizada, a resposta inclui:

- `importados`
- `ignorados`
- `erros`
- `atualizados`
- `linhas_invalidas`
- `detalhes`

## Relatorio CSV

```http
GET /api/v1/importacao/contratos/{task_id}/relatorio.csv
```

## Template

O arquivo exemplo esta em `examples/contratos_importacao.csv` e tambem pode ser baixado pela interface.

## Fluxo completo

1. Usuario escolhe `append` ou `overwrite`.
2. Usuario envia `.csv` ou `.xlsx`.
3. API salva o arquivo e agenda uma task Celery.
4. Worker processa linha a linha sem interromper a importacao em caso de erro.
5. Secretarias e fornecedores ausentes sao criados automaticamente.
6. Duplicidades por numero sao ignoradas ou atualizadas conforme o modo.
7. Relatorio final fica disponivel para visualizacao e download.
