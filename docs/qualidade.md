# Qualidade dos dados — vendas e producao

Gerado por `scripts/06_qualidade.py` em 2026-08-28 sobre o schema `raw` do `dados.duckdb`. Nenhuma linha de dado aparece aqui: so contagens.

## 1. Nulos em campos criticos

| tabela | coluna | linhas | nulos | % |
|--------|--------|-------:|------:|--:|
| `fat_pedido` | `data_entrega_prevista` | 202,918 | 4,066 | 2.0% |
| `fat_pedido` | `id_representante` | 202,918 | 4,044 | 2.0% |
| `fat_nota_saida` | `data_saida` | 132,407 | 33 | 0.0% |
| `fat_nota_saida` | `id_representante` | 132,407 | 329 | 0.2% |
| `fat_ordem_fabricacao` | `data_fim` | 618,358 | 6 | 0.0% |
| `fat_ordem_fabricacao` | `data_entrega` | 618,358 | 55,453 | 9.0% |
| `fat_pontuacao_producao` | `data_referencia` | 303,444 | 13,518 | 4.5% |

## 2. Orfaos de chave estrangeira

| de | coluna | para | total | orfaos | % |
|----|--------|------|------:|-------:|--:|
| `ponte_nota_saida_item_servico` | `id_nota_saida_item` | `fat_nota_saida_item` | 40,206 | 8,850 | 22.012% |
| `dim_centro_trabalho` | `id_centro_custo` | `dim_centro_custo` | 137 | 88 | 64.234% |

## 3. Datas incoerentes

| tabela | problema | linhas | % da tabela |
|--------|----------|-------:|------------:|
| `fat_ordem_fabricacao` | inicio antes da abertura | 247,718 | 40.06% |
| `fat_ordem_fabricacao` | entrega antes do fim de producao | 445 | 0.07% |
| `fat_pedido` | entrega prevista antes da emissao | 1 | 0.00% |
| `fat_pedido` | emissao antes da inclusao | 30,429 | 15.00% |
| `fat_ordem_fabricacao` | abertura no futuro | 7,504 | 1.21% |

**Faixa observada das datas principais**

| tabela | coluna | min | max | fora de 1990–2035 |
|--------|--------|-----|-----|------------------:|
| `fat_pedido` | `data_emissao` | 2020-01-05 | 2026-08-21 | 0 |
| `fat_nota_saida` | `data_emissao` | 2021-01-04 | 2026-08-21 | 0 |
| `fat_ordem_fabricacao` | `data_abertura` | 2020-01-30 | 2027-11-30 | 0 |
| `fat_ordem_fabricacao` | `data_prevista_fim` | 2020-08-19 | 2027-11-30 | 0 |
| `fat_ordem_movimento` | `data_apontamento` | 2021-01-04 | 2026-08-22 | 0 |

## 4. Duplicatas de chave

| tabela | chave | linhas | chaves distintas | duplicadas |
|--------|-------|-------:|-----------------:|-----------:|
| `fat_pedido` | `id_pedido` | 202,918 | 202,918 | 0 |
| `fat_pedido_item` | `id_pedido_item` | 379,754 | 379,754 | 0 |
| `fat_nota_saida` | `id_nota_saida` | 132,407 | 132,407 | 0 |
| `fat_nota_saida_item` | `id_nota_saida_item` | 254,031 | 254,031 | 0 |
| `fat_ordem_fabricacao` | `id_ordem_fabricacao` | 618,358 | 618,358 | 0 |
| `fat_ordem_fabricacao` | `num_ordem, id_empresa` | 618,358 | 618,358 | 0 |
| `fat_ordem_roteiro` | `id_ordem_roteiro` | 3,695,097 | 3,695,097 | 0 |
| `fat_ordem_roteiro` | `id_ordem_fabricacao, num_operacao` | 3,695,097 | 3,695,097 | 0 |
| `fat_ordem_movimento` | `id_ordem_movimento` | 3,425,536 | 3,425,536 | 0 |
| `fat_nota_saida_item_pontuacao` | `id_nota_saida_item, id_ordem_fabricacao` ⚠ | 1,116,354 | 148,745 | 967,609 |
| `ponte_pedido_configuracao_ordem` | `id_pedido, id_configuracao, id_ordem_fabricacao` ⚠ | 1,024,551 | 341,517 | 683,034 |
| `ponte_nota_item_pedido_item` | `id_pedido_item, id_nota_saida_item` ⚠ | 652,017 | 213,914 | 438,103 |
| `fat_pontuacao_producao` | `id_pontuacao` ⚠ | 303,444 | 40,423 | 263,021 |
| `fat_contrato_loja` | `id_contrato` ⚠ | 31,875 | 10,625 | 21,250 |
| `dim_item_empresa` | `cod_item, id_empresa` | 174,442 | 174,442 | 0 |
| `dim_cliente` | `cod_cliente` | 7,156 | 7,156 | 0 |

