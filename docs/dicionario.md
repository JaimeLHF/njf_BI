# Dicionario de dados — schema `bi`

Gerado por `scripts/01_dicionario.py` a partir do catalogo do Postgres (`obj_description` / `col_description`). Descricoes sao as do proprio banco; onde estao vazias, o banco nao tem COMMENT.

- Objetos: **91**

## Indice

**Dimensoes** (42): [dim_calendario](#dim-calendario), [dim_centro_custo](#dim-centro-custo), [dim_centro_custo_empresa](#dim-centro-custo-empresa), [dim_centro_trabalho](#dim-centro-trabalho), [dim_cidade](#dim-cidade), [dim_cliente](#dim-cliente), [dim_condicao_pagamento](#dim-condicao-pagamento), [dim_condicao_pagamento_parcela](#dim-condicao-pagamento-parcela), [dim_configurador](#dim-configurador), [dim_conta_contabil](#dim-conta-contabil), [dim_conta_contabil_temp](#dim-conta-contabil-temp), [dim_conta_financeira](#dim-conta-financeira), [dim_conta_financeira_empresa](#dim-conta-financeira-empresa), [dim_conversao_item](#dim-conversao-item), [dim_cotacao](#dim-cotacao), [dim_empresa](#dim-empresa), [dim_estabelecimento](#dim-estabelecimento), [dim_fornecedor](#dim-fornecedor), [dim_funcionario](#dim-funcionario), [dim_grupo_problema_assistencia](#dim-grupo-problema-assistencia), [dim_item](#dim-item), [dim_item_classificacao](#dim-item-classificacao), [dim_item_empresa](#dim-item-empresa), [dim_item_ordem](#dim-item-ordem), [dim_mascara](#dim-mascara), [dim_motivo_assistencia](#dim-motivo-assistencia), [dim_motivo_chamado](#dim-motivo-chamado), [dim_operacao](#dim-operacao), [dim_portador](#dim-portador), [dim_representante](#dim-representante), [dim_servico_lei](#dim-servico-lei), [dim_tipo_chamado](#dim-tipo-chamado), [dim_tipo_documento](#dim-tipo-documento), [dim_tipo_lancamento_ccr](#dim-tipo-lancamento-ccr), [dim_tipo_lancamento_ccr_contabil](#dim-tipo-lancamento-ccr-contabil), [dim_tipo_lancamento_cp](#dim-tipo-lancamento-cp), [dim_tipo_lancamento_cp_contabil](#dim-tipo-lancamento-cp-contabil), [dim_tipo_lancamento_cr](#dim-tipo-lancamento-cr), [dim_tipo_lancamento_cr_contabil](#dim-tipo-lancamento-cr-contabil), [dim_tipo_nf_entrada](#dim-tipo-nf-entrada), [dim_tipo_nf_saida](#dim-tipo-nf-saida), [dim_unidade_medida](#dim-unidade-medida)

**Fatos** (37): [fat_assistencia_item](#fat-assistencia-item), [fat_chamado_assistencia](#fat-chamado-assistencia), [fat_chamado_assistencia_texto](#fat-chamado-assistencia-texto), [fat_contrato_loja](#fat-contrato-loja), [fat_contrato_loja_parcela](#fat-contrato-loja-parcela), [fat_estoque_custo](#fat-estoque-custo), [fat_estoque_movimento](#fat-estoque-movimento), [fat_lancamento_conta_corrente](#fat-lancamento-conta-corrente), [fat_lancamento_contabil](#fat-lancamento-contabil), [fat_lancamento_contabil_conta](#fat-lancamento-contabil-conta), [fat_lancamento_contabil_transferencia](#fat-lancamento-contabil-transferencia), [fat_lancamento_contabil_transferencia_conta](#fat-lancamento-contabil-transferencia-conta), [fat_movimento_pagar](#fat-movimento-pagar), [fat_movimento_receber](#fat-movimento-receber), [fat_nota_entrada](#fat-nota-entrada), [fat_nota_entrada_item](#fat-nota-entrada-item), [fat_nota_entrada_item_origem](#fat-nota-entrada-item-origem), [fat_nota_saida](#fat-nota-saida), [fat_nota_saida_item](#fat-nota-saida-item), [fat_nota_saida_item_pedido](#fat-nota-saida-item-pedido), [fat_nota_saida_item_pontuacao](#fat-nota-saida-item-pontuacao), [fat_ordem_fabricacao](#fat-ordem-fabricacao), [fat_ordem_movimento](#fat-ordem-movimento), [fat_ordem_roteiro](#fat-ordem-roteiro), [fat_pedido](#fat-pedido), [fat_pedido_compra](#fat-pedido-compra), [fat_pedido_compra_item](#fat-pedido-compra-item), [fat_pedido_item](#fat-pedido-item), [fat_pedido_representante_secundario](#fat-pedido-representante-secundario), [fat_pontuacao_producao](#fat-pontuacao-producao), [fat_previsao_financeira](#fat-previsao-financeira), [fat_previsao_financeira_parcela](#fat-previsao-financeira-parcela), [fat_saldo_conta_corrente](#fat-saldo-conta-corrente), [fat_saldo_contabil](#fat-saldo-contabil), [fat_titulo_pagar](#fat-titulo-pagar), [fat_titulo_receber](#fat-titulo-receber), [fat_titulo_receber_detalhe](#fat-titulo-receber-detalhe)

**Pontes** (4): [ponte_assistencia_centro_custo](#ponte-assistencia-centro-custo), [ponte_nota_item_pedido_item](#ponte-nota-item-pedido-item), [ponte_nota_saida_item_servico](#ponte-nota-saida-item-servico), [ponte_pedido_configuracao_ordem](#ponte-pedido-configuracao-ordem)

**Views** (8): [vw_assistencia](#vw-assistencia), [vw_compras](#vw-compras), [vw_contas_pagar](#vw-contas-pagar), [vw_contas_receber](#vw-contas-receber), [vw_estoque_movimentos](#vw-estoque-movimentos), [vw_faturamento](#vw-faturamento), [vw_pedidos](#vw-pedidos), [vw_producao_operacoes](#vw-producao-operacoes)

## Dimensoes

### dim_calendario

> Calendario continuo para marcar como tabela de datas no Power BI

`tipo: tabela | linhas (estimativa): 4,679 | tamanho: 584.0 KB`

**PK:** `data`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`data` | `date` | nao |  |
| 2 | `ano` | `integer` | sim |  |
| 3 | `trimestre` | `integer` | sim |  |
| 4 | `mes` | `integer` | sim |  |
| 5 | `nome_mes` | `text` | sim |  |
| 6 | `ano_mes` | `text` | sim |  |
| 7 | `dia` | `integer` | sim |  |
| 8 | `dia_semana` | `integer` | sim |  |
| 9 | `nome_dia_semana` | `text` | sim |  |
| 10 | `fim_de_semana` | `boolean` | sim |  |
| 11 | `primeiro_dia_mes` | `date` | sim |  |
| 12 | `ultimo_dia_mes` | `date` | sim |  |

### dim_centro_custo

> Centro de custo GLOBAL (211 linhas), derivado da mesma origem: cada código corresponde a exatamente uma descrição. É esta a chave usada por estoque e assistência técnica — não confundir com dim_centro_custo_empresa. | origem: F_BI_D_CENTRO_CUSTOS.TXT

`tipo: tabela | linhas (estimativa): 211 | tamanho: 72.0 KB`

**PK:** `id_centro_custo`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_centro_custo` | `bigint` | nao | col 0 do arquivo \| Chave global do centro de custo |
| 2 | `descricao_centro_custo` | `text` | sim | col 1 do arquivo \| Descrição |
| 3 | `tipo_conta` | `text` | sim | col 2 do arquivo \| A = analítica, S = sintética |
| 4 | `nivel` | `bigint` | sim | col 3 do arquivo \| Nível hierárquico |
| 5 | `sigla_grupo` | `text` | sim | col 4 do arquivo \| Sigla do agrupamento (ADM, COM, PRO, AUX...) |

### dim_centro_custo_empresa

> Centro de custo POR EMPRESA (680 linhas). Chave usada pelo contas a pagar, conta corrente e saldos contábeis. | origem: F_BI_D_CENTRO_CUSTOS.TXT

`tipo: tabela | linhas (estimativa): 680 | tamanho: 144.0 KB`

**PK:** `id_centro_custo_empresa`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_centro_custo_empresa` | `bigint` | nao | col 0 do arquivo \| Chave do centro de custo dentro da empresa |
| 2 | `id_empresa` | `bigint` | sim | col 1 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 3 | `cod_centro_custo` | `bigint` | sim | col 2 do arquivo \| Código hierárquico do centro de custo |
| 4 | `descricao_centro_custo` | `text` | sim | col 3 do arquivo \| Descrição |
| 5 | `tipo_conta` | `text` | sim | col 4 do arquivo \| A = analítica, S = sintética |
| 6 | `nivel` | `bigint` | sim | col 5 do arquivo \| Nível hierárquico |
| 7 | `sigla_grupo` | `text` | sim | col 6 do arquivo \| Sigla do agrupamento (ADM, COM, PRO, AUX...) |
| 8 | `id_centro_custo` | `bigint` | sim | col 7 do arquivo \| Centro de custo global correspondente [FK -> dim_centro_custo.id_centro_custo] |
| 9 | `cod_agrupamento` | `bigint` | sim | col 8 do arquivo \| Código de agrupamento (não unívoco) |

### dim_centro_trabalho

> Centros de trabalho da fábrica | origem: F_BI_D_CENTROS_TRABALHOS.TXT

`tipo: tabela | linhas (estimativa): 137 | tamanho: 72.0 KB`

**PK:** `id_centro_trabalho`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_centro_trabalho` | `bigint` | nao | col 0 do arquivo \| Chave interna do centro de trabalho |
| 2 | `cod_centro_trabalho` | `bigint` | sim | col 1 do arquivo \| Código do centro de trabalho |
| 3 | `descricao_centro_trabalho` | `text` | sim | col 2 do arquivo \| Descrição |
| 4 | `id_centro_custo` | `bigint` | sim | col 3 do arquivo \| Centro de custo associado (provável — confirmar) |
| 5 | `qtd_recursos` | `bigint` | sim | col 4 do arquivo \| Quantidade de recursos/máquinas |
| 6 | `custo_hora` | `numeric(20,8)` | sim | col 5 do arquivo \| Custo hora cadastrado |
| 7 | `id_centro_trabalho_alternativo` | `bigint` | sim | col 6 do arquivo \| Centro de trabalho alternativo |

### dim_cidade

> Municípios (Brasil e exterior) | origem: F_BI_D_CIDADE.TXT

`tipo: tabela | linhas (estimativa): 5,685 | tamanho: 536.0 KB`

**PK:** `id_cidade`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_cidade` | `bigint` | nao | col 0 do arquivo \| Chave interna do município |
| 2 | `nome_cidade` | `text` | sim | col 1 do arquivo \| Nome do município |
| 3 | `uf` | `text` | sim | col 2 do arquivo \| Sigla da UF / região |
| 4 | `pais` | `text` | sim | col 3 do arquivo \| País |

### dim_cliente

> Clientes | origem: F_BI_D_CLIENTE.TXT

`tipo: tabela | linhas (estimativa): 7,131 | tamanho: 944.0 KB`

**PK:** `id_cliente`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_cliente` | `bigint` | nao | col 0 do arquivo \| Chave interna do cliente |
| 2 | `cod_cliente` | `bigint` | sim | col 1 do arquivo \| Código do cliente |
| 3 | `nome_cliente` | `text` | sim | col 2 do arquivo \| Razão social / nome |
| 4 | `canal_venda` | `text` | sim | col 3 do arquivo \| Canal: EMPRESA, MULTIMARCAS, CONSUMIDOR FINAL, ... |
| 5 | `tipo_cliente` | `text` | sim | col 4 do arquivo \| Classificação: CONSUMIDOR FINAL PF/PJ, FORNECEDOR, ... |

### dim_condicao_pagamento

> Condições de pagamento | origem: F_BI_D_TCOND_PAGTOS.TXT

`tipo: tabela | linhas (estimativa): 207 | tamanho: 80.0 KB`

**PK:** `id_condicao_pagamento`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_condicao_pagamento` | `bigint` | nao | col 0 do arquivo \| Chave interna da condição |
| 2 | `cod_condicao_pagamento` | `bigint` | sim | col 1 do arquivo \| Código da condição |
| 3 | `descricao_condicao` | `text` | sim | col 2 do arquivo \| Descrição (ex.: 28/42/56 dias) |
| 4 | `qtd_parcelas` | `bigint` | sim | col 3 do arquivo \| Quantidade de parcelas |
| 5 | `percentual_juros` | `numeric(20,8)` | sim | col 4 do arquivo \| Percentual de juros |
| 6 | `ativo` | `bigint` | sim | col 5 do arquivo \| Indicador de ativo |

### dim_condicao_pagamento_parcela

> Parcelas que compõem cada condição de pagamento | origem: F_BI_D_TPARC_COND_PAGTOS.TXT

`tipo: tabela | linhas (estimativa): 893 | tamanho: 152.0 KB`

**PK:** `id_parcela_condicao`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_parcela_condicao` | `bigint` | nao | col 0 do arquivo \| Chave interna da parcela |
| 2 | `num_parcela` | `bigint` | sim | col 1 do arquivo \| Número sequencial da parcela |
| 3 | `dias_prazo` | `bigint` | sim | col 2 do arquivo \| Prazo em dias |
| 4 | `percentual_valor` | `numeric(20,8)` | sim | col 3 do arquivo \| Percentual do valor total |
| 5 | `id_condicao_pagamento` | `bigint` | sim | col 4 do arquivo \| Condição de pagamento [FK -> dim_condicao_pagamento.id_condicao_pagamento] |
| 6 | `flag_fixa` | `bigint` | sim | col 5 do arquivo \| Indicador auxiliar |
| 7 | `observacao` | `text` | sim | col 6 do arquivo \| Observação |

### dim_configurador

> Respostas do configurador de produto, uma linha por pergunta. Une os 2 arquivos do configurador. | origem: F_BI_D_CONFIGURADOR.TXT, F_BI_D_CONFIGURADOR_PARTE2.TXT

`tipo: tabela | linhas (estimativa): 8,002,531 | tamanho: 1.0 GB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_configuracao` | `bigint` | sim | col 0 do arquivo \| Chave da configuração (repete por pergunta) |
| 2 | `cod_empresa` | `bigint` | sim | col 1 do arquivo \| Empresa |
| 3 | `cod_referencia_1` | `bigint` | sim | col 2 do arquivo \| Referência interna 1 — CONFIRMAR com o ERP |
| 4 | `cod_referencia_2` | `bigint` | sim | col 3 do arquivo \| Referência interna 2 — CONFIRMAR com o ERP |
| 5 | `sequencia` | `bigint` | sim | col 4 do arquivo \| Ordem da pergunta na configuração |
| 6 | `pergunta` | `text` | sim | col 5 do arquivo \| Texto da pergunta |
| 7 | `rotulo` | `text` | sim | col 6 do arquivo \| Rótulo curto exibido |
| 8 | `resposta` | `text` | sim | col 7 do arquivo \| Resposta escolhida |
| 9 | `grupo_opcao` | `text` | sim | col 8 do arquivo \| Grupo da opção (MADEIRAS, TECIDOS & COUROS, ...) |

### dim_conta_contabil

> Plano de contas contábil | origem: F_BI_D_CONTAS.TXT

`tipo: tabela | linhas (estimativa): 1,237 | tamanho: 280.0 KB`

**PK:** `id_conta`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_conta` | `bigint` | nao | col 0 do arquivo \| Chave interna da conta |
| 2 | `cod_conta_reduzido` | `bigint` | sim | col 1 do arquivo \| Código reduzido da conta |
| 3 | `id_conta_superior` | `bigint` | sim | col 2 do arquivo \| Conta pai na hierarquia |
| 4 | `descricao_conta` | `text` | sim | col 3 do arquivo \| Descrição da conta |
| 5 | `cod_conta_referencial` | `bigint` | sim | col 4 do arquivo \| Código referencial (SPED) |
| 6 | `tipo_conta` | `text` | sim | col 5 do arquivo \| A = analítica, S = sintética |
| 7 | `nivel` | `bigint` | sim | col 6 do arquivo \| Nível hierárquico |
| 8 | `flag_1` | `bigint` | sim | col 7 do arquivo \| Indicador auxiliar |
| 9 | `cod_grupo_conta` | `bigint` | sim | col 8 do arquivo \| Grupo (01=ativo, 02=passivo, 03=resultado...) |
| 10 | `flag_2` | `bigint` | sim | col 9 do arquivo \| Indicador auxiliar |
| 11 | `data_inativacao` | `date` | sim | col 10 do arquivo \| Data de inativação |
| 12 | `ativo` | `bigint` | sim | col 11 do arquivo \| Indicador de ativo |
| 13 | `data_inicio_vigencia` | `date` | sim | col 12 do arquivo \| Início da vigência |
| 14 | `data_fim_vigencia` | `date` | sim | col 13 do arquivo \| Fim da vigência |

### dim_conta_contabil_temp

> Contas contábeis auxiliares usadas no balancete | origem: F_BI_F_TEMP_CTA_CTAB.TXT

`tipo: tabela | linhas (estimativa): 7,525 | tamanho: 1000.0 KB`

**PK:** `id_conta_temp`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_conta_temp` | `bigint` | nao | col 0 do arquivo \| Chave interna |
| 2 | `id_conta_superior` | `bigint` | sim | col 1 do arquivo \| Conta pai |
| 3 | `cod_empresa` | `bigint` | sim | col 2 do arquivo \| Empresa |
| 4 | `id_conta` | `bigint` | sim | col 3 do arquivo \| Conta contábil relacionada |
| 5 | `descricao_conta` | `text` | sim | col 4 do arquivo \| Descrição |
| 6 | `flag_1` | `bigint` | sim | col 5 do arquivo \| Indicador auxiliar |
| 7 | `flag_2` | `bigint` | sim | col 6 do arquivo \| Indicador auxiliar |

### dim_conta_financeira

> Plano de contas financeiro (gerencial) | origem: F_BI_D_CONTA FINANCEIRA.TXT

`tipo: tabela | linhas (estimativa): 193 | tamanho: 80.0 KB`

**PK:** `id_conta_financeira`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_conta_financeira` | `bigint` | nao | col 0 do arquivo \| Chave interna da conta financeira |
| 2 | `cod_conta_financeira` | `bigint` | sim | col 1 do arquivo \| Código hierárquico |
| 3 | `descricao_conta_financeira` | `text` | sim | col 2 do arquivo \| Descrição |
| 4 | `tipo_conta` | `text` | sim | col 3 do arquivo \| A = analítica, S = sintética |
| 5 | `nivel` | `bigint` | sim | col 4 do arquivo \| Nível hierárquico |
| 6 | `id_conta_financeira_superior` | `bigint` | sim | col 5 do arquivo \| Conta pai |

### dim_conta_financeira_empresa

> Vínculo entre conta financeira e empresa | origem: F_BI_D_CONTA_FIN_EMP.TXT

`tipo: tabela | linhas (estimativa): 9,648 | tamanho: 1.0 MB`

**PK:** `id_conta_financeira_empresa`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_conta_financeira_empresa` | `bigint` | nao | col 0 do arquivo \| Chave interna do vínculo |
| 2 | `id_empresa` | `bigint` | sim | col 1 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 3 | `cod_referencia` | `bigint` | sim | col 2 do arquivo \| Referência interna — CONFIRMAR com o ERP |
| 4 | `id_conta_financeira` | `bigint` | sim | col 3 do arquivo \| Conta financeira [FK -> dim_conta_financeira.id_conta_financeira] |
| 5 | `flag_1` | `bigint` | sim | col 4 do arquivo \| Indicador auxiliar |
| 6 | `flag_2` | `bigint` | sim | col 5 do arquivo \| Indicador auxiliar |
| 7 | `flag_3` | `bigint` | sim | col 6 do arquivo \| Indicador auxiliar |

### dim_conversao_item

> Fatores de conversão de unidade por item | origem: F_BI_D_TCONV_ITEM.TXT

`tipo: tabela | linhas (estimativa): 5,970 | tamanho: 744.0 KB`

**PK:** `id_conversao`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_conversao` | `bigint` | nao | col 0 do arquivo \| Chave interna |
| 2 | `fator_conversao` | `numeric(20,8)` | sim | col 1 do arquivo \| Fator de conversão |
| 3 | `id_unidade_origem` | `bigint` | sim | col 2 do arquivo \| Unidade de origem [FK -> dim_unidade_medida.id_unidade] |
| 4 | `id_unidade_destino` | `bigint` | sim | col 3 do arquivo \| Unidade de destino [FK -> dim_unidade_medida.id_unidade] |
| 5 | `id_item` | `bigint` | sim | col 4 do arquivo \| Item |
| 6 | `cod_empresa` | `bigint` | sim | col 5 do arquivo \| Empresa |
| 7 | `cod_referencia` | `bigint` | sim | col 6 do arquivo \| Referência interna |
| 8 | `valor_auxiliar_1` | `numeric(20,8)` | sim | col 7 do arquivo \| Valor auxiliar |
| 9 | `tipo_conversao` | `text` | sim | col 8 do arquivo \| Tipo (P = padrão) |
| 10 | `valor_auxiliar_2` | `numeric(20,8)` | sim | col 9 do arquivo \| Valor auxiliar |

### dim_cotacao

> Cotações de indexadores e moedas por data | origem: F_BI_D_COTACOES.TXT

`tipo: tabela | linhas (estimativa): 64,143 | tamanho: 4.6 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `data_cotacao` | `date` | sim | col 0 do arquivo \| Data da cotação |
| 2 | `valor_cotacao` | `numeric(20,8)` | sim | col 1 do arquivo \| Valor da cotação |
| 3 | `id_indexador` | `bigint` | sim | col 2 do arquivo \| Chave interna do indexador |
| 4 | `cod_indexador` | `bigint` | sim | col 3 do arquivo \| Código do indexador |
| 5 | `nome_indexador` | `text` | sim | col 4 do arquivo \| Nome (UFIR, DOLAR, ...) |

### dim_empresa

> Empresas / filiais do grupo | origem: F_BI_D_EMPRESA.TXT

`tipo: tabela | linhas (estimativa): 40 | tamanho: 64.0 KB`

**PK:** `id_empresa`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_empresa` | `bigint` | nao | col 0 do arquivo \| Chave interna da empresa no ERP |
| 2 | `cod_empresa` | `bigint` | sim | col 1 do arquivo \| Código da empresa (igual ao id nesta base) |
| 3 | `razao_social` | `text` | sim | col 2 do arquivo \| Razão social |
| 4 | `nome_fantasia` | `text` | sim | col 3 do arquivo \| Nome fantasia |
| 5 | `cnpj_cpf` | `text` | sim | col 4 do arquivo \| CNPJ ou CPF sem formatação |
| 6 | `cep` | `text` | sim | col 5 do arquivo \| CEP sem formatação |
| 7 | `id_cidade` | `bigint` | sim | col 6 do arquivo \| Cidade da sede [FK -> dim_cidade.id_cidade] |
| 8 | `cod_grupo_empresa` | `bigint` | sim | col 7 do arquivo \| Código de agrupamento societário (a confirmar) |

### dim_estabelecimento

> Estabelecimentos / endereços de entrega e cobrança vinculados a clientes | origem: F_BI_D_ESTABELECIMENTO.TXT

`tipo: tabela | linhas (estimativa): 7,910 | tamanho: 1.8 MB`

**PK:** `id_estabelecimento`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_estabelecimento` | `bigint` | nao | col 0 do arquivo \| Chave interna do estabelecimento |
| 2 | `cod_tipo_estabelecimento` | `bigint` | sim | col 1 do arquivo \| Tipo/sequência do endereço do cliente |
| 3 | `id_cliente` | `bigint` | sim | col 2 do arquivo \| Cliente proprietário do estabelecimento [FK -> dim_cliente.id_cliente] |
| 4 | `id_cidade` | `bigint` | sim | col 3 do arquivo \| Município [FK -> dim_cidade.id_cidade] |
| 5 | `razao_social` | `text` | sim | col 4 do arquivo \| Razão social |
| 6 | `nome_fantasia` | `text` | sim | col 5 do arquivo \| Nome fantasia |
| 7 | `endereco` | `text` | sim | col 6 do arquivo \| Logradouro e número |
| 8 | `complemento` | `text` | sim | col 7 do arquivo \| Complemento |
| 9 | `bairro` | `text` | sim | col 8 do arquivo \| Bairro |
| 10 | `cep` | `text` | sim | col 9 do arquivo \| CEP |
| 11 | `cnpj` | `text` | sim | col 10 do arquivo \| CNPJ |
| 12 | `cpf` | `text` | sim | col 11 do arquivo \| CPF |

### dim_fornecedor

> Fornecedores | origem: F_BI_D_FORNECEDOR.TXT

`tipo: tabela | linhas (estimativa): 10,900 | tamanho: 1.8 MB`

**PK:** `id_fornecedor`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_fornecedor` | `bigint` | nao | col 0 do arquivo \| Chave interna do fornecedor |
| 2 | `cod_fornecedor` | `bigint` | sim | col 1 do arquivo \| Código do fornecedor |
| 3 | `razao_social` | `text` | sim | col 2 do arquivo \| Razão social |
| 4 | `nome_fantasia` | `text` | sim | col 3 do arquivo \| Nome fantasia |
| 5 | `cnpj` | `text` | sim | col 4 do arquivo \| CNPJ sem formatação (0 quando não informado) |
| 6 | `cod_localidade` | `text` | sim | col 5 do arquivo \| Código de localidade/CEP resumido — CONFIRMAR com o ERP |
| 7 | `cpf` | `text` | sim | col 6 do arquivo \| CPF sem formatação (0 quando não informado) |

### dim_funcionario

> Funcionários / usuários operacionais | origem: F_BI_D_FUNCIONARIO.TXT

`tipo: tabela | linhas (estimativa): 323 | tamanho: 88.0 KB`

**PK:** `id_funcionario`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_funcionario` | `bigint` | nao | col 0 do arquivo \| Chave interna do funcionário |
| 2 | `cod_funcionario` | `text` | sim | col 1 do arquivo \| Matrícula / código |
| 3 | `nome_funcionario` | `text` | sim | col 2 do arquivo \| Nome ou descrição da função |
| 4 | `cod_empresa` | `bigint` | sim | col 3 do arquivo \| Empresa de vínculo (a confirmar) |
| 5 | `ativo` | `bigint` | sim | col 4 do arquivo \| Indicador de ativo (1 = sim) |

### dim_grupo_problema_assistencia

> Grupos de responsabilidade do problema de assistência | origem: F_BI_D_TGPR_ASSISTENCIA.TXT

`tipo: tabela | linhas (estimativa): 15 | tamanho: 32.0 KB`

**PK:** `id_grupo_problema`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_grupo_problema` | `bigint` | nao | col 0 do arquivo \| Chave interna |
| 2 | `cod_grupo_problema` | `bigint` | sim | col 1 do arquivo \| Código |
| 3 | `descricao_grupo_problema` | `text` | sim | col 2 do arquivo \| Descrição (CLIENTE, FABRICA, TRANSPORTE...) |
| 4 | `flag_1` | `bigint` | sim | col 3 do arquivo \| Indicador auxiliar |
| 5 | `cod_empresa` | `bigint` | sim | col 4 do arquivo \| Empresa |
| 6 | `situacao` | `text` | sim | col 5 do arquivo \| A = ativo |

### dim_item

> Catálogo global de itens (1 linha por código). Chave usada por compras, estoque e NF de entrada. | origem: F_BI_D_ITENS_CADASTRO.TXT

`tipo: tabela | linhas (estimativa): 125,261 | tamanho: 14.1 MB`

**PK:** `id_item`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_item` | `bigint` | nao | col 0 do arquivo \| Chave interna do item no cadastro global |
| 2 | `cod_item` | `bigint` | sim | col 1 do arquivo \| Código do item |
| 3 | `descricao_item` | `text` | sim | col 2 do arquivo \| Descrição do item |

### dim_item_classificacao

> Classificações do item por visão (comercial, contábil, custos, engenharia, estoque...) | origem: F_BI_D_ITENS_CLASS.TXT

`tipo: tabela | linhas (estimativa): 45,749 | tamanho: 4.7 MB`

**PK:** `id_classificacao`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `tipo_classificacao` | `text` | sim | col 0 do arquivo \| Visão: COMERCIAL, CONTABIL, CUSTOS, ENGENHARIA, ESTOQUE... |
| 2 | `cod_classificacao` | `text` | sim | col 1 do arquivo \| Código hierárquico (ex.: 10.100.004.0002) |
| 3 | `descricao_classificacao` | `text` | sim | col 2 do arquivo \| Descrição da classificação |
| 4 | 🔑`id_classificacao` | `bigint` | nao | col 3 do arquivo \| Chave interna da classificação |

### dim_item_empresa

> Item por empresa. ATENÇÃO: id próprio, diferente de dim_item. Usado por pedido de venda e NF de saída. | origem: F_BI_D_ITENS.TXT

`tipo: tabela | linhas (estimativa): 174,442 | tamanho: 23.3 MB`

**PK:** `id_item_empresa`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_item_empresa` | `bigint` | nao | col 0 do arquivo \| Chave interna do item na empresa |
| 2 | `cod_item` | `bigint` | sim | col 1 do arquivo \| Código do item (mesmo código de dim_item.cod_item) |
| 3 | `descricao_item` | `text` | sim | col 2 do arquivo \| Descrição do item |
| 4 | `cod_familia` | `bigint` | sim | col 3 do arquivo \| Código de família/grupo do item |
| 5 | `id_empresa` | `bigint` | sim | col 4 do arquivo \| Empresa dona do cadastro [FK -> dim_empresa.id_empresa] |
| 6 | `peso` | `numeric(20,8)` | sim | col 5 do arquivo \| Peso cadastrado |

### dim_item_ordem

> Item na visão de produção. Liga a ordem de fabricação ao catálogo global. | origem: F_BI_D_ITENS_ORDENS.TXT

`tipo: tabela | linhas (estimativa): 174,449 | tamanho: 13.9 MB`

**PK:** `id_item_ordem`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_item_ordem` | `bigint` | nao | col 0 do arquivo \| Chave interna do item na produção |
| 2 | `peso` | `numeric(20,8)` | sim | col 1 do arquivo \| Peso do item |
| 3 | `cod_unidade` | `bigint` | sim | col 2 do arquivo \| Unidade de medida (código) |
| 4 | `id_item` | `bigint` | sim | col 3 do arquivo \| Item correspondente no catálogo global [FK -> dim_item.id_item] |

### dim_mascara

> Máscara de configuração do produto (texto com atributos separados por #). Une os 2 arquivos de máscaras. | origem: F_BI_D_MASCARAS.TXT, F_BI_D_MASCARAS_PARTE2.TXT

`tipo: tabela | linhas (estimativa): 1,762,217 | tamanho: 286.8 MB`

**PK:** `id_mascara`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_mascara` | `bigint` | nao | col 0 do arquivo \| Chave interna da máscara |
| 2 | `id_mascara_origem` | `bigint` | sim | col 1 do arquivo \| Máscara de origem / referência |
| 3 | `descricao_mascara` | `text` | sim | col 2 do arquivo \| Configuração completa (atributos separados por #) |

### dim_motivo_assistencia

> Motivos de assistência técnica | origem: F_BI_D_TMOT_ASSISTENCIA.TXT

`tipo: tabela | linhas (estimativa): 261 | tamanho: 88.0 KB`

**PK:** `id_motivo_assistencia`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_motivo_assistencia` | `bigint` | nao | col 0 do arquivo \| Chave interna |
| 2 | `cod_motivo_assistencia` | `bigint` | sim | col 1 do arquivo \| Código |
| 3 | `descricao_motivo` | `text` | sim | col 2 do arquivo \| Descrição do defeito/motivo |
| 4 | `flag_1` | `bigint` | sim | col 3 do arquivo \| Indicador auxiliar |
| 5 | `id_grupo_problema` | `bigint` | sim | col 4 do arquivo \| Grupo responsável [FK -> dim_grupo_problema_assistencia.id_grupo_problema] |
| 6 | `situacao` | `text` | sim | col 5 do arquivo \| A = ativo |
| 7 | `flag_2` | `bigint` | sim | col 6 do arquivo \| Indicador auxiliar |

### dim_motivo_chamado

> Motivos / responsáveis pelo chamado | origem: F_BI_D_TMOT_CHAMADOS.TXT

`tipo: tabela | linhas (estimativa): 145 | tamanho: 64.0 KB`

**PK:** `id_motivo_chamado`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_motivo_chamado` | `bigint` | nao | col 0 do arquivo \| Chave interna |
| 2 | `cod_motivo_chamado` | `bigint` | sim | col 1 do arquivo \| Código |
| 3 | `descricao_motivo_chamado` | `text` | sim | col 2 do arquivo \| Descrição (CLIENTE, FORNECEDOR, TRANSPORTE, FABRICA...) |

### dim_operacao

> Operações do roteiro de produção | origem: F_BI_D_OPERACOES.TXT

`tipo: tabela | linhas (estimativa): 5,221 | tamanho: 784.0 KB`

**PK:** `id_operacao`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_operacao` | `bigint` | nao | col 0 do arquivo \| Chave interna da operação |
| 2 | `cod_operacao` | `bigint` | sim | col 1 do arquivo \| Código da operação |
| 3 | `descricao_operacao` | `text` | sim | col 2 do arquivo \| Descrição da operação |
| 4 | `tipo_operacao` | `text` | sim | col 3 do arquivo \| I = interna, T = terceiro |
| 5 | `cod_operacao_padrao` | `bigint` | sim | col 4 do arquivo \| Operação padrão relacionada |
| 6 | `cod_empresa` | `bigint` | sim | col 5 do arquivo \| Empresa |
| 7 | `reservado_1` | `bigint` | sim | col 6 do arquivo \| Coluna sem uso na extração |
| 8 | `reservado_2` | `bigint` | sim | col 7 do arquivo \| Coluna sem uso na extração |
| 9 | `reservado_3` | `bigint` | sim | col 8 do arquivo \| Coluna sem uso na extração |
| 10 | `reservado_4` | `bigint` | sim | col 9 do arquivo \| Coluna sem uso na extração |

### dim_portador

> Portadores / bancos / carteiras | origem: F_BI_D_TPORTADORES.TXT

`tipo: tabela | linhas (estimativa): 111 | tamanho: 72.0 KB`

**PK:** `id_portador`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_portador` | `bigint` | nao | col 0 do arquivo \| Chave interna do portador |
| 2 | `cod_portador` | `bigint` | sim | col 1 do arquivo \| Código do portador |
| 3 | `nome_portador` | `text` | sim | col 2 do arquivo \| Nome do banco/carteira |

### dim_representante

> Representantes comerciais / canais de venda | origem: F_BI_D_REPRESENTANTE.TXT

`tipo: tabela | linhas (estimativa): 180 | tamanho: 72.0 KB`

**PK:** `id_representante`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_representante` | `bigint` | nao | col 0 do arquivo \| Chave interna do representante |
| 2 | `cod_representante` | `bigint` | sim | col 1 do arquivo \| Código do representante |
| 3 | `nome_representante` | `text` | sim | col 2 do arquivo \| Nome / razão social do representante |

### dim_servico_lei

> Lista de serviços da LC 116 (ISS) | origem: F_BI_D_TSERVICOS_LEI.TXT

`tipo: tabela | linhas (estimativa): 238 | tamanho: 96.0 KB`

**PK:** `id_servico`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_servico` | `bigint` | nao | col 0 do arquivo \| Chave interna |
| 2 | `cod_servico_lc116` | `text` | sim | col 1 do arquivo \| Item da lista de serviços |
| 3 | `descricao_servico` | `text` | sim | col 2 do arquivo \| Descrição do serviço |

### dim_tipo_chamado

> Tipos de chamado de assistência | origem: F_BI_D_TTP_CHAMADOS.TXT

`tipo: tabela | linhas (estimativa): 52 | tamanho: 64.0 KB`

**PK:** `id_tipo_chamado`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_tipo_chamado` | `bigint` | nao | col 0 do arquivo \| Chave interna |
| 2 | `cod_tipo_chamado` | `bigint` | sim | col 1 do arquivo \| Código |
| 3 | `descricao_tipo_chamado` | `text` | sim | col 2 do arquivo \| Descrição |

### dim_tipo_documento

> Tipos de documento financeiro | origem: F_BI_D_TP_DOC.TXT

`tipo: tabela | linhas (estimativa): 69 | tamanho: 64.0 KB`

**PK:** `id_tipo_documento`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_tipo_documento` | `bigint` | nao | col 0 do arquivo \| Chave interna do tipo de documento |
| 2 | `sigla_documento` | `text` | sim | col 1 do arquivo \| Sigla (DUP, NP, REC, IMP...) |
| 3 | `descricao_documento` | `text` | sim | col 2 do arquivo \| Descrição |
| 4 | `cod_especie` | `bigint` | sim | col 3 do arquivo \| Código de espécie fiscal |

### dim_tipo_lancamento_ccr

> Tipos de lançamento de conta corrente | origem: F_BI_F_TTP_CCR.TXT

`tipo: tabela | linhas (estimativa): 134 | tamanho: 72.0 KB`

**PK:** `id_tipo_lancamento_ccr`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_tipo_lancamento_ccr` | `bigint` | nao | col 0 do arquivo \| Chave interna |
| 2 | `cod_tipo_lancamento_ccr` | `bigint` | sim | col 1 do arquivo \| Código do tipo |
| 3 | `descricao_tipo` | `text` | sim | col 2 do arquivo \| Descrição |
| 4 | `natureza` | `text` | sim | col 3 do arquivo \| D = débito, C = crédito |
| 5 | `flag_1` | `bigint` | sim | col 4 do arquivo \| Indicador auxiliar |
| 6 | `flag_2` | `bigint` | sim | col 5 do arquivo \| Indicador auxiliar |
| 7 | `cod_agrupamento` | `bigint` | sim | col 6 do arquivo \| Código de agrupamento |

### dim_tipo_lancamento_ccr_contabil

> Amarração contábil dos tipos de lançamento (conta débito/crédito) | origem: F_BI_D_TTP_CCR_CTAB.TXT

`tipo: tabela | linhas (estimativa): 1,299 | tamanho: 224.0 KB`

**PK:** `id_amarracao`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_amarracao` | `bigint` | nao | col 0 do arquivo \| Chave interna da amarração |
| 2 | `cod_amarracao` | `bigint` | sim | col 1 do arquivo \| Código da amarração |
| 3 | `id_tipo_lancamento` | `bigint` | sim | col 2 do arquivo \| Tipo de lançamento [FK -> dim_tipo_lancamento_ccr.id_tipo_lancamento_ccr] |
| 4 | `id_portador` | `bigint` | sim | col 3 do arquivo \| Portador [FK -> dim_portador.id_portador] |
| 5 | `id_conta_debito` | `bigint` | sim | col 4 do arquivo \| Conta contábil de débito |
| 6 | `id_conta_credito` | `bigint` | sim | col 5 do arquivo \| Conta contábil de crédito |
| 7 | `flag_1` | `bigint` | sim | col 6 do arquivo \| Indicador auxiliar |
| 8 | `flag_2` | `bigint` | sim | col 7 do arquivo \| Indicador auxiliar |
| 9 | `id_historico` | `bigint` | sim | col 8 do arquivo \| Histórico padrão |
| 10 | `id_empresa` | `bigint` | sim | col 9 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |

### dim_tipo_lancamento_cp

> Tipos de lançamento de contas a pagar | origem: F_BI_D_TTP_CP.TXT

`tipo: tabela | linhas (estimativa): 88 | tamanho: 72.0 KB`

**PK:** `id_tipo_lancamento_cp`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_tipo_lancamento_cp` | `bigint` | nao | col 0 do arquivo \| Chave interna |
| 2 | `cod_tipo_lancamento_cp` | `bigint` | sim | col 1 do arquivo \| Código do tipo |
| 3 | `descricao_tipo` | `text` | sim | col 2 do arquivo \| Descrição |
| 4 | `momento` | `text` | sim | col 3 do arquivo \| EM = emissão, PG = pagamento |
| 5 | `natureza` | `text` | sim | col 4 do arquivo \| D = débito, C = crédito |
| 6 | `ativo` | `bigint` | sim | col 5 do arquivo \| Indicador de ativo |

### dim_tipo_lancamento_cp_contabil

> Amarração contábil dos tipos de lançamento (conta débito/crédito) | origem: F_BI_D_TTP_CP_CTAB.TXT

`tipo: tabela | linhas (estimativa): 882 | tamanho: 168.0 KB`

**PK:** `id_amarracao`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_amarracao` | `bigint` | nao | col 0 do arquivo \| Chave interna da amarração |
| 2 | `cod_amarracao` | `bigint` | sim | col 1 do arquivo \| Código da amarração |
| 3 | `id_tipo_lancamento` | `bigint` | sim | col 2 do arquivo \| Tipo de lançamento [FK -> dim_tipo_lancamento_cp.id_tipo_lancamento_cp] |
| 4 | `id_portador` | `bigint` | sim | col 3 do arquivo \| Portador [FK -> dim_portador.id_portador] |
| 5 | `id_conta_debito` | `bigint` | sim | col 4 do arquivo \| Conta contábil de débito |
| 6 | `id_conta_credito` | `bigint` | sim | col 5 do arquivo \| Conta contábil de crédito |
| 7 | `flag_1` | `bigint` | sim | col 6 do arquivo \| Indicador auxiliar |
| 8 | `flag_2` | `bigint` | sim | col 7 do arquivo \| Indicador auxiliar |
| 9 | `id_historico` | `bigint` | sim | col 8 do arquivo \| Histórico padrão |
| 10 | `id_empresa` | `bigint` | sim | col 9 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |

### dim_tipo_lancamento_cr

> Tipos de lançamento de contas a receber | origem: F_BI_D_TTP_CR.TXT

`tipo: tabela | linhas (estimativa): 86 | tamanho: 72.0 KB`

**PK:** `id_tipo_lancamento_cr`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_tipo_lancamento_cr` | `bigint` | nao | col 0 do arquivo \| Chave interna |
| 2 | `cod_tipo_lancamento_cr` | `bigint` | sim | col 1 do arquivo \| Código do tipo |
| 3 | `descricao_tipo` | `text` | sim | col 2 do arquivo \| Descrição |
| 4 | `momento` | `text` | sim | col 3 do arquivo \| EM = emissão, PG = pagamento |
| 5 | `natureza` | `text` | sim | col 4 do arquivo \| D = débito, C = crédito |

### dim_tipo_lancamento_cr_contabil

> Amarração contábil dos tipos de lançamento (conta débito/crédito) | origem: F_BI_D_TTP_CR_CTAB.TXT

`tipo: tabela | linhas (estimativa): 484 | tamanho: 120.0 KB`

**PK:** `id_amarracao`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_amarracao` | `bigint` | nao | col 0 do arquivo \| Chave interna da amarração |
| 2 | `cod_amarracao` | `bigint` | sim | col 1 do arquivo \| Código da amarração |
| 3 | `id_tipo_lancamento` | `bigint` | sim | col 2 do arquivo \| Tipo de lançamento [FK -> dim_tipo_lancamento_cr.id_tipo_lancamento_cr] |
| 4 | `id_portador` | `bigint` | sim | col 3 do arquivo \| Portador [FK -> dim_portador.id_portador] |
| 5 | `id_conta_debito` | `bigint` | sim | col 4 do arquivo \| Conta contábil de débito |
| 6 | `id_conta_credito` | `bigint` | sim | col 5 do arquivo \| Conta contábil de crédito |
| 7 | `flag_1` | `bigint` | sim | col 6 do arquivo \| Indicador auxiliar |
| 8 | `flag_2` | `bigint` | sim | col 7 do arquivo \| Indicador auxiliar |
| 9 | `id_historico` | `bigint` | sim | col 8 do arquivo \| Histórico padrão |
| 10 | `id_empresa` | `bigint` | sim | col 9 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |

### dim_tipo_nf_entrada

> Tipos de nota fiscal de entrada | origem: F_BI_D_TIPO_NF_ENT.TXT

`tipo: tabela | linhas (estimativa): 523 | tamanho: 136.0 KB`

**PK:** `id_tipo_nf_entrada`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_tipo_nf_entrada` | `bigint` | nao | col 0 do arquivo \| Chave interna do tipo de NF de entrada |
| 2 | `cod_tipo_nf_entrada` | `bigint` | sim | col 1 do arquivo \| Código do tipo |
| 3 | `descricao_tipo_nf` | `text` | sim | col 2 do arquivo \| Descrição da natureza da operação |
| 4 | `cod_finalidade` | `bigint` | sim | col 3 do arquivo \| Código de finalidade |
| 5 | `cfop` | `bigint` | sim | col 4 do arquivo \| CFOP |

### dim_tipo_nf_saida

> Tipos de nota fiscal de saída (CFOP e natureza) | origem: F_BI_D_TIPO_NF.TXT

`tipo: tabela | linhas (estimativa): 412 | tamanho: 128.0 KB`

**PK:** `id_tipo_nf_saida`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_tipo_nf_saida` | `bigint` | nao | col 0 do arquivo \| Chave interna do tipo de NF de saída |
| 2 | `cod_tipo_nf_saida` | `bigint` | sim | col 1 do arquivo \| Código / CFOP base |
| 3 | `descricao_tipo_nf` | `text` | sim | col 2 do arquivo \| Descrição da natureza da operação |
| 4 | `flag_gera_financeiro` | `bigint` | sim | col 3 do arquivo \| Indicador auxiliar |
| 5 | `flag_movimenta_estoque` | `bigint` | sim | col 4 do arquivo \| Indicador auxiliar |
| 6 | `cod_finalidade` | `bigint` | sim | col 5 do arquivo \| Código de finalidade da operação |

### dim_unidade_medida

> Unidades de medida | origem: F_BI_D_UNIDADEMEDIDA.TXT

`tipo: tabela | linhas (estimativa): 168 | tamanho: 64.0 KB`

**PK:** `id_unidade`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_unidade` | `bigint` | nao | col 0 do arquivo \| Chave interna da unidade |
| 2 | `sigla_unidade` | `text` | sim | col 1 do arquivo \| Sigla (KG, MT, UN, PC...) |

## Fatos

### fat_assistencia_item

> Itens em assistência técnica | origem: F_BI_F_TITENS_ASSISTENCIA.TXT

`tipo: tabela | linhas (estimativa): 50,922 | tamanho: 14.3 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_assistencia_item` | `bigint` | sim | col 0 do arquivo \| Chave interna do item de assistência |
| 2 | `id_solicitacao` | `bigint` | sim | col 1 do arquivo \| Solicitação de assistência |
| 3 | `id_chamado` | `bigint` | sim | col 2 do arquivo \| Chamado de assistência [FK -> fat_chamado_assistencia.id_chamado] |
| 4 | `id_item_empresa` | `bigint` | sim | col 3 do arquivo \| Item (cadastro por empresa) [FK -> dim_item_empresa.id_item_empresa] |
| 5 | `id_referencia` | `bigint` | sim | col 4 do arquivo \| Referência interna |
| 6 | `quantidade` | `numeric(20,8)` | sim | col 5 do arquivo \| Quantidade |
| 7 | `valor_item` | `numeric(20,8)` | sim | col 6 do arquivo \| Valor do item |
| 8 | `num_nota` | `bigint` | sim | col 7 do arquivo \| Número da nota fiscal de origem |
| 9 | `data_ocorrencia` | `date` | sim | col 8 do arquivo \| Data da ocorrência |
| 10 | `id_grupo_problema` | `bigint` | sim | col 9 do arquivo \| Grupo do problema (informado) [FK -> dim_grupo_problema_assistencia.id_grupo_problema] |
| 11 | `id_motivo_assistencia` | `bigint` | sim | col 10 do arquivo \| Motivo (informado) [FK -> dim_motivo_assistencia.id_motivo_assistencia] |
| 12 | `obs_informada` | `text` | sim | col 11 do arquivo \| Observação informada |
| 13 | `id_grupo_problema_apurado` | `bigint` | sim | col 12 do arquivo \| Grupo do problema (apurado) [FK -> dim_grupo_problema_assistencia.id_grupo_problema] |
| 14 | `id_motivo_assistencia_apurado` | `bigint` | sim | col 13 do arquivo \| Motivo (apurado) [FK -> dim_motivo_assistencia.id_motivo_assistencia] |
| 15 | `obs_apurada` | `text` | sim | col 14 do arquivo \| Observação apurada |
| 16 | `descricao_problema` | `text` | sim | col 15 do arquivo \| Descrição livre do problema e da solução |

### fat_chamado_assistencia

> Chamados de assistência técnica | origem: F_BI_F_CHAMADOS_ASSISTENCIA.TXT

`tipo: tabela | linhas (estimativa): 14,813 | tamanho: 2.0 MB`

**PK:** `id_chamado`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_empresa` | `bigint` | sim | col 0 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 2 | `num_chamado` | `bigint` | sim | col 1 do arquivo \| Número do chamado |
| 3 | `data_abertura` | `date` | sim | col 2 do arquivo \| Data de abertura |
| 4 | `id_funcionario` | `bigint` | sim | col 3 do arquivo \| Atendente responsável [FK -> dim_funcionario.id_funcionario] |
| 5 | `id_estabelecimento` | `bigint` | sim | col 4 do arquivo \| Estabelecimento do cliente [FK -> dim_estabelecimento.id_estabelecimento] |
| 6 | `id_tipo_chamado` | `bigint` | sim | col 5 do arquivo \| Tipo do chamado [FK -> dim_tipo_chamado.id_tipo_chamado] |
| 7 | `id_motivo_chamado` | `bigint` | sim | col 6 do arquivo \| Motivo do chamado [FK -> dim_motivo_chamado.id_motivo_chamado] |
| 8 | `situacao_chamado` | `text` | sim | col 7 do arquivo \| AM = em aberto, AP = aprovado (confirmar legenda) |
| 9 | 🔑`id_chamado` | `bigint` | nao | col 8 do arquivo \| Chave interna do chamado |

### fat_chamado_assistencia_texto

> Textos livres dos chamados de assistência | origem: F_BI_F_CHAMADOS_ASSISTENCIA_TEXTOS.TXT

`tipo: tabela | linhas (estimativa): 44,445 | tamanho: 5.6 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_chamado` | `bigint` | sim | col 0 do arquivo \| Chamado [FK -> fat_chamado_assistencia.id_chamado] |
| 2 | `texto_solucao` | `text` | sim | col 1 do arquivo \| Texto da solução / providência |
| 3 | `texto_reclamacao` | `text` | sim | col 2 do arquivo \| Texto da reclamação |

### fat_contrato_loja

> Contratos de venda das lojas (Focco Lojas) | origem: F_BI_F_CONTRATOS_FOCCOLOJAS.TXT

`tipo: tabela | linhas (estimativa): 31,875 | tamanho: 4.8 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_contrato` | `bigint` | sim | col 0 do arquivo \| Chave interna do contrato |
| 2 | `id_empresa` | `bigint` | sim | col 1 do arquivo \| Empresa/loja [FK -> dim_empresa.id_empresa] |
| 3 | `data_contrato` | `date` | sim | col 2 do arquivo \| Data do contrato |
| 4 | `nome_vendedor` | `text` | sim | col 3 do arquivo \| Vendedor responsável |
| 5 | `cod_contrato` | `text` | sim | col 4 do arquivo \| Código/identificação do contrato |
| 6 | `data_assinatura` | `date` | sim | col 5 do arquivo \| Data de assinatura |
| 7 | `id_cliente` | `bigint` | sim | col 6 do arquivo \| Cliente [FK -> dim_cliente.id_cliente] |
| 8 | `cpf_cliente` | `text` | sim | col 7 do arquivo \| CPF do cliente |
| 9 | `cnpj_cliente` | `text` | sim | col 8 do arquivo \| CNPJ do cliente |
| 10 | `campo_reservado_1` | `text` | sim | col 9 do arquivo \| Campo sem uso na extração |
| 11 | `campo_reservado_2` | `text` | sim | col 10 do arquivo \| Campo sem uso na extração |

### fat_contrato_loja_parcela

> Parcelas dos contratos das lojas | origem: F_BI_F_PARCELAS_CONTRATOS_FOCCOLOJAS.TXT

`tipo: tabela | linhas (estimativa): 107,970 | tamanho: 10.0 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_contrato_parcela` | `bigint` | sim | col 0 do arquivo \| Chave interna da parcela |
| 2 | `id_contrato` | `bigint` | sim | col 1 do arquivo \| Contrato [FK -> fat_contrato_loja.id_contrato] |
| 3 | `num_parcela` | `text` | sim | col 2 do arquivo \| Identificação da parcela (1A, 2A...) |
| 4 | `data_vencimento` | `date` | sim | col 3 do arquivo \| Data de vencimento |
| 5 | `valor_parcela` | `numeric(20,8)` | sim | col 4 do arquivo \| Valor da parcela |
| 6 | `forma_pagamento` | `text` | sim | col 5 do arquivo \| BOL, DEP, CAR... |
| 7 | `cod_autorizacao` | `text` | sim | col 6 do arquivo \| Código de autorização |
| 8 | `num_cartao` | `text` | sim | col 7 do arquivo \| Identificação do cartão |
| 9 | `bandeira_cartao` | `text` | sim | col 8 do arquivo \| Bandeira do cartão |
| 10 | `tipo_cartao` | `text` | sim | col 9 do arquivo \| Tipo do cartão |
| 11 | `num_documento` | `text` | sim | col 10 do arquivo \| Número do documento |
| 12 | `flag_1` | `text` | sim | col 11 do arquivo \| Indicador auxiliar |
| 13 | `observacao` | `text` | sim | col 12 do arquivo \| Observação |
| 14 | `cnpj_operadora` | `text` | sim | col 13 do arquivo \| CNPJ da operadora |
| 15 | `campo_reservado_1` | `text` | sim | col 14 do arquivo \| Campo sem uso na extração |
| 16 | `cod_banco` | `text` | sim | col 15 do arquivo \| Código do banco |
| 17 | `cod_agencia` | `text` | sim | col 16 do arquivo \| Agência |
| 18 | `cod_conta` | `text` | sim | col 17 do arquivo \| Conta |
| 19 | `valor_taxa` | `numeric(20,8)` | sim | col 18 do arquivo \| Valor de taxa/juros |

### fat_estoque_custo

> Movimentações de estoque valorizadas, com centro de custo | origem: F_BI_F_ESTOQUE_CUSTO_COMCC.TXT

`tipo: tabela | linhas (estimativa): 6,502,723 | tamanho: 832.1 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `flag_origem` | `text` | sim | col 0 do arquivo \| Indicador fixo da extração (S) |
| 2 | `id_item` | `bigint` | sim | col 1 do arquivo \| Item no catálogo global [FK -> dim_item.id_item] |
| 3 | `data_movimento` | `date` | sim | col 2 do arquivo \| Data do movimento |
| 4 | `cod_deposito` | `bigint` | sim | col 3 do arquivo \| Depósito / almoxarifado |
| 5 | `cod_classificacao` | `text` | sim | col 4 do arquivo \| Classificação do item |
| 6 | `tipo_movimento` | `text` | sim | col 5 do arquivo \| Tipo do movimento (REP...) |
| 7 | `quantidade` | `numeric(20,8)` | sim | col 6 do arquivo \| Quantidade movimentada |
| 8 | `valor_movimento` | `numeric(20,8)` | sim | col 7 do arquivo \| Valor do movimento |
| 9 | `custo_unitario` | `numeric(20,8)` | sim | col 8 do arquivo \| Custo unitário apurado |
| 10 | `cod_item` | `bigint` | sim | col 9 do arquivo \| Código do item |
| 11 | `flag_1` | `bigint` | sim | col 10 do arquivo \| Indicador auxiliar |
| 12 | `flag_2` | `bigint` | sim | col 11 do arquivo \| Indicador auxiliar |
| 13 | `id_centro_custo` | `bigint` | sim | col 12 do arquivo \| Centro de custo [FK -> dim_centro_custo.id_centro_custo] |

### fat_estoque_movimento

> Movimentações de estoque (quantidades) | origem: F_BI_F_ESTOQUE.TXT

`tipo: tabela | linhas (estimativa): 6,810,394 | tamanho: 709.0 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `flag_origem` | `text` | sim | col 0 do arquivo \| Indicador fixo da extração (S) |
| 2 | `id_item` | `bigint` | sim | col 1 do arquivo \| Item no catálogo global [FK -> dim_item.id_item] |
| 3 | `data_movimento` | `date` | sim | col 2 do arquivo \| Data do movimento |
| 4 | `cod_deposito` | `bigint` | sim | col 3 do arquivo \| Depósito / almoxarifado |
| 5 | `cod_classificacao` | `text` | sim | col 4 do arquivo \| Classificação do item |
| 6 | `tipo_movimento` | `text` | sim | col 5 do arquivo \| REP, RET, REQ, ACS, CPV, NER, NSR, TRA |
| 7 | `quantidade` | `numeric(20,8)` | sim | col 6 do arquivo \| Quantidade movimentada |
| 8 | `valor_movimento` | `numeric(20,8)` | sim | col 7 do arquivo \| Valor do movimento |
| 9 | `fator` | `numeric(20,8)` | sim | col 8 do arquivo \| Fator / sinal do movimento |
| 10 | `cod_item` | `bigint` | sim | col 9 do arquivo \| Código do item |

### fat_lancamento_conta_corrente

> Lançamentos de conta corrente | origem: F_BI_F_TLCTO_CCR.TXT

`tipo: tabela | linhas (estimativa): 79,213 | tamanho: 13.4 MB`

**PK:** `id_lancamento_ccr`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_lancamento_ccr` | `bigint` | nao | col 0 do arquivo \| Chave interna do lançamento |
| 2 | `data_lancamento` | `date` | sim | col 1 do arquivo \| Data do lançamento |
| 3 | `valor_lancamento` | `numeric(20,8)` | sim | col 2 do arquivo \| Valor do lançamento |
| 4 | `natureza` | `text` | sim | col 3 do arquivo \| D = débito, C = crédito |
| 5 | `historico` | `text` | sim | col 4 do arquivo \| Histórico do lançamento |
| 6 | `id_portador` | `bigint` | sim | col 5 do arquivo \| Portador / conta bancária [FK -> dim_portador.id_portador] |
| 7 | `id_empresa` | `bigint` | sim | col 6 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 8 | `id_conta_financeira` | `bigint` | sim | col 7 do arquivo \| Conta financeira [FK -> dim_conta_financeira.id_conta_financeira] |
| 9 | `id_conta_debito` | `bigint` | sim | col 8 do arquivo \| Conta contábil de débito |
| 10 | `id_conta_credito` | `bigint` | sim | col 9 do arquivo \| Conta contábil de crédito |
| 11 | `id_centro_custo_debito` | `bigint` | sim | col 10 do arquivo \| Centro de custo de débito [FK -> dim_centro_custo_empresa.id_centro_custo_empresa] |
| 12 | `id_centro_custo_credito` | `bigint` | sim | col 11 do arquivo \| Centro de custo de crédito [FK -> dim_centro_custo_empresa.id_centro_custo_empresa] |
| 13 | `id_referencia` | `bigint` | sim | col 12 do arquivo \| Referência interna |
| 14 | `id_tipo_lancamento_ccr` | `bigint` | sim | col 13 do arquivo \| Tipo de lançamento [FK -> dim_tipo_lancamento_ccr.id_tipo_lancamento_ccr] |

### fat_lancamento_contabil

> Lançamentos contábeis do balancete (partida dobrada) | origem: F_BI_F_TLCTO_CTAB_BALANCETE.TXT

`tipo: tabela | linhas (estimativa): 4,444,619 | tamanho: 396.4 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `data_lancamento` | `date` | sim | col 0 do arquivo \| Data do lançamento |
| 2 | `valor_lancamento` | `numeric(20,8)` | sim | col 1 do arquivo \| Valor do lançamento |
| 3 | `tipo_lancamento` | `text` | sim | col 2 do arquivo \| Tipo (CTP, TRA...) |
| 4 | `id_conta_debito` | `bigint` | sim | col 3 do arquivo \| Conta contábil de débito [FK -> dim_conta_contabil.id_conta] |
| 5 | `id_empresa_debito` | `bigint` | sim | col 4 do arquivo \| Empresa do débito [FK -> dim_empresa.id_empresa] |
| 6 | `id_conta_credito` | `bigint` | sim | col 5 do arquivo \| Conta contábil de crédito [FK -> dim_conta_contabil.id_conta] |
| 7 | `id_empresa_credito` | `bigint` | sim | col 6 do arquivo \| Empresa do crédito [FK -> dim_empresa.id_empresa] |
| 8 | `flag_1` | `bigint` | sim | col 7 do arquivo \| Indicador auxiliar |
| 9 | `flag_2` | `bigint` | sim | col 8 do arquivo \| Indicador auxiliar |

### fat_lancamento_contabil_conta

> Lançamentos contábeis por conta financeira | origem: F_BI_F_TLCTO_CTAB_BALANCETE_CONTABIL.TXT

`tipo: tabela | linhas (estimativa): 4,992,907 | tamanho: 482.1 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `data_lancamento` | `date` | sim | col 0 do arquivo \| Data do lançamento |
| 2 | `num_lancamento` | `bigint` | sim | col 1 do arquivo \| Número sequencial do lançamento no período (não é FK) |
| 3 | `tipo_lancamento` | `text` | sim | col 2 do arquivo \| Tipo (CTP...) |
| 4 | `valor_lancamento` | `numeric(20,8)` | sim | col 3 do arquivo \| Valor do lançamento |
| 5 | `id_conta_debito` | `bigint` | sim | col 4 do arquivo \| Conta contábil de débito |
| 6 | `id_conta_credito` | `bigint` | sim | col 5 do arquivo \| Conta contábil de crédito |
| 7 | `id_historico` | `bigint` | sim | col 6 do arquivo \| Histórico padrão |
| 8 | `id_empresa_debito` | `bigint` | sim | col 7 do arquivo \| Empresa do débito [FK -> dim_empresa.id_empresa] |
| 9 | `id_empresa_credito` | `bigint` | sim | col 8 do arquivo \| Empresa do crédito [FK -> dim_empresa.id_empresa] |

### fat_lancamento_contabil_transferencia

> Lançamentos contábeis de transferência entre centros de custo | origem: F_BI_F_TLCTO_CTAB_BALANCETE_TRANSFERENCIAS.TXT

`tipo: tabela | linhas (estimativa): 52,770 | tamanho: 4.9 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `data_lancamento` | `date` | sim | col 0 do arquivo \| Data do lançamento |
| 2 | `valor_lancamento` | `numeric(20,8)` | sim | col 1 do arquivo \| Valor do lançamento |
| 3 | `tipo_lancamento` | `text` | sim | col 2 do arquivo \| Tipo (TRA) |
| 4 | `id_conta_debito` | `bigint` | sim | col 3 do arquivo \| Conta contábil de débito |
| 5 | `id_empresa_debito` | `bigint` | sim | col 4 do arquivo \| Empresa do débito [FK -> dim_empresa.id_empresa] |
| 6 | `id_conta_credito` | `bigint` | sim | col 5 do arquivo \| Conta contábil de crédito |
| 7 | `id_empresa_credito` | `bigint` | sim | col 6 do arquivo \| Empresa do crédito [FK -> dim_empresa.id_empresa] |
| 8 | `id_centro_custo_empresa` | `bigint` | sim | col 7 do arquivo \| Centro de custo [FK -> dim_centro_custo_empresa.id_centro_custo_empresa] |
| 9 | `id_referencia` | `bigint` | sim | col 8 do arquivo \| Referência interna |

### fat_lancamento_contabil_transferencia_conta

> Lançamentos contábeis de transferência entre contas | origem: F_BI_F_TLCTO_CTAB_BALANCETE_TRANSFERENCIAS_CONTA.TXT

`tipo: tabela | linhas (estimativa): 55,836 | tamanho: 4.2 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `data_lancamento` | `date` | sim | col 0 do arquivo \| Data do lançamento |
| 2 | `valor_lancamento` | `numeric(20,8)` | sim | col 1 do arquivo \| Valor do lançamento |
| 3 | `tipo_lancamento` | `text` | sim | col 2 do arquivo \| Tipo (TRA) |
| 4 | `id_conta_debito` | `bigint` | sim | col 3 do arquivo \| Conta contábil de débito |
| 5 | `id_empresa_debito` | `bigint` | sim | col 4 do arquivo \| Empresa do débito [FK -> dim_empresa.id_empresa] |
| 6 | `id_conta_credito` | `bigint` | sim | col 5 do arquivo \| Conta contábil de crédito |
| 7 | `id_empresa_credito` | `bigint` | sim | col 6 do arquivo \| Empresa do crédito [FK -> dim_empresa.id_empresa] |

### fat_movimento_pagar

> Histórico de movimentos de contas a pagar | origem: F_BI_F_THIST_MOV_CP.TXT

`tipo: tabela | linhas (estimativa): 1,654,302 | tamanho: 172.9 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_titulo_pagar` | `bigint` | sim | col 0 do arquivo \| Título a pagar [FK -> fat_titulo_pagar.id_titulo_pagar] |
| 2 | `id_movimento` | `bigint` | sim | col 1 do arquivo \| Chave interna do movimento |
| 3 | `num_parcela` | `bigint` | sim | col 2 do arquivo \| Parcela |
| 4 | `data_movimento` | `date` | sim | col 3 do arquivo \| Data do movimento |
| 5 | `valor_titulo` | `numeric(20,8)` | sim | col 4 do arquivo \| Valor do título |
| 6 | `valor_movimento` | `numeric(20,8)` | sim | col 5 do arquivo \| Valor do movimento |
| 7 | `valor_juros` | `numeric(20,8)` | sim | col 6 do arquivo \| Juros |
| 8 | `valor_desconto` | `numeric(20,8)` | sim | col 7 do arquivo \| Desconto |
| 9 | `id_tipo_lancamento_cp` | `bigint` | sim | col 8 do arquivo \| Tipo de lançamento [FK -> dim_tipo_lancamento_cp.id_tipo_lancamento_cp] |
| 10 | `id_portador` | `bigint` | sim | col 9 do arquivo \| Portador [FK -> dim_portador.id_portador] |
| 11 | `cod_referencia` | `bigint` | sim | col 10 do arquivo \| Referência interna |
| 12 | `valor_auxiliar` | `numeric(20,8)` | sim | col 11 do arquivo \| Valor auxiliar |

### fat_movimento_receber

> Histórico de movimentos de contas a receber | origem: F_BI_F_THIST_MOV_CR.TXT

`tipo: tabela | linhas (estimativa): 1,183,875 | tamanho: 145.6 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_titulo_receber` | `bigint` | sim | col 0 do arquivo \| Título a receber |
| 2 | `id_movimento` | `bigint` | sim | col 1 do arquivo \| Chave interna do movimento |
| 3 | `num_parcela` | `bigint` | sim | col 2 do arquivo \| Parcela |
| 4 | `data_movimento` | `date` | sim | col 3 do arquivo \| Data do movimento |
| 5 | `valor_titulo` | `numeric(20,8)` | sim | col 4 do arquivo \| Valor do título |
| 6 | `valor_movimento` | `numeric(20,8)` | sim | col 5 do arquivo \| Valor do movimento |
| 7 | `valor_juros` | `numeric(20,8)` | sim | col 6 do arquivo \| Juros |
| 8 | `valor_multa` | `numeric(20,8)` | sim | col 7 do arquivo \| Multa |
| 9 | `valor_desconto` | `numeric(20,8)` | sim | col 8 do arquivo \| Desconto |
| 10 | `id_tipo_lancamento_cr` | `bigint` | sim | col 9 do arquivo \| Tipo de lançamento [FK -> dim_tipo_lancamento_cr.id_tipo_lancamento_cr] |
| 11 | `id_portador` | `bigint` | sim | col 10 do arquivo \| Portador [FK -> dim_portador.id_portador] |
| 12 | `flag_1` | `bigint` | sim | col 11 do arquivo \| Indicador auxiliar |
| 13 | `cod_referencia` | `bigint` | sim | col 12 do arquivo \| Referência interna |
| 14 | `id_movimento_origem` | `bigint` | sim | col 13 do arquivo \| Movimento de origem |
| 15 | `data_credito` | `date` | sim | col 14 do arquivo \| Data de crédito |

### fat_nota_entrada

> Capa da nota fiscal de entrada | origem: F_BI_F_NOTA_ENTRADA.TXT

`tipo: tabela | linhas (estimativa): 188,866 | tamanho: 26.0 MB`

**PK:** `id_nota_entrada`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_nota_entrada` | `bigint` | nao | col 0 do arquivo \| Chave interna da NF de entrada |
| 2 | `id_empresa` | `bigint` | sim | col 1 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 3 | `serie_nota` | `text` | sim | col 2 do arquivo \| Série da nota |
| 4 | `num_nota` | `bigint` | sim | col 3 do arquivo \| Número da nota fiscal |
| 5 | `id_fornecedor` | `bigint` | sim | col 4 do arquivo \| Fornecedor [FK -> dim_fornecedor.id_fornecedor] |
| 6 | `data_emissao` | `date` | sim | col 5 do arquivo \| Data de emissão |
| 7 | `data_entrada` | `date` | sim | col 6 do arquivo \| Data de entrada |
| 8 | `data_cancelamento` | `date` | sim | col 7 do arquivo \| Data de cancelamento |
| 9 | `flag_cancelada` | `bigint` | sim | col 8 do arquivo \| Indicador de cancelamento |
| 10 | `cod_situacao` | `text` | sim | col 9 do arquivo \| Situação detalhada |
| 11 | `id_tipo_nf_entrada` | `bigint` | sim | col 10 do arquivo \| Tipo de NF de entrada [FK -> dim_tipo_nf_entrada.id_tipo_nf_entrada] |
| 12 | `valor_produtos` | `numeric(20,8)` | sim | col 11 do arquivo \| Valor dos produtos |
| 13 | `valor_total` | `numeric(20,8)` | sim | col 12 do arquivo \| Valor total da nota |

### fat_nota_entrada_item

> Itens da nota fiscal de entrada | origem: F_BI_F_NOTA_ENTRADA_IT.TXT

`tipo: tabela | linhas (estimativa): 376,948 | tamanho: 52.8 MB`

**PK:** `id_nota_entrada_item`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_nota_entrada_item` | `bigint` | nao | col 0 do arquivo \| Chave interna do item |
| 2 | `id_nota_entrada` | `bigint` | sim | col 1 do arquivo \| Nota fiscal de entrada [FK -> fat_nota_entrada.id_nota_entrada] |
| 3 | `num_item` | `bigint` | sim | col 2 do arquivo \| Sequência do item |
| 4 | `id_tipo_nf_entrada` | `bigint` | sim | col 3 do arquivo \| Tipo de NF / natureza [FK -> dim_tipo_nf_entrada.id_tipo_nf_entrada] |
| 5 | `valor_total` | `numeric(20,8)` | sim | col 4 do arquivo \| Valor total do item |
| 6 | `valor_ipi` | `numeric(20,8)` | sim | col 5 do arquivo \| Valor de IPI |
| 7 | `valor_icms` | `numeric(20,8)` | sim | col 6 do arquivo \| Valor de ICMS |
| 8 | `valor_produtos` | `numeric(20,8)` | sim | col 7 do arquivo \| Valor dos produtos |
| 9 | `id_item` | `bigint` | sim | col 8 do arquivo \| Item no catálogo global [FK -> dim_item.id_item] |
| 10 | `cod_item` | `text` | sim | col 9 do arquivo \| Código do item |
| 11 | `cod_classificacao` | `text` | sim | col 10 do arquivo \| Classificação do item |
| 12 | `quantidade` | `numeric(20,8)` | sim | col 11 do arquivo \| Quantidade recebida |

### fat_nota_entrada_item_origem

> Documentos de origem de cada item de NF de entrada. Um mesmo item aparece em mais de uma linha (7.328 casos), por isso ficou separado de fat_nota_entrada_item: somar valores aqui duplicaria as compras. ATENÇÃO: as duas colunas de código NÃO batem com fat_pedido_compra — confirmar o significado com o time do ERP antes de usar. | origem: F_BI_F_NOTA_ENTRADA_IT.TXT

`tipo: tabela | linhas (estimativa): 1,152,990 | tamanho: 57.4 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_nota_entrada_item` | `bigint` | sim | col 0 do arquivo \| Item da NF de entrada [FK -> fat_nota_entrada_item.id_nota_entrada_item] |
| 2 | `cod_documento_origem` | `bigint` | sim | col 1 do arquivo \| Código do documento de origem — NÃO CONFIRMADO |
| 3 | `cod_item_origem` | `bigint` | sim | col 2 do arquivo \| Código do item no documento de origem — NÃO CONFIRMADO |

### fat_nota_saida

> Capa da nota fiscal de saída (faturamento) | origem: F_BI_F_NOTA_SAIDA.TXT

`tipo: tabela | linhas (estimativa): 132,379 | tamanho: 15.9 MB`

**PK:** `id_nota_saida`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_nota_saida` | `bigint` | nao | col 0 do arquivo \| Chave interna da NF de saída |
| 2 | `id_empresa` | `bigint` | sim | col 1 do arquivo \| Empresa emitente [FK -> dim_empresa.id_empresa] |
| 3 | `cod_transportadora` | `bigint` | sim | col 2 do arquivo \| Transportadora / série — CONFIRMAR com o ERP |
| 4 | `num_nota` | `bigint` | sim | col 3 do arquivo \| Número da nota fiscal |
| 5 | `id_cliente` | `bigint` | sim | col 4 do arquivo \| Cliente [FK -> dim_cliente.id_cliente] |
| 6 | `data_emissao` | `date` | sim | col 5 do arquivo \| Data de emissão |
| 7 | `data_saida` | `date` | sim | col 6 do arquivo \| Data de saída |
| 8 | `id_estabelecimento` | `bigint` | sim | col 7 do arquivo \| Estabelecimento de entrega [FK -> dim_estabelecimento.id_estabelecimento] |
| 9 | `id_representante` | `bigint` | sim | col 8 do arquivo \| Representante [FK -> dim_representante.id_representante] |
| 10 | `situacao_nota` | `text` | sim | col 9 do arquivo \| I, G, C |

### fat_nota_saida_item

> Itens da nota fiscal de saída | origem: F_BI_F_NOTA_SAIDA_IT.TXT

`tipo: tabela | linhas (estimativa): 253,997 | tamanho: 35.2 MB`

**PK:** `id_nota_saida_item`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_nota_saida_item` | `bigint` | nao | col 0 do arquivo \| Chave interna do item da NF |
| 2 | `id_nota_saida` | `bigint` | sim | col 1 do arquivo \| Nota fiscal de saída [FK -> fat_nota_saida.id_nota_saida] |
| 3 | `num_item` | `bigint` | sim | col 2 do arquivo \| Sequência do item |
| 4 | `id_item_empresa` | `bigint` | sim | col 3 do arquivo \| Item (cadastro por empresa) [FK -> dim_item_empresa.id_item_empresa] |
| 5 | `quantidade` | `numeric(20,8)` | sim | col 4 do arquivo \| Quantidade faturada |
| 6 | `valor_bruto` | `numeric(20,8)` | sim | col 5 do arquivo \| Valor bruto do item |
| 7 | `id_tipo_nf_saida` | `bigint` | sim | col 6 do arquivo \| Tipo de NF / natureza [FK -> dim_tipo_nf_saida.id_tipo_nf_saida] |
| 8 | `valor_ipi` | `numeric(20,8)` | sim | col 7 do arquivo \| Valor de IPI |
| 9 | `valor_icms` | `numeric(20,8)` | sim | col 8 do arquivo \| Valor de ICMS |
| 10 | `valor_desconto` | `numeric(20,8)` | sim | col 9 do arquivo \| Valor de desconto |
| 11 | `valor_liquido` | `numeric(20,8)` | sim | col 10 do arquivo \| Valor líquido do item |
| 12 | `id_item` | `bigint` | sim | col 11 do arquivo \| Item no catálogo global [FK -> dim_item.id_item] |
| 13 | `id_referencia_pedido` | `bigint` | sim | col 12 do arquivo \| Referência ao pedido/OF de origem |

### fat_nota_saida_item_pedido

> Itens da NF de saída com vínculo ao pedido de origem | origem: F_BI_F_NOTA_SAIDA_IT_VINCULOPEDIDO.TXT

`tipo: tabela | linhas (estimativa): 562,914 | tamanho: 62.2 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_nota_saida_item` | `bigint` | sim | col 0 do arquivo \| Item da NF de saída [FK -> fat_nota_saida_item.id_nota_saida_item] |
| 2 | `id_nota_saida` | `bigint` | sim | col 1 do arquivo \| Nota fiscal de saída [FK -> fat_nota_saida.id_nota_saida] |
| 3 | `num_item` | `bigint` | sim | col 2 do arquivo \| Sequência do item |
| 4 | `id_item_empresa` | `bigint` | sim | col 3 do arquivo \| Item (cadastro por empresa) [FK -> dim_item_empresa.id_item_empresa] |
| 5 | `quantidade` | `numeric(20,8)` | sim | col 4 do arquivo \| Quantidade |
| 6 | `valor_bruto` | `numeric(20,8)` | sim | col 5 do arquivo \| Valor bruto |
| 7 | `id_tipo_nf_saida` | `bigint` | sim | col 6 do arquivo \| Tipo de NF [FK -> dim_tipo_nf_saida.id_tipo_nf_saida] |
| 8 | `id_pedido` | `bigint` | sim | col 7 do arquivo \| Pedido de origem [FK -> fat_pedido.id_pedido] |
| 9 | `valor_ipi` | `numeric(20,8)` | sim | col 8 do arquivo \| Valor de IPI |
| 10 | `valor_icms` | `numeric(20,8)` | sim | col 9 do arquivo \| Valor de ICMS |
| 11 | `valor_desconto` | `numeric(20,8)` | sim | col 10 do arquivo \| Valor de desconto |
| 12 | `valor_liquido` | `numeric(20,8)` | sim | col 11 do arquivo \| Valor líquido |

### fat_nota_saida_item_pontuacao

> Pontuação de produção associada aos itens faturados | origem: F_BI_F_NOTA_SAIDA_ITENS_PONTUACAO_ORDEMPRODUCAO.TXT

`tipo: tabela | linhas (estimativa): 1,116,354 | tamanho: 72.8 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_ordem_fabricacao` | `bigint` | sim | col 0 do arquivo \| Ordem de fabricação |
| 2 | `id_nota_saida_item` | `bigint` | sim | col 1 do arquivo \| Item da NF de saída [FK -> fat_nota_saida_item.id_nota_saida_item] |
| 3 | `id_nota_saida` | `bigint` | sim | col 2 do arquivo \| Nota fiscal de saída [FK -> fat_nota_saida.id_nota_saida] |
| 4 | `pontuacao` | `bigint` | sim | col 3 do arquivo \| Pontos apurados |
| 5 | `cod_faixa_pontuacao` | `text` | sim | col 4 do arquivo \| Faixa de pontuação (P70, P130...) |

### fat_ordem_fabricacao

> Ordens de fabricação | origem: F_BI_D_ORDENS_FABRICACAO.TXT

`tipo: tabela | linhas (estimativa): 618,358 | tamanho: 116.0 MB`

**PK:** `id_ordem_fabricacao`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_ordem_fabricacao` | `bigint` | nao | col 0 do arquivo \| Chave interna da ordem |
| 2 | `num_ordem` | `bigint` | sim | col 1 do arquivo \| Número da ordem |
| 3 | `origem_ordem` | `text` | sim | col 2 do arquivo \| L = livre, F = firme |
| 4 | `tipo_ordem` | `text` | sim | col 3 do arquivo \| Tipo da ordem (OFE) |
| 5 | `id_empresa` | `bigint` | sim | col 4 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 6 | `cod_situacao` | `bigint` | sim | col 5 do arquivo \| Código de situação |
| 7 | `data_abertura` | `date` | sim | col 6 do arquivo \| Data de abertura |
| 8 | `data_prevista_fim` | `date` | sim | col 7 do arquivo \| Data prevista de término |
| 9 | `data_inicio` | `date` | sim | col 8 do arquivo \| Data de início |
| 10 | `data_fim` | `date` | sim | col 9 do arquivo \| Data de término |
| 11 | `data_entrega` | `date` | sim | col 10 do arquivo \| Data de entrega |
| 12 | `quantidade_prevista` | `numeric(20,8)` | sim | col 11 do arquivo \| Quantidade prevista |
| 13 | `quantidade_produzida` | `numeric(20,8)` | sim | col 12 do arquivo \| Quantidade produzida |
| 14 | `quantidade_refugada` | `numeric(20,8)` | sim | col 13 do arquivo \| Quantidade refugada |
| 15 | `quantidade_cancelada` | `numeric(20,8)` | sim | col 14 do arquivo \| Quantidade cancelada |
| 16 | `flag_encerrada` | `bigint` | sim | col 15 do arquivo \| Indicador de encerramento |
| 17 | `cod_prioridade` | `bigint` | sim | col 16 do arquivo \| Prioridade |
| 18 | `id_referencia_producao` | `bigint` | sim | col 17 do arquivo \| Referência interna de produção — CONFIRMAR com o ERP |
| 19 | `id_item_ordem` | `bigint` | sim | col 18 do arquivo \| Item produzido (visão produção) [FK -> dim_item_ordem.id_item_ordem] |
| 20 | `id_mascara` | `bigint` | sim | col 19 do arquivo \| Máscara de configuração do produto [FK -> dim_mascara.id_mascara] |
| 21 | `cod_linha_producao` | `bigint` | sim | col 20 do arquivo \| Linha/setor de produção — CONFIRMAR com o ERP |
| 22 | `flag_1` | `bigint` | sim | col 21 do arquivo \| Indicador auxiliar |
| 23 | `cod_referencia` | `bigint` | sim | col 22 do arquivo \| Referência interna |

### fat_ordem_movimento

> Apontamentos de produção nas operações do roteiro | origem: F_BI_D_ORDENS_MOVIMENTOS.TXT

`tipo: tabela | linhas (estimativa): 3,425,536 | tamanho: 950.5 MB`

**PK:** `id_ordem_movimento`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_ordem_movimento` | `bigint` | nao | col 0 do arquivo \| Chave interna do apontamento |
| 2 | `quantidade` | `numeric(20,8)` | sim | col 1 do arquivo \| Quantidade apontada |
| 3 | `tipo_apontamento` | `text` | sim | col 2 do arquivo \| Tipo (TP) |
| 4 | `tempo_apontado` | `numeric(20,8)` | sim | col 3 do arquivo \| Tempo apontado |
| 5 | `texto_1` | `text` | sim | col 4 do arquivo \| Campo texto sem uso na extração |
| 6 | `texto_2` | `text` | sim | col 5 do arquivo \| Campo texto sem uso na extração |
| 7 | `texto_3` | `text` | sim | col 6 do arquivo \| Campo texto sem uso na extração |
| 8 | `flag_1` | `bigint` | sim | col 7 do arquivo \| Indicador auxiliar |
| 9 | `data_apontamento` | `date` | sim | col 8 do arquivo \| Data do apontamento |
| 10 | `id_ordem_roteiro` | `bigint` | sim | col 9 do arquivo \| Operação do roteiro [FK -> fat_ordem_roteiro.id_ordem_roteiro] |
| 11 | `usuario_apontamento` | `text` | sim | col 10 do arquivo \| Usuário / estação do apontamento |
| 12 | `texto_4` | `text` | sim | col 11 do arquivo \| Campo texto sem uso na extração |
| 13 | `texto_5` | `text` | sim | col 12 do arquivo \| Campo texto sem uso na extração |
| 14 | `tipo_movimento` | `text` | sim | col 13 do arquivo \| E = entrada, S = saída |
| 15 | `id_referencia_producao` | `bigint` | sim | col 14 do arquivo \| Referência interna de produção — CONFIRMAR com o ERP |
| 16 | `cod_auxiliar` | `bigint` | sim | col 15 do arquivo \| Código auxiliar |
| 17 | `valor_auxiliar_1` | `numeric(20,8)` | sim | col 16 do arquivo \| Valor auxiliar |
| 18 | `flag_2` | `bigint` | sim | col 17 do arquivo \| Indicador auxiliar |
| 19 | `flag_3` | `bigint` | sim | col 18 do arquivo \| Indicador auxiliar |
| 20 | `flag_4` | `bigint` | sim | col 19 do arquivo \| Indicador auxiliar |
| 21 | `flag_5` | `bigint` | sim | col 20 do arquivo \| Indicador auxiliar |
| 22 | `flag_6` | `bigint` | sim | col 21 do arquivo \| Indicador auxiliar |
| 23 | `valor_auxiliar_2` | `numeric(20,8)` | sim | col 22 do arquivo \| Valor auxiliar |
| 24 | `valor_auxiliar_3` | `numeric(20,8)` | sim | col 23 do arquivo \| Valor auxiliar |
| 25 | `flag_7` | `bigint` | sim | col 24 do arquivo \| Indicador auxiliar |
| 26 | `flag_8` | `bigint` | sim | col 25 do arquivo \| Indicador auxiliar |
| 27 | `flag_9` | `bigint` | sim | col 26 do arquivo \| Indicador auxiliar |
| 28 | `flag_10` | `bigint` | sim | col 27 do arquivo \| Indicador auxiliar |
| 29 | `valor_auxiliar_4` | `numeric(20,8)` | sim | col 28 do arquivo \| Valor auxiliar |
| 30 | `flag_12` | `bigint` | sim | col 29 do arquivo \| Indicador auxiliar |
| 31 | `texto_6` | `text` | sim | col 30 do arquivo \| Campo texto sem uso na extração |
| 32 | `valor_auxiliar_5` | `numeric(20,8)` | sim | col 31 do arquivo \| Valor auxiliar |
| 33 | `valor_auxiliar_6` | `numeric(20,8)` | sim | col 32 do arquivo \| Valor auxiliar |

### fat_ordem_roteiro

> Roteiro (operações) das ordens de fabricação | origem: F_BI_D_ORDENS_ROTEIRO.TXT

`tipo: tabela | linhas (estimativa): 3,695,097 | tamanho: 1.2 GB`

**PK:** `id_ordem_roteiro`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_ordem_roteiro` | `bigint` | nao | col 0 do arquivo \| Chave interna da operação da ordem |
| 2 | `num_operacao` | `bigint` | sim | col 1 do arquivo \| Sequência da operação (10, 20, 30...) |
| 3 | `tempo_previsto` | `numeric(20,8)` | sim | col 2 do arquivo \| Tempo previsto |
| 4 | `tempo_realizado` | `numeric(20,8)` | sim | col 3 do arquivo \| Tempo realizado |
| 5 | `tempo_setup` | `numeric(20,8)` | sim | col 4 do arquivo \| Tempo de setup |
| 6 | `cod_tipo_roteiro` | `bigint` | sim | col 5 do arquivo \| Tipo de roteiro |
| 7 | `id_ordem_fabricacao` | `bigint` | sim | col 6 do arquivo \| Ordem de fabricação [FK -> fat_ordem_fabricacao.id_ordem_fabricacao] |
| 8 | `flag_1` | `bigint` | sim | col 7 do arquivo \| Indicador auxiliar |
| 9 | `flag_2` | `bigint` | sim | col 8 do arquivo \| Indicador auxiliar |
| 10 | `id_operacao` | `bigint` | sim | col 9 do arquivo \| Operação executada [FK -> dim_operacao.id_operacao] |
| 11 | `cod_empresa` | `bigint` | sim | col 10 do arquivo \| Empresa |
| 12 | `id_referencia` | `bigint` | sim | col 11 do arquivo \| Referência interna |
| 13 | `texto_1` | `text` | sim | col 12 do arquivo \| Campo texto sem uso na extração |
| 14 | `texto_2` | `text` | sim | col 13 do arquivo \| Campo texto sem uso na extração |
| 15 | `cod_status` | `text` | sim | col 14 do arquivo \| Status da operação |
| 16 | `flag_3` | `bigint` | sim | col 15 do arquivo \| Indicador auxiliar |
| 17 | `id_referencia_2` | `bigint` | sim | col 16 do arquivo \| Referência interna 2 |
| 18 | `id_centro_trabalho` | `bigint` | sim | col 17 do arquivo \| Centro de trabalho [FK -> dim_centro_trabalho.id_centro_trabalho] |
| 19 | `cod_auxiliar_1` | `bigint` | sim | col 18 do arquivo \| Código auxiliar |
| 20 | `valor_auxiliar_1` | `numeric(20,8)` | sim | col 19 do arquivo \| Valor auxiliar |
| 21 | `flag_4` | `bigint` | sim | col 20 do arquivo \| Indicador auxiliar |
| 22 | `flag_5` | `bigint` | sim | col 21 do arquivo \| Indicador auxiliar |
| 23 | `flag_6` | `bigint` | sim | col 22 do arquivo \| Indicador auxiliar |
| 24 | `flag_7` | `bigint` | sim | col 23 do arquivo \| Indicador auxiliar |
| 25 | `flag_8` | `bigint` | sim | col 24 do arquivo \| Indicador auxiliar |
| 26 | `flag_9` | `bigint` | sim | col 25 do arquivo \| Indicador auxiliar |
| 27 | `flag_10` | `bigint` | sim | col 26 do arquivo \| Indicador auxiliar |
| 28 | `valor_auxiliar_2` | `numeric(20,8)` | sim | col 27 do arquivo \| Valor auxiliar |
| 29 | `usuario_inclusao` | `text` | sim | col 28 do arquivo \| Usuário / estação de inclusão |
| 30 | `data_inclusao` | `date` | sim | col 29 do arquivo \| Data de inclusão |
| 31 | `usuario_alteracao` | `text` | sim | col 30 do arquivo \| Usuário / estação da última alteração |
| 32 | `data_alteracao` | `date` | sim | col 31 do arquivo \| Data da última alteração |

### fat_pedido

> Capa do pedido de venda | origem: F_BI_F_PEDIDO.TXT

`tipo: tabela | linhas (estimativa): 202,918 | tamanho: 39.7 MB`

**PK:** `id_pedido`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_pedido` | `bigint` | nao | col 0 do arquivo \| Chave interna do pedido |
| 2 | `num_pedido` | `bigint` | sim | col 1 do arquivo \| Número do pedido |
| 3 | `id_empresa` | `bigint` | sim | col 2 do arquivo \| Empresa emitente [FK -> dim_empresa.id_empresa] |
| 4 | `data_emissao` | `date` | sim | col 3 do arquivo \| Data de emissão |
| 5 | `data_entrega_prevista` | `date` | sim | col 4 do arquivo \| Data de entrega prevista |
| 6 | `situacao_pedido` | `text` | sim | col 5 do arquivo \| PE = pendente, A = atendido, C = cancelado, AC = atendido/cancelado |
| 7 | `id_estabelecimento` | `bigint` | sim | col 6 do arquivo \| Estabelecimento de entrega/cobrança [FK -> dim_estabelecimento.id_estabelecimento] |
| 8 | `origem_pedido` | `text` | sim | col 7 do arquivo \| SIM, PDV, EXP, ORC |
| 9 | `valor_desconto` | `numeric(20,8)` | sim | col 8 do arquivo \| Valor de desconto |
| 10 | `valor_bruto` | `numeric(20,8)` | sim | col 9 do arquivo \| Valor bruto do pedido |
| 11 | `valor_liquido` | `numeric(20,8)` | sim | col 10 do arquivo \| Valor líquido do pedido |
| 12 | `id_empresa_faturamento` | `bigint` | sim | col 11 do arquivo \| Empresa de faturamento [FK -> dim_empresa.id_empresa] |
| 13 | `id_tipo_nf_saida` | `bigint` | sim | col 12 do arquivo \| Tipo de NF prevista [FK -> dim_tipo_nf_saida.id_tipo_nf_saida] |
| 14 | `id_representante` | `bigint` | sim | col 13 do arquivo \| Representante [FK -> dim_representante.id_representante] |
| 15 | `cod_tipo_frete` | `text` | sim | col 14 do arquivo \| Código auxiliar (frete/transportadora) — CONFIRMAR com o ERP |
| 16 | `pedido_cliente` | `text` | sim | col 15 do arquivo \| Número do pedido no cliente |
| 17 | `cod_referencia` | `bigint` | sim | col 16 do arquivo \| Referência interna |
| 18 | `status_liberacao` | `text` | sim | col 17 do arquivo \| LIB = liberado, BLQ = bloqueado |
| 19 | `cod_situacao_detalhe` | `text` | sim | col 18 do arquivo \| Situação detalhada (S, O, N, L, A, C, X, F) |
| 20 | `id_condicao_pagamento` | `bigint` | sim | col 19 do arquivo \| Condição de pagamento [FK -> dim_condicao_pagamento.id_condicao_pagamento] |
| 21 | `valor_auxiliar` | `numeric(20,8)` | sim | col 20 do arquivo \| Valor auxiliar |
| 22 | `data_inclusao` | `date` | sim | col 21 do arquivo \| Data de inclusão/digitação |
| 23 | `flag_auxiliar` | `bigint` | sim | col 22 do arquivo \| Indicador auxiliar |

### fat_pedido_compra

> Capa do pedido de compra | origem: F_BI_F_PEDIDO_COMPRA.TXT

`tipo: tabela | linhas (estimativa): 50,130 | tamanho: 5.8 MB`

**PK:** `id_pedido_compra`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_pedido_compra` | `bigint` | nao | col 0 do arquivo \| Chave interna do pedido de compra |
| 2 | `num_pedido_compra` | `bigint` | sim | col 1 do arquivo \| Número do pedido de compra |
| 3 | `data_emissao` | `date` | sim | col 2 do arquivo \| Data de emissão |
| 4 | `situacao` | `text` | sim | col 3 do arquivo \| Situação (A = ativo) |
| 5 | `id_fornecedor` | `bigint` | sim | col 4 do arquivo \| Fornecedor [FK -> dim_fornecedor.id_fornecedor] |
| 6 | `id_fornecedor_entrega` | `bigint` | sim | col 5 do arquivo \| Fornecedor de entrega [FK -> dim_fornecedor.id_fornecedor] |
| 7 | `id_empresa` | `bigint` | sim | col 6 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 8 | `cod_referencia` | `bigint` | sim | col 7 do arquivo \| Referência interna |
| 9 | `tipo_pedido_compra` | `text` | sim | col 8 do arquivo \| Tipo (OCL...) |
| 10 | `origem` | `text` | sim | col 9 do arquivo \| Origem (I...) |

### fat_pedido_compra_item

> Itens do pedido de compra | origem: F_BI_F_PEDIDO_COMPRA_ITEM.TXT

`tipo: tabela | linhas (estimativa): 171,873 | tamanho: 31.1 MB`

**PK:** `id_pedido_compra_item`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_pedido_compra_item` | `bigint` | nao | col 0 do arquivo \| Chave interna do item |
| 2 | `id_pedido_compra` | `bigint` | sim | col 1 do arquivo \| Pedido de compra [FK -> fat_pedido_compra.id_pedido_compra] |
| 3 | `quantidade` | `numeric(20,8)` | sim | col 2 do arquivo \| Quantidade pedida |
| 4 | `quantidade_saldo` | `numeric(20,8)` | sim | col 3 do arquivo \| Saldo a receber |
| 5 | `quantidade_recebida` | `numeric(20,8)` | sim | col 4 do arquivo \| Quantidade recebida |
| 6 | `quantidade_cancelada` | `numeric(20,8)` | sim | col 5 do arquivo \| Quantidade cancelada |
| 7 | `valor_unitario` | `numeric(20,8)` | sim | col 6 do arquivo \| Valor unitário |
| 8 | `id_item` | `bigint` | sim | col 7 do arquivo \| Item no catálogo global [FK -> dim_item.id_item] |
| 9 | `cod_item` | `bigint` | sim | col 8 do arquivo \| Código do item |
| 10 | `id_unidade` | `bigint` | sim | col 9 do arquivo \| Unidade de medida [FK -> dim_unidade_medida.id_unidade] |
| 11 | `situacao` | `text` | sim | col 10 do arquivo \| Situação do item |
| 12 | `valor_total` | `numeric(20,8)` | sim | col 11 do arquivo \| Valor total do item |
| 13 | `valor_total_liquido` | `numeric(20,8)` | sim | col 12 do arquivo \| Valor total líquido |
| 14 | `valor_total_com_impostos` | `numeric(20,8)` | sim | col 13 do arquivo \| Valor total com impostos |
| 15 | `data_entrega_prevista` | `date` | sim | col 14 do arquivo \| Data de entrega prevista |
| 16 | `data_necessidade` | `date` | sim | col 15 do arquivo \| Data de necessidade |
| 17 | `origem` | `text` | sim | col 16 do arquivo \| Origem do item |
| 18 | `valor_unitario_liquido` | `numeric(20,8)` | sim | col 17 do arquivo \| Valor unitário líquido |
| 19 | `valor_total_geral` | `numeric(20,8)` | sim | col 18 do arquivo \| Valor total geral |
| 20 | `id_funcionario_comprador` | `bigint` | sim | col 19 do arquivo \| Comprador responsável [FK -> dim_funcionario.id_funcionario] |
| 21 | `cod_classificacao` | `text` | sim | col 20 do arquivo \| Classificação do item (ex.: 40.100.700.0002) |

### fat_pedido_item

> Itens do pedido de venda | origem: F_BI_F_PEDIDO_ITEM.TXT

`tipo: tabela | linhas (estimativa): 379,702 | tamanho: 59.6 MB`

**PK:** `id_pedido_item`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_pedido` | `bigint` | sim | col 0 do arquivo \| Pedido [FK -> fat_pedido.id_pedido] |
| 2 | 🔑`id_pedido_item` | `bigint` | nao | col 1 do arquivo \| Chave interna do item do pedido |
| 3 | `num_item` | `bigint` | sim | col 2 do arquivo \| Sequência do item no pedido |
| 4 | `cod_item` | `bigint` | sim | col 3 do arquivo \| Código do item |
| 5 | `quantidade` | `numeric(20,8)` | sim | col 4 do arquivo \| Quantidade pedida |
| 6 | `valor_unitario` | `numeric(20,8)` | sim | col 5 do arquivo \| Valor unitário |
| 7 | `valor_unitario_liquido` | `numeric(20,8)` | sim | col 6 do arquivo \| Valor unitário líquido |
| 8 | `percentual_desconto` | `numeric(20,8)` | sim | col 7 do arquivo \| Percentual de desconto/IPI |
| 9 | `id_item_empresa` | `bigint` | sim | col 8 do arquivo \| Item (cadastro por empresa) [FK -> dim_item_empresa.id_item_empresa] |
| 10 | `quantidade_saldo` | `numeric(20,8)` | sim | col 9 do arquivo \| Saldo a atender |
| 11 | `quantidade_cancelada` | `numeric(20,8)` | sim | col 10 do arquivo \| Quantidade cancelada |
| 12 | `id_empresa` | `bigint` | sim | col 11 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 13 | `num_pedido` | `bigint` | sim | col 12 do arquivo \| Número do pedido |
| 14 | `origem_pedido` | `text` | sim | col 13 do arquivo \| SIM, PDV, EXP |
| 15 | `id_mascara` | `bigint` | sim | col 14 do arquivo \| Máscara de configuração do produto [FK -> dim_mascara.id_mascara] |
| 16 | `flag_auxiliar` | `bigint` | sim | col 15 do arquivo \| Indicador auxiliar |

### fat_pedido_representante_secundario

> Rateio de comissão entre representantes secundários DE CADA PEDIDO. Grão = pedido x representante (o mesmo pedido aparece em várias linhas). | origem: F_BI_D_REPRESENTANTE_SECUNDARIO.TXT

`tipo: tabela | linhas (estimativa): 2,880 | tamanho: 280.0 KB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_pedido` | `bigint` | sim | col 0 do arquivo \| Pedido de venda rateado [FK -> fat_pedido.id_pedido] |
| 2 | `id_representante` | `bigint` | sim | col 1 do arquivo \| Representante que participa do rateio [FK -> dim_representante.id_representante] |
| 3 | `cod_representante` | `bigint` | sim | col 2 do arquivo \| Código do representante |
| 4 | `nome_representante` | `text` | sim | col 3 do arquivo \| Nome do representante |
| 5 | `percentual_participacao` | `numeric(20,8)` | sim | col 4 do arquivo \| Percentual de participação na comissão |

### fat_pontuacao_producao

> Pontuação de produção por item | origem: F_BI_F_PONTUACAO_PRODUCAO.TXT

`tipo: tabela | linhas (estimativa): 303,444 | tamanho: 27.5 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_pontuacao` | `bigint` | sim | col 0 do arquivo \| Chave interna do registro |
| 2 | `id_empresa` | `bigint` | sim | col 1 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 3 | `id_item` | `bigint` | sim | col 2 do arquivo \| Item no catálogo global [FK -> dim_item.id_item] |
| 4 | `quantidade` | `bigint` | sim | col 3 do arquivo \| Quantidade |
| 5 | `pontuacao` | `numeric(20,8)` | sim | col 4 do arquivo \| Pontuação apurada |
| 6 | `tipo_ordem` | `text` | sim | col 5 do arquivo \| Tipo da ordem (OFE) |
| 7 | `pontos` | `bigint` | sim | col 6 do arquivo \| Pontos |
| 8 | `data_referencia` | `date` | sim | col 7 do arquivo \| Data de referência |
| 9 | `cod_faixa_pontuacao` | `text` | sim | col 8 do arquivo \| Faixa de pontuação (P70, P130...) |

### fat_previsao_financeira

> Previsões financeiras (orçamento) | origem: F_BI_F_PREVISAO_FINANCEIRA.TXT

`tipo: tabela | linhas (estimativa): 474 | tamanho: 144.0 KB`

**PK:** `id_previsao`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_previsao` | `bigint` | nao | col 0 do arquivo \| Chave interna da previsão |
| 2 | `data_previsao` | `date` | sim | col 1 do arquivo \| Data da previsão |
| 3 | `tipo_previsao` | `text` | sim | col 2 do arquivo \| Tipo (P = previsão) |
| 4 | `cod_periodicidade` | `bigint` | sim | col 3 do arquivo \| Código de periodicidade |
| 5 | `valor_realizado` | `numeric(20,8)` | sim | col 4 do arquivo \| Valor realizado |
| 6 | `data_inicio` | `date` | sim | col 5 do arquivo \| Data de início |
| 7 | `situacao` | `text` | sim | col 6 do arquivo \| A = ativa |
| 8 | `natureza` | `text` | sim | col 7 do arquivo \| F = fixa, V = variável |
| 9 | `id_cliente` | `bigint` | sim | col 8 do arquivo \| Cliente [FK -> dim_cliente.id_cliente] |
| 10 | `id_conta_financeira` | `bigint` | sim | col 9 do arquivo \| Conta financeira [FK -> dim_conta_financeira.id_conta_financeira] |
| 11 | `id_estabelecimento` | `bigint` | sim | col 10 do arquivo \| Estabelecimento [FK -> dim_estabelecimento.id_estabelecimento] |
| 12 | `id_fornecedor` | `bigint` | sim | col 11 do arquivo \| Fornecedor [FK -> dim_fornecedor.id_fornecedor] |
| 13 | `descricao_previsao` | `text` | sim | col 12 do arquivo \| Descrição da previsão |
| 14 | `id_empresa` | `bigint` | sim | col 13 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 15 | `dia_vencimento` | `bigint` | sim | col 14 do arquivo \| Dia de vencimento |
| 16 | `valor_previsto` | `numeric(20,8)` | sim | col 15 do arquivo \| Valor previsto |
| 17 | `flag_1` | `bigint` | sim | col 16 do arquivo \| Indicador auxiliar |

### fat_previsao_financeira_parcela

> Parcelas das previsões financeiras | origem: F_BI_F_SEQUENCIA_PREVISAO_FINANCEIRA.TXT

`tipo: tabela | linhas (estimativa): 2,973 | tamanho: 400.0 KB`

**PK:** `id_previsao_parcela`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_previsao_parcela` | `bigint` | nao | col 0 do arquivo \| Chave interna da parcela |
| 2 | `num_parcela` | `bigint` | sim | col 1 do arquivo \| Número da parcela |
| 3 | `valor_parcela` | `numeric(20,8)` | sim | col 2 do arquivo \| Valor da parcela |
| 4 | `data_vencimento` | `date` | sim | col 3 do arquivo \| Data de vencimento |
| 5 | `descricao` | `text` | sim | col 4 do arquivo \| Descrição |
| 6 | `id_previsao` | `bigint` | sim | col 5 do arquivo \| Previsão financeira [FK -> fat_previsao_financeira.id_previsao] |

### fat_saldo_conta_corrente

> Saldos de abertura de conta corrente | origem: F_BI_F_TSLD_IMP_CCR.TXT

`tipo: tabela | linhas (estimativa): 5 | tamanho: 16.0 KB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_saldo` | `bigint` | sim | col 0 do arquivo \| Chave interna |
| 2 | `data_saldo` | `date` | sim | col 1 do arquivo \| Data do saldo |
| 3 | `valor_saldo` | `numeric(20,8)` | sim | col 2 do arquivo \| Valor do saldo |
| 4 | `id_empresa` | `bigint` | sim | col 3 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 5 | `id_portador` | `bigint` | sim | col 4 do arquivo \| Portador [FK -> dim_portador.id_portador] |
| 6 | `natureza` | `text` | sim | col 5 do arquivo \| D = débito, C = crédito |

### fat_saldo_contabil

> Saldos contábeis por conta e período | origem: F_BI_F_TSLD_CTA_CTAB_BALANCETE.TXT

`tipo: tabela | linhas (estimativa): 2,881,786 | tamanho: 297.1 MB`

**PK:** `id_saldo_contabil`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | 🔑`id_saldo_contabil` | `bigint` | nao | col 0 do arquivo \| Chave interna do saldo |
| 2 | `data_saldo` | `date` | sim | col 1 do arquivo \| Data de referência do saldo |
| 3 | `valor_debito` | `numeric(20,8)` | sim | col 2 do arquivo \| Total de débitos no período |
| 4 | `valor_credito` | `numeric(20,8)` | sim | col 3 do arquivo \| Total de créditos no período |
| 5 | `id_conta` | `bigint` | sim | col 4 do arquivo \| Conta contábil [FK -> dim_conta_contabil.id_conta] |
| 6 | `id_empresa` | `bigint` | sim | col 5 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 7 | `saldo_anterior` | `numeric(20,8)` | sim | col 6 do arquivo \| Saldo anterior |
| 8 | `saldo_atual` | `numeric(20,8)` | sim | col 7 do arquivo \| Saldo atual |
| 9 | `id_centro_custo_empresa` | `bigint` | sim | col 8 do arquivo \| Centro de custo [FK -> dim_centro_custo_empresa.id_centro_custo_empresa] |

### fat_titulo_pagar

> Títulos a pagar | origem: F_BI_F_TTIT_CP.TXT

`tipo: tabela | linhas (estimativa): 809,946 | tamanho: 124.5 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_titulo_pagar` | `bigint` | sim | col 0 do arquivo \| Chave interna do título |
| 2 | `num_documento` | `bigint` | sim | col 1 do arquivo \| Número do documento |
| 3 | `num_parcela` | `bigint` | sim | col 2 do arquivo \| Parcela |
| 4 | `data_emissao` | `date` | sim | col 3 do arquivo \| Data de emissão |
| 5 | `data_vencimento` | `date` | sim | col 4 do arquivo \| Data de vencimento |
| 6 | `data_pagamento_prevista` | `date` | sim | col 5 do arquivo \| Data prevista de pagamento |
| 7 | `valor_titulo` | `numeric(20,8)` | sim | col 6 do arquivo \| Valor original |
| 8 | `valor_saldo` | `numeric(20,8)` | sim | col 7 do arquivo \| Saldo em aberto |
| 9 | `valor_juros` | `numeric(20,8)` | sim | col 8 do arquivo \| Juros |
| 10 | `valor_desconto` | `numeric(20,8)` | sim | col 9 do arquivo \| Desconto |
| 11 | `valor_multa` | `numeric(20,8)` | sim | col 10 do arquivo \| Multa |
| 12 | `id_empresa` | `bigint` | sim | col 11 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 13 | `id_nota_entrada` | `bigint` | sim | col 12 do arquivo \| Nota fiscal de entrada de origem [FK -> fat_nota_entrada.id_nota_entrada] |
| 14 | `id_fornecedor` | `bigint` | sim | col 13 do arquivo \| Fornecedor [FK -> dim_fornecedor.id_fornecedor] |
| 15 | `id_tipo_documento` | `bigint` | sim | col 14 do arquivo \| Tipo de documento [FK -> dim_tipo_documento.id_tipo_documento] |
| 16 | `id_tipo_lancamento_cp` | `bigint` | sim | col 15 do arquivo \| Tipo de lançamento [FK -> dim_tipo_lancamento_cp.id_tipo_lancamento_cp] |
| 17 | `id_conta_financeira` | `bigint` | sim | col 16 do arquivo \| Conta financeira [FK -> dim_conta_financeira.id_conta_financeira] |
| 18 | `id_referencia` | `bigint` | sim | col 17 do arquivo \| Referência interna |
| 19 | `id_centro_custo_empresa` | `bigint` | sim | col 18 do arquivo \| Centro de custo [FK -> dim_centro_custo_empresa.id_centro_custo_empresa] |
| 20 | `valor_auxiliar` | `numeric(20,8)` | sim | col 19 do arquivo \| Valor auxiliar |

### fat_titulo_receber

> Títulos a receber | origem: F_BI_F_TTIT_CR.TXT

`tipo: tabela | linhas (estimativa): 1,183,662 | tamanho: 144.6 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_titulo_receber` | `bigint` | sim | col 0 do arquivo \| Chave interna do título |
| 2 | `id_nota_saida` | `bigint` | sim | col 1 do arquivo \| Nota fiscal de saída de origem [FK -> fat_nota_saida.id_nota_saida] |
| 3 | `num_documento` | `bigint` | sim | col 2 do arquivo \| Número do documento |
| 4 | `num_parcela` | `text` | sim | col 3 do arquivo \| Parcela |
| 5 | `data_emissao` | `date` | sim | col 4 do arquivo \| Data de emissão |
| 6 | `data_vencimento` | `date` | sim | col 5 do arquivo \| Data de vencimento |
| 7 | `data_movimento` | `date` | sim | col 6 do arquivo \| Data do movimento/baixa |
| 8 | `valor_titulo` | `numeric(20,8)` | sim | col 7 do arquivo \| Valor original do título |
| 9 | `valor_saldo` | `numeric(20,8)` | sim | col 8 do arquivo \| Saldo em aberto |
| 10 | `valor_juros` | `numeric(20,8)` | sim | col 9 do arquivo \| Juros |
| 11 | `valor_desconto` | `numeric(20,8)` | sim | col 10 do arquivo \| Desconto |
| 12 | `valor_multa` | `numeric(20,8)` | sim | col 11 do arquivo \| Multa |
| 13 | `id_tipo_lancamento_cr` | `bigint` | sim | col 12 do arquivo \| Tipo de lançamento [FK -> dim_tipo_lancamento_cr.id_tipo_lancamento_cr] |
| 14 | `valor_recebido` | `numeric(20,8)` | sim | col 13 do arquivo \| Valor recebido |
| 15 | `id_portador` | `bigint` | sim | col 14 do arquivo \| Portador [FK -> dim_portador.id_portador] |
| 16 | `cod_sequencia` | `bigint` | sim | col 15 do arquivo \| Sequência do movimento |

### fat_titulo_receber_detalhe

> Títulos a receber — visão detalhada com cliente e representante | origem: F_BI_F_TTIT_CR_.TXT

`tipo: tabela | linhas (estimativa): 504,771 | tamanho: 77.6 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_titulo_receber` | `bigint` | sim | col 0 do arquivo \| Chave interna do título |
| 2 | `num_documento` | `bigint` | sim | col 1 do arquivo \| Número do documento |
| 3 | `num_parcela` | `text` | sim | col 2 do arquivo \| Parcela |
| 4 | `data_emissao` | `date` | sim | col 3 do arquivo \| Data de emissão |
| 5 | `data_vencimento` | `date` | sim | col 4 do arquivo \| Data de vencimento |
| 6 | `data_prevista_recebimento` | `date` | sim | col 5 do arquivo \| Data prevista de recebimento |
| 7 | `valor_titulo` | `numeric(20,8)` | sim | col 6 do arquivo \| Valor original |
| 8 | `valor_saldo` | `numeric(20,8)` | sim | col 7 do arquivo \| Saldo em aberto |
| 9 | `valor_juros` | `numeric(20,8)` | sim | col 8 do arquivo \| Juros |
| 10 | `valor_desconto` | `numeric(20,8)` | sim | col 9 do arquivo \| Desconto |
| 11 | `valor_multa` | `numeric(20,8)` | sim | col 10 do arquivo \| Multa |
| 12 | `valor_auxiliar` | `numeric(20,8)` | sim | col 11 do arquivo \| Valor auxiliar |
| 13 | `id_empresa` | `bigint` | sim | col 12 do arquivo \| Empresa [FK -> dim_empresa.id_empresa] |
| 14 | `id_referencia` | `bigint` | sim | col 13 do arquivo \| Referência interna |
| 15 | `id_estabelecimento` | `bigint` | sim | col 14 do arquivo \| Estabelecimento de cobrança [FK -> dim_estabelecimento.id_estabelecimento] |
| 16 | `id_cliente` | `bigint` | sim | col 15 do arquivo \| Cliente [FK -> dim_cliente.id_cliente] |
| 17 | `cod_referencia` | `bigint` | sim | col 16 do arquivo \| Referência interna |
| 18 | `id_representante` | `bigint` | sim | col 17 do arquivo \| Representante [FK -> dim_representante.id_representante] |
| 19 | `valor_liquido` | `numeric(20,8)` | sim | col 18 do arquivo \| Valor líquido |
| 20 | `percentual_comissao` | `numeric(20,8)` | sim | col 19 do arquivo \| Percentual de comissão |
| 21 | `id_tipo_lancamento_cr` | `bigint` | sim | col 20 do arquivo \| Tipo de lançamento [FK -> dim_tipo_lancamento_cr.id_tipo_lancamento_cr] |

## Pontes

### ponte_assistencia_centro_custo

> Rateio de assistência por centro de custo | origem: F_BI_F_TSOLLOS_CC_ITASS.TXT

`tipo: tabela | linhas (estimativa): 8,592 | tamanho: 488.0 KB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_registro` | `bigint` | sim | col 0 do arquivo \| Chave interna |
| 2 | `id_solicitacao` | `bigint` | sim | col 1 do arquivo \| Solicitação de assistência |
| 3 | `id_centro_custo` | `bigint` | sim | col 2 do arquivo \| Centro de custo [FK -> dim_centro_custo.id_centro_custo] |

### ponte_nota_item_pedido_item

> Ponte item da NF de saída x item do pedido | origem: F_BI_F_NOTAITEM_PEDIDOITEM.TXT

`tipo: tabela | linhas (estimativa): 652,017 | tamanho: 37.3 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_pedido_item` | `bigint` | sim | col 0 do arquivo \| Item do pedido [FK -> fat_pedido_item.id_pedido_item] |
| 2 | `id_nota_saida_item` | `bigint` | sim | col 1 do arquivo \| Item da NF de saída [FK -> fat_nota_saida_item.id_nota_saida_item] |
| 3 | `cod_referencia` | `bigint` | sim | col 2 do arquivo \| Referência interna |
| 4 | `data_vinculo` | `date` | sim | col 3 do arquivo \| Data do vínculo/faturamento |

### ponte_nota_saida_item_servico

> Ponte item da NF de saída x serviço da LC 116 | origem: F_BI_F_NOTA_SAIDA_IT_SERVICOS_LEI.TXT

`tipo: tabela | linhas (estimativa): 40,206 | tamanho: 1.7 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_nota_saida_item` | `bigint` | sim | col 0 do arquivo \| Item da NF de saída |
| 2 | `id_servico` | `bigint` | sim | col 1 do arquivo \| Serviço da LC 116 [FK -> dim_servico_lei.id_servico] |

### ponte_pedido_configuracao_ordem

> Ponte entre pedido, configuração do produto e ordem de fabricação | origem: F_BI_D_ITENS_PDV.TXT

`tipo: tabela | linhas (estimativa): 1,024,551 | tamanho: 51.5 MB`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_pedido` | `bigint` | sim | col 0 do arquivo \| Pedido de venda [FK -> fat_pedido.id_pedido] |
| 2 | `id_configuracao` | `bigint` | sim | col 1 do arquivo \| Configuração do produto |
| 3 | `id_ordem_fabricacao` | `bigint` | sim | col 2 do arquivo \| Ordem de fabricação [FK -> fat_ordem_fabricacao.id_ordem_fabricacao] |

## Views

### vw_assistencia

> Chamados de assistencia com item, motivo apurado e responsavel

`tipo: view`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_chamado` | `bigint` | sim |  |
| 2 | `num_chamado` | `bigint` | sim |  |
| 3 | `data_abertura` | `date` | sim |  |
| 4 | `situacao_chamado` | `text` | sim |  |
| 5 | `empresa` | `text` | sim |  |
| 6 | `estabelecimento` | `text` | sim |  |
| 7 | `nome_cidade` | `text` | sim |  |
| 8 | `uf` | `text` | sim |  |
| 9 | `descricao_tipo_chamado` | `text` | sim |  |
| 10 | `descricao_motivo_chamado` | `text` | sim |  |
| 11 | `id_assistencia_item` | `bigint` | sim |  |
| 12 | `cod_item` | `bigint` | sim |  |
| 13 | `descricao_item` | `text` | sim |  |
| 14 | `responsavel_apurado` | `text` | sim |  |
| 15 | `motivo_apurado` | `text` | sim |  |
| 16 | `quantidade` | `numeric(20,8)` | sim |  |
| 17 | `valor_item` | `numeric(20,8)` | sim |  |
| 18 | `data_ocorrencia` | `date` | sim |  |

### vw_compras

> Uma linha por item de pedido de compra, com fornecedor, item e comprador

`tipo: view`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_pedido_compra` | `bigint` | sim |  |
| 2 | `id_pedido_compra_item` | `bigint` | sim |  |
| 3 | `num_pedido_compra` | `bigint` | sim |  |
| 4 | `data_emissao` | `date` | sim |  |
| 5 | `situacao` | `text` | sim |  |
| 6 | `empresa` | `text` | sim |  |
| 7 | `id_fornecedor` | `bigint` | sim |  |
| 8 | `fornecedor` | `text` | sim |  |
| 9 | `cod_item` | `bigint` | sim |  |
| 10 | `descricao_item` | `text` | sim |  |
| 11 | `sigla_unidade` | `text` | sim |  |
| 12 | `comprador` | `text` | sim |  |
| 13 | `quantidade` | `numeric(20,8)` | sim |  |
| 14 | `quantidade_recebida` | `numeric(20,8)` | sim |  |
| 15 | `quantidade_saldo` | `numeric(20,8)` | sim |  |
| 16 | `valor_unitario` | `numeric(20,8)` | sim |  |
| 17 | `valor_total` | `numeric(20,8)` | sim |  |
| 18 | `data_entrega_prevista` | `date` | sim |  |

### vw_contas_pagar

> Titulos a pagar com fornecedor, centro de custo e conta financeira

`tipo: view`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_titulo_pagar` | `bigint` | sim |  |
| 2 | `num_documento` | `bigint` | sim |  |
| 3 | `num_parcela` | `bigint` | sim |  |
| 4 | `data_emissao` | `date` | sim |  |
| 5 | `data_vencimento` | `date` | sim |  |
| 6 | `empresa` | `text` | sim |  |
| 7 | `id_fornecedor` | `bigint` | sim |  |
| 8 | `fornecedor` | `text` | sim |  |
| 9 | `descricao_centro_custo` | `text` | sim |  |
| 10 | `descricao_conta_financeira` | `text` | sim |  |
| 11 | `descricao_documento` | `text` | sim |  |
| 12 | `tipo_lancamento` | `text` | sim |  |
| 13 | `valor_titulo` | `numeric(20,8)` | sim |  |
| 14 | `valor_saldo` | `numeric(20,8)` | sim |  |
| 15 | `valor_juros` | `numeric(20,8)` | sim |  |
| 16 | `valor_desconto` | `numeric(20,8)` | sim |  |
| 17 | `dias_atraso` | `integer` | sim |  |

### vw_contas_receber

> Titulos a receber com cliente, representante e dias de atraso calculados

`tipo: view`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_titulo_receber` | `bigint` | sim |  |
| 2 | `num_documento` | `bigint` | sim |  |
| 3 | `num_parcela` | `text` | sim |  |
| 4 | `data_emissao` | `date` | sim |  |
| 5 | `data_vencimento` | `date` | sim |  |
| 6 | `data_prevista_recebimento` | `date` | sim |  |
| 7 | `empresa` | `text` | sim |  |
| 8 | `id_cliente` | `bigint` | sim |  |
| 9 | `nome_cliente` | `text` | sim |  |
| 10 | `canal_venda` | `text` | sim |  |
| 11 | `nome_representante` | `text` | sim |  |
| 12 | `tipo_lancamento` | `text` | sim |  |
| 13 | `valor_titulo` | `numeric(20,8)` | sim |  |
| 14 | `valor_saldo` | `numeric(20,8)` | sim |  |
| 15 | `valor_juros` | `numeric(20,8)` | sim |  |
| 16 | `valor_desconto` | `numeric(20,8)` | sim |  |
| 17 | `valor_liquido` | `numeric(20,8)` | sim |  |
| 18 | `dias_atraso` | `integer` | sim |  |

### vw_estoque_movimentos

> Movimentos de estoque valorizados por item e centro de custo

`tipo: view`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `data_movimento` | `date` | sim |  |
| 2 | `tipo_movimento` | `text` | sim |  |
| 3 | `cod_deposito` | `bigint` | sim |  |
| 4 | `cod_classificacao` | `text` | sim |  |
| 5 | `id_item` | `bigint` | sim |  |
| 6 | `cod_item` | `bigint` | sim |  |
| 7 | `descricao_item` | `text` | sim |  |
| 8 | `descricao_centro_custo` | `text` | sim |  |
| 9 | `quantidade` | `numeric(20,8)` | sim |  |
| 10 | `custo_unitario` | `numeric(20,8)` | sim |  |
| 11 | `valor_movimento_calculado` | `numeric` | sim |  |

### vw_faturamento

> Uma linha por item de nota fiscal de saida, com cliente, item, representante e empresa

`tipo: view`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_nota_saida` | `bigint` | sim |  |
| 2 | `id_nota_saida_item` | `bigint` | sim |  |
| 3 | `num_nota` | `bigint` | sim |  |
| 4 | `data_emissao` | `date` | sim |  |
| 5 | `data_saida` | `date` | sim |  |
| 6 | `situacao_nota` | `text` | sim |  |
| 7 | `id_empresa` | `bigint` | sim |  |
| 8 | `empresa` | `text` | sim |  |
| 9 | `id_cliente` | `bigint` | sim |  |
| 10 | `nome_cliente` | `text` | sim |  |
| 11 | `canal_venda` | `text` | sim |  |
| 12 | `tipo_cliente` | `text` | sim |  |
| 13 | `id_estabelecimento` | `bigint` | sim |  |
| 14 | `nome_cidade` | `text` | sim |  |
| 15 | `uf` | `text` | sim |  |
| 16 | `pais` | `text` | sim |  |
| 17 | `id_representante` | `bigint` | sim |  |
| 18 | `nome_representante` | `text` | sim |  |
| 19 | `id_item` | `bigint` | sim |  |
| 20 | `cod_item` | `bigint` | sim |  |
| 21 | `descricao_item` | `text` | sim |  |
| 22 | `descricao_tipo_nf` | `text` | sim |  |
| 23 | `num_item` | `bigint` | sim |  |
| 24 | `quantidade` | `numeric(20,8)` | sim |  |
| 25 | `valor_bruto` | `numeric(20,8)` | sim |  |
| 26 | `valor_ipi` | `numeric(20,8)` | sim |  |
| 27 | `valor_icms` | `numeric(20,8)` | sim |  |
| 28 | `valor_desconto` | `numeric(20,8)` | sim |  |
| 29 | `valor_liquido` | `numeric(20,8)` | sim |  |

### vw_pedidos

> Uma linha por item de pedido de venda, com cliente, item e configuracao do produto

`tipo: view`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_pedido` | `bigint` | sim |  |
| 2 | `id_pedido_item` | `bigint` | sim |  |
| 3 | `num_pedido` | `bigint` | sim |  |
| 4 | `data_emissao` | `date` | sim |  |
| 5 | `data_entrega_prevista` | `date` | sim |  |
| 6 | `situacao_pedido` | `text` | sim |  |
| 7 | `origem_pedido` | `text` | sim |  |
| 8 | `status_liberacao` | `text` | sim |  |
| 9 | `id_empresa` | `bigint` | sim |  |
| 10 | `empresa` | `text` | sim |  |
| 11 | `id_estabelecimento` | `bigint` | sim |  |
| 12 | `id_cliente` | `bigint` | sim |  |
| 13 | `nome_cliente` | `text` | sim |  |
| 14 | `canal_venda` | `text` | sim |  |
| 15 | `nome_cidade` | `text` | sim |  |
| 16 | `uf` | `text` | sim |  |
| 17 | `id_representante` | `bigint` | sim |  |
| 18 | `nome_representante` | `text` | sim |  |
| 19 | `descricao_condicao` | `text` | sim |  |
| 20 | `id_item_empresa` | `bigint` | sim |  |
| 21 | `cod_item` | `bigint` | sim |  |
| 22 | `descricao_item` | `text` | sim |  |
| 23 | `configuracao_produto` | `text` | sim |  |
| 24 | `num_item` | `bigint` | sim |  |
| 25 | `quantidade` | `numeric(20,8)` | sim |  |
| 26 | `quantidade_saldo` | `numeric(20,8)` | sim |  |
| 27 | `quantidade_cancelada` | `numeric(20,8)` | sim |  |
| 28 | `valor_unitario` | `numeric(20,8)` | sim |  |
| 29 | `valor_item` | `numeric` | sim |  |
| 30 | `valor_bruto_pedido` | `numeric(20,8)` | sim |  |
| 31 | `valor_liquido_pedido` | `numeric(20,8)` | sim |  |

### vw_producao_operacoes

> Uma linha por operacao de roteiro, com a ordem de fabricacao e o item

`tipo: view`

| # | coluna | tipo | nulo | descricao |
|---|--------|------|------|-----------|
| 1 | `id_ordem_fabricacao` | `bigint` | sim |  |
| 2 | `num_ordem` | `bigint` | sim |  |
| 3 | `data_abertura` | `date` | sim |  |
| 4 | `data_prevista_fim` | `date` | sim |  |
| 5 | `data_fim` | `date` | sim |  |
| 6 | `quantidade_prevista` | `numeric(20,8)` | sim |  |
| 7 | `quantidade_produzida` | `numeric(20,8)` | sim |  |
| 8 | `quantidade_refugada` | `numeric(20,8)` | sim |  |
| 9 | `empresa` | `text` | sim |  |
| 10 | `cod_item` | `bigint` | sim |  |
| 11 | `descricao_item` | `text` | sim |  |
| 12 | `configuracao_produto` | `text` | sim |  |
| 13 | `id_ordem_roteiro` | `bigint` | sim |  |
| 14 | `num_operacao` | `bigint` | sim |  |
| 15 | `descricao_operacao` | `text` | sim |  |
| 16 | `tipo_operacao` | `text` | sim |  |
| 17 | `descricao_centro_trabalho` | `text` | sim |  |
| 18 | `tempo_previsto` | `numeric(20,8)` | sim |  |
| 19 | `tempo_realizado` | `numeric(20,8)` | sim |  |
| 20 | `tempo_setup` | `numeric(20,8)` | sim |  |
| 21 | `data_inclusao_operacao` | `date` | sim |  |
