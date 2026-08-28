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

5. **`origem_pedido = 'SIM'` e o canal de revenda pendente de liberacao?** Os pedidos `SIM` sao **90% MULTIMARCAS** e **nunca geram ordem de fabricacao** (0 para 116.429 pedidos, contra 341.410 ordens do `PDV`). Nossa leitura e que representam **intencao de compra do canal de revenda, pendente de liberacao** (credito, pedido minimo, colecao), enquanto FLAGSHIP e loja propria e libera direto — o que explica os 100% em `PE` + `BLQ`. Confirmam? E alguem acompanha esse volume como funil comercial?

   Correcao importante para a conversa: o numero certo do funil e **~R$ 138 milhoes anualizados em 2026, estavel**, nao os R$ 426 milhoes do agregado bruto. A diferenca sao 60 pedidos com valor irreal, que a secao 11 detalha.

6. **Existe processo de cancelamento de pedido nao atendido?** Sem ele, **~R$ 83 milhoes da carteira sao registros fantasma de 2021-2025** — pedidos com entrega prevista vencida ha mais de um ano, nunca faturados e nunca cancelados. Se nao ha rotina de baixa, a carteira precisa de um corte por idade para significar alguma coisa.

7. **Existe um agrupamento comercial acima de `cod_familia`?** Sao 2.584 familias, e as 20 maiores respondem por apenas 28% do faturamento — nao da para navegar numa reuniao nem resumir em top-N. `dim_item_classificacao` tem 6.5 mil valores por tipo, pior ainda. Existe linha, colecao ou grupo com algumas dezenas de valores?

8. **Como a fabrica aponta producao?** A mediana do tempo entre o primeiro e o ultimo apontamento de uma ordem e zero dias: quase tudo cai no mesmo dia. Se o apontamento e feito em lote no fechamento, o tempo de ciclo nao esta no dado. E `data_abertura` vem depois do primeiro apontamento em 24,8% das ordens — o que ela marca de fato?


## 9. Efeito da correcao de prazo nos marts

Duas coisas diferentes saem do apontamento, e elas **nao tem o mesmo grau de confianca**. A aderencia a prazo esta solida; o tempo de ciclo nao. Nao descartar as duas juntas.

### Aderencia a prazo — solida

Usa `data_prevista_fim` contra `data_conclusao_real`, que e o **ultimo** apontamento da ordem. O ultimo apontamento e conclusao real independente de como a fabrica aponta: mesmo que tudo seja lancado de uma vez no fechamento, a ordem nao esta concluida antes dele. O indicador vale.

| | com data_fim (ingenuo) | com o apontamento (real) |
|---|---:|---:|
| ordens no prazo | **73.7%** | **32.9%** |
| mediana do atraso | -13 dias (adiantado) | +11 dias |

Base: 563,819 ordens ativas (`cod_situacao = 1`), 550,985 com apontamento (97.7%).

A ordem em que o prazo e medido muda o indicador em **41 pontos percentuais**. O numero ingenuo diz que tres em cada quatro ordens fecham no prazo, e com folga. O real diz que uma em cada tres fecha no prazo, com mediana de 11 dias de atraso. **Se algum indicador de producao hoje mostra algo perto de 74%, ele esta medindo o plano contra o plano.**

### Lead time / tempo de ciclo — comprometido

Aqui sim ha problema, e ele **nao afeta a aderencia acima**.

O tempo do primeiro ao ultimo apontamento (`lead_time_producao_dias`) tem mediana de 0 dias: quase toda ordem concentra o apontamento num unico dia. Isso mede a janela de apontamento, nao o tempo de fabricacao. Se a fabrica aponta em lote no fechamento, o tempo de ciclo simplesmente nao esta no dado.

E o lead time contado da abertura (`lead_time_dias`) e negativo em 110,312 das 550,985 ordens com apontamento (**20.0%**): a producao terminou antes da ordem ser aberta. Em 136,849 ordens (**24.8%**) o primeiro apontamento vem antes da abertura, e `data_inicio` ja era anterior a `data_abertura` em 41% das ordens (secao 3). **`data_abertura` e um registro administrativo posterior**, nao a criacao da ordem.

Por isso o mart traz as duas medidas lado a lado, mais a flag `apontamento_antes_da_abertura`. **Nao publicar tempo de ciclo** ate a producao confirmar o habito de apontamento (pergunta 5 da secao 8).

### Ordens com abertura no futuro

7,476 ordens tem `data_abertura` entre hoje e o fim de 2026: isso e programacao normal, nao defeito. Ja as 28 ordens abertas em 2027 (com apenas 9 apontamentos) sao o que faz o recorte "carteira 2027" parecer existir. Trate 2027 como residual ate a empresa confirmar.


## 10. Carteira em aberto: o filtro que faltava

Tres coisas precisam estar certas para a carteira fechar. Duas ja estavam em `docs/qualidade.md`; a terceira so apareceu ao construir `fct_pedido`.

1. `quantidade_saldo` nao serve (secao 7) — a origem nao a baixa.
2. A ponte pedido ↔ NF esta triplicada (secao 6) — deduplicar antes.
3. **`origem_pedido` separa pedido de nao-pedido** — o achado novo.