## 5. Valores negativos

Nenhum valor negativo nas colunas de quantidade, valor e tempo.

## 6. Duplicacao de carga (linha inteira repetida)

| tabela | linhas | linhas distintas | fator | tem PK? |
|--------|-------:|-----------------:|------:|---------|
| `fat_contrato_loja` | 31,875 | 10,625 | **3.00x** | **nao** |
| `fat_contrato_loja_parcela` | 107,970 | 35,990 | **3.00x** | **nao** |
| `fat_nota_saida_item_pedido` | 562,914 | 187,615 | **3.00x** | **nao** |
| `fat_nota_saida_item_pontuacao` | 1,116,354 | 372,118 | **3.00x** | **nao** |
| `fat_pedido_representante_secundario` | 2,880 | 960 | **3.00x** | **nao** |
| `fat_pontuacao_producao` | 303,444 | 101,146 | **3.00x** | **nao** |
| `ponte_nota_item_pedido_item` | 652,017 | 215,658 | **3.02x** | **nao** |
| `ponte_nota_saida_item_servico` | 40,206 | 10,534 | **3.82x** | **nao** |
| `ponte_pedido_configuracao_ordem` | 1,024,551 | 341,517 | **3.00x** | **nao** |

## 7. Colunas que nao significam o que o nome sugere

### `fat_ordem_fabricacao.data_fim` nao e a data real de termino

Em 296,983 ordens encerradas com apontamento, **293,261 (98.7%)** tem `data_fim` ANTERIOR ao ultimo apontamento de producao. Mediana: -43 dias.

A data real de conclusao e `max(fat_ordem_movimento.data_apontamento)` por ordem, via `fat_ordem_roteiro`. Aderencia a prazo calculada com `data_fim` mede o plano contra o plano, nao o realizado.

### `flag_encerrada = 0` nao significa "ordem em aberto"

273,960 ordens tem `flag_encerrada = 0`, mas **263,676 (96.2%)** ja produziram quantidade e **270,881 (98.9%)** tem previsao de fim no passado. A flag parece marcar encerramento administrativo, nao status de producao. Use `cod_situacao` + apontamento para status real.

### `fat_pedido_item.quantidade_saldo` nao e saldo em aberto

De 175,056 itens com `quantidade_saldo > 0`, **169,190 (96.6%) ja foram faturados** (tem vinculo em `ponte_nota_item_pedido_item`). A coluna guarda a quantidade original do pedido e nao e baixada no faturamento. Carteira em aberto = quantidade do item menos o faturado pela ponte **deduplicada**.

### `fat_ordem_fabricacao.cod_situacao`

| cod_situacao | ordens | com producao | leitura |
|---|-------:|-------------:|---------|
| 1 | 563,819 | 561,569 | ativa |
| 0 | 54,539 | 132 | cancelada/nao executada (praticamente nenhuma produziu) |


## 8. Impacto em relatorios existentes e a correcao no dbt

> **Isto afeta relatorios que a empresa ja tenha em producao.** Qualquer consulta que leia essas 9 tabelas direto da origem — Power BI, Excel, extracao propria — esta contando cada linha tres vezes. Nao e um problema desta migracao: a duplicacao vem do Postgres, e a migracao e single-pass. Numeros ja publicados a partir dessas tabelas precisam ser reconferidos.

