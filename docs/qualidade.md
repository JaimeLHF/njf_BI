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

