# Perguntas de negócio candidatas — vendas e produção

Classificação: **respondível** (o dado sustenta a resposta), **parcial** (dá para
responder com ressalva ou proxy), **sem dado** (falta a informação no escopo
migrado). Toda justificativa abaixo vem de contagem medida em
`dados.duckdb`, registrada em `docs/qualidade.md`.

> **Regra que atravessa todas:** 9 das 34 tabelas migradas vieram **triplicadas**
> (linha inteira repetida, fator 3,00x). Qualquer consulta que passe por
> `ponte_nota_item_pedido_item`, `ponte_pedido_configuracao_ordem`,
> `fat_nota_saida_item_pedido`, `fat_nota_saida_item_pontuacao`,
> `fat_pontuacao_producao`, `fat_pedido_representante_secundario`,
> `ponte_nota_saida_item_servico`, `fat_contrato_loja` ou
> `fat_contrato_loja_parcela` precisa de `SELECT DISTINCT` antes de agregar.

---

## 1. Qual a aderência a prazo das ordens de fabricação? *(obrigatória)*

**Respondível — resolvida em `marts.fct_ordem_producao`.** O texto abaixo é o
diagnóstico original; a derivação foi implementada e o número mudou muito:
**32,9% no prazo**, contra 73,7% pelo cálculo ingênuo com `data_fim`. Mediana
de atraso de +11 dias, contra -13 dias (adiantado) no ingênuo. Ver
`docs/qualidade.md` seção 10.

O prazo prometido está em `data_prevista_fim` e é confiável. O problema é o
realizado: **`data_fim` não é a data em que a produção terminou**. Em 296.983
ordens encerradas com apontamento, 293.261 (**98,7%**) têm `data_fim` anterior
ao último apontamento de produção, com mediana de **-43 dias**. Comparar
`data_fim` com `data_prevista_fim` mede plano contra plano.

A data real de conclusão foi derivada como
`max(fat_ordem_movimento.data_apontamento)` por ordem, via `fat_ordem_roteiro`,
e é a coluna `data_conclusao_real` do mart. O cálculo ingênuo continua
disponível em `atraso_dias_por_data_fim`, ao lado, para a diferença ficar
visível em vez de virar discussão.

`data_entrega` é uma terceira data, nula em 9,0% das ordens, e ainda não sabemos
se é entrega ao cliente ou transferência para expedição — **confirmar com o ERP**.

Tabelas: `fat_ordem_fabricacao`, `fat_ordem_roteiro`, `fat_ordem_movimento`,
`dim_item_ordem`, `dim_empresa`, `dim_calendario`.

## 2. Qual o tamanho e a composição da carteira em aberto de 2026-2027? *(obrigatória)*

**Parcial — e o recorte 2027 é quase vazio.**

Dois problemas. Primeiro, **`fat_pedido_item.quantidade_saldo` não é saldo em
aberto**: de 175.056 itens com saldo positivo, 169.190 (**96,6%**) já foram
faturados. A coluna guarda a quantidade original e não é baixada. Carteira real =
quantidade do item menos o faturado via `ponte_nota_item_pedido_item`
**deduplicada**.

Segundo, 2027 é residual: apenas **10 pedidos** com entrega prevista em 2027 e
**28 ordens** com abertura ou previsão de fim em 2027. O volume em aberto está
concentrado em 2026 (9.507 pedidos com saldo, 33.913 ordens não encerradas com
previsão de fim em 2026). Tratar "2026-2027" como um bloco vai sugerir um
horizonte que o dado não tem.

Terceiro cuidado: `flag_encerrada = 0` **não** quer dizer ordem em aberto —
96,2% dessas ordens já produziram quantidade e 98,9% têm previsão de fim no
passado. Use `cod_situacao = 1` mais apontamento.

Tabelas: `fat_pedido`, `fat_pedido_item`, `ponte_nota_item_pedido_item`,
`fat_ordem_fabricacao`, `ponte_pedido_configuracao_ordem`.

## 3. Como evoluiu o faturamento por ano, mês, empresa, canal e representante?