O que infla, na pratica:

- vinculo pedido ↔ NF (`ponte_nota_item_pedido_item`, `fat_nota_saida_item_pedido`) — conversao de pedido em faturamento e tempo entre venda e faturamento
- vinculo pedido ↔ ordem (`ponte_pedido_configuracao_ordem`) — qualquer visao que compare vendido com produzido
- pontuacao de producao (`fat_pontuacao_producao`, `fat_nota_saida_item_pontuacao`) — produtividade da fabrica
- rateio de comissao (`fat_pedido_representante_secundario`)
- contratos de loja (`fat_contrato_loja`, `fat_contrato_loja_parcela`)
- servicos da LC 116 (`ponte_nota_saida_item_servico`) — base de ISS

A correcao esta na camada `staging` do dbt (`models/staging/`), com dedup explicita por chave natural. O `raw` fica intacto de proposito: o defeito da origem precisa continuar visivel e versionado.

**Efeito medido da correcao**

| tabela | raw | staging | removidas | fator |
|--------|----:|--------:|----------:|------:|
| `fat_contrato_loja` | 31,875 | 10,625 | 21,250 | 3.000x |
| `fat_contrato_loja_parcela` | 107,970 | 35,990 | 71,980 | 3.000x |
| `fat_nota_saida_item_pedido` | 562,914 | 187,615 | 375,299 | 3.000x |
| `fat_nota_saida_item_pontuacao` | 1,116,354 | 372,118 | 744,236 | 3.000x |
| `fat_pedido_representante_secundario` | 2,880 | 960 | 1,920 | 3.000x |
| `fat_pontuacao_producao` | 303,444 | 101,146 | 202,298 | 3.000x |
| `ponte_nota_item_pedido_item` | 652,017 | 215,658 | 436,359 | 3.023x |
| `ponte_nota_saida_item_servico` | 40,206 | 10,452 | 29,754 | 3.847x |
| `ponte_pedido_configuracao_ordem` | 1,024,551 | 341,517 | 683,034 | 3.000x |


### Perguntas para a empresa

Nenhuma destas se responde com o dado que temos. Levar para a reuniao.

1. **Quais relatorios consomem essas 9 tabelas hoje?** Power BI, Excel, extracao propria — precisamos da lista para estimar o erro de cada numero ja publicado. Enquanto nao soubermos, todo indicador construido sobre elas esta sob suspeita de estar 3x inflado.

2. **Qual o grao real de `fat_pontuacao_producao`?** `id_pontuacao` nao identifica a linha: sao 40.423 valores para 101.146 linhas distintas, e um unico id cobre 880 itens e 678 datas. Ele e um numero de lote, de apuracao mensal, de documento? Sem isso a dedup fica travada em linha inteira e o indicador de produtividade nao tem grao definido.

3. **O que e `quantidade_refugada` quando e maior que a produzida?** Acontece em 54.439 das 54.494 ordens com valor preenchido. E refugo acumulado do roteiro inteiro, sucata em outra unidade de medida, ou outra grandeza? Enquanto nao souber, nao ha indicador de qualidade de producao.

4. **Qual a diferenca entre `flag_encerrada` e `cod_situacao` na ordem de fabricacao?** 96,2% das ordens com `flag_encerrada = 0` ja produziram quantidade e 98,9% tem previsao de fim no passado. A flag parece encerramento administrativo e `cod_situacao` o status real (1 = ativa, 0 = cancelada), mas isso e leitura nossa. Qual das duas define "ordem em aberto" para a fabrica?

5. **Por que 62 codigos de servico da LC 116 nao tem nenhuma nota vinculada?** Ver a secao 9. Se a base de ISS desses servicos e apurada em outro lugar, precisamos saber onde.