### Conversao em nota fiscal por origem

| origem | conversao em NF | itens | valor do pedido | em aberto |
|---|---:|---:|---:|---:|
| `PDV` | **84.4%** | 202,298 | R$ 1499.1 mi | R$ 189.0 mi |
| `SIM` | **0.0%** | 176,559 | R$ 2596.4 mi | R$ 2596.4 mi |
| `EXP` | **0.0%** | 860 | R$ 1.9 mi | R$ 1.8 mi |
| `ORC` | **0.0%** | 37 | R$ 0.3 mi | R$ 0.2 mi |

**`SIM` nunca gerou uma nota fiscal.** Nao e baixa conversao: e zero, em cinco anos e 176 mil itens. A origem esta quase perfeitamente correlacionada com `situacao_pedido = 'PE'` (pendente) e `status_liberacao = 'BLQ'` (bloqueado). `EXP` e `ORC` idem, mas sao residuais.

### O tamanho do erro

| criterio | carteira |
|---|---:|
| pela `quantidade_saldo` da origem | R$ 1149.4 mi |
| sem separar origem | R$ 2787.1 mi |
| **so origens que faturam** | **R$ 189.0 mi** |

Sem o filtro de origem a carteira daria R$ 2787.1 milhoes — mais que o dobro de todo o faturamento de 2021 a 2026 somado. Com o filtro, R$ 189.0 milhoes, que se sustenta contra R$ 301 milhoes faturados em 2025.

### Carteira por ano de entrega prevista (so origens que faturam)

| ano | pedidos | em aberto |
|---|---:|---:|
| 2020 | 1 | R$ 0.0 mi |
| 2021 | 2,034 | R$ 10.9 mi |
| 2022 | 2,249 | R$ 16.2 mi |
| 2023 | 2,544 | R$ 17.9 mi |
| 2024 | 1,870 | R$ 13.8 mi |
| 2025 | 2,009 | R$ 24.3 mi |
| 2026 | 4,520 | R$ 101.3 mi |
| 2027 | 57 | R$ 4.6 mi |

### O que `SIM` e: tres testes feitos com o proprio dado

**1. `SIM` nunca virou compromisso produtivo.** Cruzando com `ponte_pedido_configuracao_ordem`: **0 ordens de fabricacao** para os 116.429 pedidos `SIM`, contra 341,410 ordens para os 86.296 pedidos `PDV`. Zero ordens, zero produzidas (0). A fabrica nunca produziu contra um pedido `SIM`. **Isso sustenta os R$ 189 milhoes**: se nao gerou ordem nem nota, nao e compromisso.

**2. Nao e espelho nem desdobramento.** Os clientes quase nao se sobrepoem no volume: 254 clientes aparecem nas duas origens, 4 so em `SIM` e 5,691 so em `PDV`. E `SIM` esta concentrado em **MULTIMARCAS** (128 clientes, 105.419 pedidos — 90% do total), enquanto `PDV` e dominado por FLAGSHIP. Buscando duplicata por estabelecimento + valor, so 9,022 de 37,048 combinacoes (24%) tem par em `PDV` — acima do acaso, mas longe de espelho sistematico. **Os R$ 2,6 bi nao sao duplicata de pedido existente.**

**3. `SIM` e um estado, nao uma origem.** Os 116.429 pedidos estao **100% em `situacao_pedido = 'PE'` e `status_liberacao = 'BLQ'`** — 0 excecoes. Nenhum foi liberado, nunca, em cinco anos. Ja `PDV` tem 75.996 pedidos atendidos e liberados. Mesmas empresas emitentes (1, 11, 21), mesmo perfil de produto configurado (88% dos itens com mascara em ambas). Nao e outro sistema: e o mesmo fluxo parado num estagio anterior.

**Leitura:** `SIM` e **intencao de compra do canal de revenda, pendente de liberacao** — 90% MULTIMARCAS, 100% bloqueado, nunca produzido. `PDV` e dominado por FLAGSHIP, loja propria, que libera direto. Por isso `SIM` fica fora da carteira.

**O volume nao esta crescendo.** O agregado bruto de 2026 (R$ 426.7 milhoes) engana: sao 60 pedidos com valor irreal (secao 11). Filtrando por `valor_pedido_plausivel`, a serie e plana:

| ano | pedidos | valor plausivel |
|---|---:|---:|
| 2021 | 39,599 | R$ 279.4 mi |
| 2022 | 16,506 | R$ 123.8 mi |
| 2023 | 15,994 | R$ 117.4 mi |
| 2024 | 16,536 | R$ 131.8 mi |
| 2025 | 16,936 | R$ 204.2 mi |
| 2026 | 9,582 | R$ 114.5 mi |

O numero de pedidos por ano esta estavel desde 2022 (16-17 mil) e 2026 projeta na mesma faixa. **Nao e funil em crescimento nem acumulo de registros: e um canal de tamanho constante que nunca foi medido.**

