# Saneamento de contratos e atas

## Alteracoes e publicacao

A migracao `20261027_0006` adiciona `tipo` e identifica como ata os numeros existentes
que comecam com `ATA `, ignorando maiusculas/minusculas e espacos externos. Os demais
registros recebem `contrato`. IDs, numeros, datas, valores e observacoes sao preservados.
A inicializacao existente no Render aplica a migracao antes de iniciar a API.
Publique backend e frontend do mesmo commit; aguarde ambos os deploys antes de importar.
A disponibilidade externa precisa ser confirmada no painel dos provedores.

Nenhum registro e excluido ou fundido automaticamente. O painel sinaliza grupos de
possiveis duplicados para revisao manual. Dados ausentes nao sao inventados.
A migracao nao transfere os registros das tabelas legadas de fiscalizacao/contratos.
O dashboard e a listagem principal usam `contracts`, a mesma fonte da importacao XLS/XLSX.

## Importacao

1. Selecione a primeira aba do arquivo XLS/XLSX (limite de 10 MB).
2. Use a coluna `Tipo` com `contrato` ou `ata`. Sem ela, o prefixo `ATA ` ou o cabecalho
   `Ata` identifica atas. O restante e tratado como contrato; o tipo pode ser editado depois.
3. Clique em **Analisar planilha**. A previa nao grava contratos nem logs de importacao.
   Exibe ate 50 linhas; contadores consideram a primeira aba inteira.
4. Confira os erros e confirme a importacao das linhas validas.

O padrao e ignorar duplicados. A identidade conservadora compara tipo, numero sem
prefixo ATA, CNPJ (ou fornecedor quando ausente), secretaria e aditivo.
Comparacoes ignoram acentos, caixa e separadores. Campos diferentes podem representar
instrumentos diferentes e nao sao fundidos por aproximacao. Edite inconsistencias
antes de reimportar; numero e fornecedor sao exigidos para novos registros.
Repeticoes na mesma planilha sao ignoradas apos a primeira linha valida.

No modo **Atualizar**, somente uma correspondencia inequivoca existente e alterada.
Celulas vazias e status administrativo existentes sao preservados. Se houver mais de
uma correspondencia, a linha e ignorada para revisao. Alteracao de vencimento reinicia
as marcacoes de alerta do registro; nao ativa um agendador.
Importacoes concorrentes em PostgreSQL sao serializadas por um lock de transacao.
A confirmacao reavalia duplicados; seus totais podem diferir da previa caso outros
usuarios alterem a base no intervalo.

Datas ou valores preenchidos mas invalidos sao relatados por linha, sem virar valores
inventados. Campos realmente vazios continuam vazios e aparecem como pendencias.

## Vencimentos e pendencias

A situacao e calculada na consulta, sem depender de Redis/Celery. `suspenso`, `encerrado`
e `cancelado` prevalecem; os demais sao classificados em sem vencimento, vencido,
vencendo (hoje ate 30 dias, inclusive) ou ativo. O status administrativo original
permanece separado, sem reescrita automatica.

Dias restantes e exportacoes usam o vencimento atual, nao o numero em cache no banco.
O painel conta contratos e atas, agrupa por situacao, exibe ate 10 prioridades e ate
20 registros em grupos duplicados. O filtro de dados incompletos encontra ausencia de
numero, fornecedor, secretaria, objeto, vencimento, valor, gestor ou fiscal. Valor zero
nao e considerado ausente. Estes sao indicadores de revisao, nao validacao juridica.

Os limites da versao gratuita continuam: documentos temporarios, API sujeita a suspensao
por inatividade e ausencia de agendamento continuo. Nenhum servico pago foi adicionado.