6. **Como a fabrica aponta producao?** A mediana do tempo entre o primeiro e o ultimo apontamento de uma ordem e zero dias: quase tudo cai no mesmo dia. Se o apontamento e feito em lote no fechamento, o tempo de ciclo nao esta no dado. E `data_abertura` vem depois do primeiro apontamento em 24,8% das ordens — o que ela marca de fato?


## 9. Vinculos fiscais de servico sem base

As 8,850 linhas do sentinela `id_nota_saida_item = 0` foram verificadas: **o servico esta preenchido em todas**. `id_servico` nulo: 0. Servico inexistente em `dim_servico_lei`: 0. Sao 82 servicos da LC 116 distintos, todos validos, apontando para um item de nota fiscal que nao existe.

A ponte tem so duas colunas e nao carrega valor, entao **nao ha receita de servico perdida em reais** — o valor mora em `fat_nota_saida_item.valor_liquido`, e sem item nao ha o que somar. O problema e de cobertura fiscal:

| | servicos LC 116 |
|---|---:|
| so aparecem no sentinela (nenhuma nota vinculada) | **62** |
| aparecem no sentinela e em notas reais | 20 |
| nunca aparecem no sentinela | 2 |
| **total na ponte** | **84** |

Em volume de vinculo o sentinela e pequeno: 82 pares distintos contra 10,452 uteis (0.8%). As 8,850 linhas sao esses 82 pares repetidos, nao 8,850 vinculos.

Em cobertura de catalogo o buraco e grande: **62 dos 84 codigos de servico (74%) nao tem uma unica nota atribuida**. Qualquer visao de ISS por tipo de servico vai mostrar esses codigos zerados, e nao da para saber pelo DW se e porque nao houve movimento ou porque o vinculo se perdeu na carga.

A base recuperavel sao os 10,452 itens de NF vinculados, R$ 59.45 milhoes de valor liquido.


## 10. Efeito da correcao de prazo nos marts

A ordem em que o prazo e medido muda o indicador em **41 pontos percentuais**. Sobre as ordens ativas (`cod_situacao = 1`):

| | com data_fim (ingenuo) | com o apontamento (real) |
|---|---:|---:|
| ordens no prazo | **73.7%** | **32.9%** |
| mediana do atraso | -13 dias (adiantado) | +11 dias |

Base: 563,819 ordens ativas, 550,985 com apontamento (97.7%). Lead time mediano da abertura a conclusao real: **19 dias**.

O numero ingenuo diz que tres em cada quatro ordens fecham no prazo, e com folga. O numero real diz que uma em cada tres fecha no prazo, com mediana de 11 dias de atraso. **Se algum indicador de produção hoje mostra algo perto de 74%, ele esta medindo o plano contra o plano.**

### `data_abertura` nao e o comeco do processo

Em 110,312 das 550,985 ordens com apontamento (**20.0%**) o `lead_time_dias` da negativo: a producao terminou antes da ordem ser aberta. Olhando o inicio em vez do fim, 136,849 ordens (**24.8%**) tem o primeiro apontamento anterior a abertura — e `data_inicio` ja era anterior a `data_abertura` em 41% das ordens (secao 3).

A leitura: **`data_abertura` e um registro administrativo posterior**, nao a criacao da ordem. Por isso o mart traz `lead_time_producao_dias` (do primeiro ao ultimo apontamento, nunca negativo) ao lado de `lead_time_dias`, mais a flag `apontamento_antes_da_abertura`.

Ressalva sobre o proprio `lead_time_producao_dias`: a mediana e 0 dias — a maior parte das ordens concentra todo o apontamento num unico dia. Ele mede a janela de apontamento, que pode nao ser o tempo real de fabricacao se a fabrica aponta em lote no fechamento. **Confirmar com a producao como e o habito de apontamento** antes de publicar tempo de ciclo.

### Ordens com abertura no futuro

7,476 ordens tem `data_abertura` entre hoje e o fim de 2026: isso e programacao normal, nao defeito. Ja as 28 ordens abertas em 2027 (com apenas 9 apontamentos) sao o que faz o recorte "carteira 2027" parecer existir. Trate 2027 como residual ate a empresa confirmar.