O grosso da carteira esta em **2026**. 2027 continua residual. E sobra um resto espalhado por 2021-2025: pedidos antigos que nunca foram faturados nem cancelados — provavelmente abandono, mas isso tambem e pergunta para a empresa.


## 11. Pedidos com valor irreal

Apareceu ao investigar por que o valor de `SIM` saltou em 2026. Nao era o canal: era um punhado de pedidos com quantidade impossivel.

### Quantidade redonda nao e o sinal

A primeira hipotese era que quantidades redondas (10.000, 40.000) marcassem registro de teste. **Elas aparecem nas duas origens**, mas significam coisas diferentes:

| quantidade | itens | em `SIM` | em `PDV` | valor |
|---:|---:|---:|---:|---:|
| 1,000 | 79 | 25 | 54 | R$ 72.46 mi |
| 5,000 | 19 | 0 | 19 | R$ 0.07 mi |
| 10,000 | 16 | 13 | 3 | R$ 531.24 mi |
| 20,000 | 4 | 3 | 1 | R$ 118.51 mi |
| 40,000 | 8 | 8 | 0 | R$ 513.86 mi |

5.000 unidades aparecem 19 vezes, todas em `PDV`, e somam R$ 0,07 milhao: e item barato comprado em volume, perfeitamente legitimo. Ja 40.000 unidades somam R$ 514 milhoes. **A redondeza nao distingue nada — o que distingue e a magnitude relativa ao proprio produto.** Por isso o mart nao usa lista de numeros redondos nem corte em reais.

### As duas assinaturas usadas

**1. `flag_quantidade_igual_valor_unitario`** — o mesmo numero digitado nos dois campos. Sozinha ela e ruidosa, e o piso de 100 unidades e o que a torna util:

| quantidade | itens | valor |
|---|---:|---:|
| menos de 10 | 617 | R$ 0.0 mi |
| 10 a 99 | 64 | R$ 0.04 mi |
| 100 ou mais | 7 | R$ 158.63 mi |

Comprar 1 unidade de um item de R$ 1,00 e trivialmente comum e nao e erro. Acima de 100 a coincidencia deixa de ser plausivel — e o maior pedido da base esta ai: quantidade 11.747, valor unitario R$ 11.747,00, total R$ 138 milhoes.

**2. `flag_quantidade_atipica`** — quantidade acima de **10x o p99 do proprio item**, com o mesmo piso de 100. O p99 cai para a familia e depois para o global quando o item nao tem 30 ocorrencias.

O detalhe que quase passou: **o percentil precisa ser calculado sobre base limpa** (`quantidade <= 500`, o p99,9 global). Na primeira versao a referencia se contaminava com o proprio defeito — um item com seis pedidos falsos de 40.000 unidades tinha p99 = 40.000 e passava ileso. Com a base limpa o p99 desse item cai para 7 e ele e marcado.

Sobre o N: 10 marca 150 itens, 20 marca 111 e 50 apenas 81, deixando passar erro evidente; 5 comeca a pegar produto de cauda curta.

### Resultado

| flag | itens |
|---|---:|
| `flag_quantidade_igual_valor_unitario` | 7 |
| `flag_quantidade_atipica` | 150 |
| **`valor_pedido_plausivel` = falso** | **155** |

155 itens em 379.754 (**0,04%**), R$ 1626.3 milhoes de valor irreal.

| origem | itens implausiveis | valor |
|---|---:|---:|
| `PDV` | 92 | R$ 1.0 mi |
| `SIM` | 63 | R$ 1625.3 mi |
| `EXP` | 0 | R$ 0.0 mi |
| `ORC` | 0 | R$ 0.0 mi |

**O erro existe nas duas origens.** `SIM` concentra o valor (63 itens, R$ 1.625 milhoes), mas `PDV` tem 92 itens marcados — mais casos, com valor pequeno. Isso o torna **achado proprio**, um problema de entrada de dados no pedido, e nao apenas mais um indicio de ambiente de simulacao.

### Impacto

**A carteira nao e afetada:** R$ 188.96 milhoes com os outliers, R$ 188.7 milhoes sem.

O que **e** afetado: qualquer media, ticket medio ou serie temporal de valor de pedido. Foi exatamente o que fez o funil de 2026 parecer tres vezes maior do que e.


## Apendice — sentinela da ponte de servicos

_Nota tecnica, nao e achado. Nao vai para a apresentacao._

O sentinela `id_nota_saida_item = 0` da ponte de servicos (8,850 linhas, 82 pares distintos) foi verificado: `id_servico` esta preenchido e valido em todas. A ponte nao carrega valor, entao nao ha receita em risco.

Os 62 codigos da LC 116 que so aparecem no sentinela **nao sao anomalia**: o catalogo fiscal vem pre-populado com a lista inteira da lei, e usar 22 de 84 codigos e o normal de uma industria. O sentinela apenas carrega o resto do catalogo.

O que importa operacionalmente: os 10,452 pares uteis (99.2% dos vinculos) ficam em `stg_ponte_nota_saida_item_servico`, com o sentinela descartado. Era so isso que os "22% de orfaos" da secao 2 significavam.