**Respondível.**

`fat_nota_saida` × `fat_nota_saida_item` está íntegra: sem duplicação de carga,
sem órfão, `id_cliente` e `id_empresa` completos. `dim_cliente` traz
`canal_venda` (FLAGSHIP, MULTIMARCAS, CONTRACT, E-COMMERCE, CONSUMIDOR FINAL) e
`tipo_cliente`. Série de 2021-01 a 2026-08.

Um filtro é obrigatório: `dim_tipo_nf_saida` tem 412 tipos, dos quais só 158
geram financeiro. Somar tudo mistura remessa, bonificação e devolução com venda.
Há 59 tipos com "devolução" na descrição.

`id_representante` é nulo em 0,2% das notas — irrelevante para o total.

Tabelas: `fat_nota_saida`, `fat_nota_saida_item`, `dim_cliente`,
`dim_tipo_nf_saida`, `dim_representante`, `dim_empresa`, `dim_calendario`.

## 4. Qual o lead time real de produção, da abertura ao último apontamento?

**Parcial — e a pergunta estava mal formulada.** `data_abertura` não é o começo
do processo: em 24,8% das ordens o primeiro apontamento vem antes dela, e o
lead time medido da abertura é negativo em 20%. O mart traz
`lead_time_producao_dias` (primeiro ao último apontamento) ao lado de
`lead_time_dias`. Mas a mediana desse lead de produção é **zero dias** — quase
todo apontamento cai num único dia, o que sugere apontamento em lote no
fechamento. Tempo de ciclo real depende de confirmar o hábito de apontamento
com a produção.

`fat_ordem_movimento` tem 3.425.536 apontamentos, com `data_apontamento` e
`usuario_apontamento` preenchidos em 100% e `tempo_apontado > 0` em 91%. Liga a
`fat_ordem_roteiro` (0 órfãos) e daí à ordem. `data_abertura` é completa.

Esta é a base honesta para prazo, e resolve o problema da pergunta 1.

Tabelas: `fat_ordem_fabricacao`, `fat_ordem_roteiro`, `fat_ordem_movimento`,
`dim_centro_trabalho`, `dim_operacao`.

## 5. Onde estão os gargalos de produção, por centro de trabalho e operação?

**Respondível pelo apontamento, não pelo roteiro.**

`fat_ordem_roteiro.tempo_realizado` é uma armadilha: está preenchido em
**2.894 de 3.695.097 linhas (0,08%)**. `tempo_setup` idem, 286 linhas. Comparar
previsto contra realizado pelo roteiro dá um número calculado sobre nada.

O caminho é `fat_ordem_movimento.tempo_apontado` agregado por
`id_centro_trabalho` e `id_operacao` do roteiro, contra
`fat_ordem_roteiro.tempo_previsto` (esse sim, positivo em 91% das linhas).

Tabelas: `fat_ordem_roteiro`, `fat_ordem_movimento`, `dim_centro_trabalho`,
`dim_operacao`.

## 6. Qual a taxa de conversão de pedido em faturamento, e em quanto tempo?

**Respondível, com o desenho de junção correto.**

`ponte_nota_item_pedido_item` liga item de pedido a item de NF sem nenhum órfão,
e `fat_nota_saida_item_pedido` traz o vínculo pelo lado da nota. Com as datas de
`fat_pedido.data_emissao` e `fat_nota_saida.data_emissao` sai o tempo entre
venda e faturamento.

Duas ressalvas: as duas tabelas estão triplicadas (dedupe obrigatório), e
`fat_pedido` **não tem `id_cliente`** — o cliente do pedido só sai por
`dim_estabelecimento → dim_cliente`, enquanto a NF tem cliente direto. Uma
comparação pedido × faturamento por cliente precisa reconciliar os dois caminhos.

Tabelas: `fat_pedido`, `fat_pedido_item`, `ponte_nota_item_pedido_item`,
`fat_nota_saida`, `fat_nota_saida_item`, `dim_estabelecimento`, `dim_cliente`.

## 7. Qual o mix de produtos vendidos e produzidos, e eles conversam?

**Respondível, com atenção às três dimensões de item.**

São três: `dim_item` (catálogo global, usada pela NF e pela produção),
`dim_item_empresa` (item por empresa, **id próprio e diferente**, usada pelo
pedido e pelo item de NF) e `dim_item_ordem` (visão de produção, que faz a ponte
para `dim_item`). Cruzar as três pelo id errado produz join vazio ou multiplicado.

O caminho pedido → ordem existe (`ponte_pedido_configuracao_ordem`, 0 órfãos)
mas cobre só **61.260 dos 202.918 pedidos (30%)** — o resto não gera ordem de
fabricação. Isso é esperado num negócio que também revende, mas precisa ser dito
em qualquer visão que compare vendido com produzido.

Tabelas: `fat_nota_saida_item`, `fat_pedido_item`, `fat_ordem_fabricacao`,
`ponte_pedido_configuracao_ordem`, `dim_item`, `dim_item_empresa`,
`dim_item_ordem`, `dim_item_classificacao`.

## 8. Qual a taxa de refugo por item e por centro de trabalho?

**Sem dado confiável.**

`fat_ordem_fabricacao.quantidade_refugada` não se comporta como refugo: em
**54.439 das 54.494 ordens** com valor preenchido, a quantidade refugada é
**maior que a produzida**. O agregado dá 877.857 refugados contra 5.784.383
produzidos (15,2%), o que seria altíssimo para o setor e é provavelmente outra
grandeza — sucata em outra unidade, ou refugo acumulado do roteiro inteiro.

Além disso não há coluna de refugo em `fat_ordem_movimento`, então não dá para
atribuir refugo ao centro de trabalho. **Confirmar a semântica com o ERP** antes
de qualquer indicador de qualidade de produção.

Tabelas: `fat_ordem_fabricacao` (insuficiente).

## 9. Qual a margem por produto, cliente ou canal?

**Sem dado.**

Não há coluna de custo em nenhuma das 34 tabelas migradas. O custo unitário está
em `fat_estoque_custo` (6,5M linhas, 832 MB), que ficou fora do escopo desta
fase, e `dim_centro_trabalho.custo_hora` está **zerado nos 137 centros**, então
nem custo de transformação dá para estimar.

Responder margem exige uma segunda fase: migrar `fat_estoque_custo` e
`fat_estoque_movimento` e definir o critério de custeio com a controladoria.

Tabelas necessárias e ausentes: `fat_estoque_custo`, `fat_estoque_movimento`.

## 10. Quanto pesam as devoluções, e de quais produtos e clientes?

**Parcial.**

`dim_tipo_nf_saida` tem 59 tipos com "devolução" na descrição, o que permite
separar o fluxo. Mas `descricao_tipo_nf` é texto livre: classificar por `LIKE`
é frágil e provavelmente incompleto, e `flag_gera_financeiro` /
`flag_movimenta_estoque` estão documentados apenas como "indicador auxiliar" —
o COMMENT não diz o que 0 e 1 significam.

Antes de virar indicador, é preciso **mapear os CFOPs com a fiscal** e fixar a
lista de tipos que contam como devolução.

Tabelas: `fat_nota_saida`, `fat_nota_saida_item`, `dim_tipo_nf_saida`,
`dim_cliente`, `dim_item`.

---

## Resumo

| # | Pergunta | Status |
|---|----------|--------|
| 1 | Aderência a prazo de produção | **respondível** (implementada) |
| 2 | Carteira em aberto 2026-2027 | parcial |
| 3 | Faturamento por ano/canal/representante | **respondível** (implementada) |
| 4 | Lead time real de produção | parcial |
| 5 | Gargalos por centro de trabalho | respondível |
| 6 | Conversão pedido → faturamento | respondível |
| 7 | Mix vendido × produzido | respondível |
| 8 | Taxa de refugo | sem dado |
| 9 | Margem | sem dado |
| 10 | Devoluções | parcial |
