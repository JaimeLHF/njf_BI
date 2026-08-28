# njf_BI

BI local sobre o DW `erp_bi` de uma indústria de produção sob configuração.
Fase atual: **exploração**. Escopo: **vendas e produção**. Contábil, financeiro,
compras e estoque estão fora por ora.

## Stack

`uv` (Python 3.12) · DuckDB · Polars · dbt-core + dbt-duckdb ·
ydata-profiling · Plotly · Jupyter

Postgres local `erp_bi`, schema `bi`, credenciais no `.env` (lidas com
python-dotenv). **Somente SELECT** — a conexão em `scripts/_db.py` abre a sessão
com `readonly=True`.

## Estrutura

```
scripts/   _db.py e os 6 scripts numerados do pipeline
docs/      dicionario.md, modelo.md, qualidade.md, perguntas.md
reports/   1 HTML de profiling por tabela (gitignored)
models/staging/  camada dbt que corrige a triplicação da origem
models/marts/    fct_faturamento e fct_ordem_producao
macros/    generate_schema_name
tests/generic/   teste chave_unica
notebooks/ análise exploratória
dados.duckdb   schema raw com as 34 tabelas migradas (gitignored)
```

## Pipeline

| script | o que faz | saída |
|--------|-----------|-------|
| `01_dicionario.py` | extrai o catálogo do Postgres | `docs/dicionario.md`, `docs/catalogo.json` |
| `02_relacionamentos.py` | resolve e valida as FKs | `docs/relacionamentos.json` |
| `03_modelo.py` | diagramas do star schema | `docs/modelo.md` |
| `04_migrar_duckdb.py` | Postgres → `raw` no DuckDB | `dados.duckdb` |
| `05_profiling.py` | perfila as tabelas migradas | `reports/*.html` |
| `06_qualidade.py` | checks de qualidade | `docs/qualidade.md` |

Depois da migração, construir a camada staging (é ela que corrige a
triplicação; `06_qualidade.py` mede o efeito):

```bash
DBT_PROFILES_DIR=. uv run dbt build
```

**Marts.** `marts.fct_faturamento` (grão: item de NF de saída, filtro de
natureza da operação exposto em `gera_financeiro`) e `marts.fct_ordem_producao`
(grão: ordem, com `data_conclusao_real` derivada do apontamento).

Rodar tudo:

```bash
cd scripts
uv run python 01_dicionario.py && uv run python 02_relacionamentos.py \
  && uv run python 03_modelo.py && uv run python 04_migrar_duckdb.py \
  && uv run python 05_profiling.py && uv run python 06_qualidade.py
```

## O modelo em uma página

Star schema com prefixos `dim_`, `fat_`, `ponte_`. 91 objetos no schema `bi`,
34 migrados para `raw` (11 vendas, 5 produção, 18 dimensões).

**Vendas.** `fat_pedido` → `fat_pedido_item` → `ponte_nota_item_pedido_item` →
`fat_nota_saida_item` → `fat_nota_saida`. Dimensões: `dim_cliente`,
`dim_estabelecimento`, `dim_representante`, `dim_tipo_nf_saida`,
`dim_item_empresa`, `dim_condicao_pagamento`, `dim_empresa`.

**Produção.** `fat_ordem_fabricacao` → `fat_ordem_roteiro` →
`fat_ordem_movimento`. Dimensões: `dim_item_ordem`, `dim_operacao`,
`dim_centro_trabalho`, `dim_empresa`.

**Ligação.** `ponte_pedido_configuracao_ordem` é o único caminho pedido ↔ ordem,
e cobre 30% dos pedidos.

`dim_calendario` liga por igualdade de data, em vários papéis por fato.
Detalhe completo com contagens em `docs/modelo.md`.

## Convenções

- Ambiente sempre via `uv run`; nunca `pip` nem venv manual.
- Postgres é **read-only**. DuckDB é o ambiente de trabalho.
- **Nunca imprimir linhas de dado no terminal** — só agregados, contagens e
  metadados. Dado de cliente é confidencial; `05_profiling.py` mascara por hash
  as colunas com nome, CNPJ, CPF, endereço e usuário antes de perfilar.
- Não tocar em `dim_configurador` (8,0M linhas) nem `dim_mascara` (1,8M):
  grandes e fora do escopo.
- Commit ao final de cada etapa.
- Documentação gerada por script, nunca escrita à mão — reexecutar o script é o
  jeito de atualizar.

## Armadilhas que já custaram tempo

Todas medidas e registradas em `docs/qualidade.md`.

1. **O banco não tem FOREIGN KEY como constraint.** Mas os COMMENTs de coluna
   declaram o alvo em texto: `[FK -> dim_empresa.id_empresa]`. Essa é a fonte
   primária; `02_relacionamentos.py` a lê e valida medindo órfãos.

2. **9 tabelas vieram triplicadas na origem** — linha inteira repetida, fator
   3,00x, exatamente as que não têm PK. Assinatura de ETL do DW rodado 3x sem
   truncate; a migração é single-pass e não pode ter causado.
   **Corrigido em `models/staging/`**, com dedup explícita por chave natural e
   teste `chave_unica` que trava a regressão. Leia sempre de `staging`, nunca de
   `raw`. `raw` fica intacto de propósito, para o defeito continuar visível.
   Isso afeta relatórios que a empresa já tenha em cima dessas tabelas —
   ver `docs/qualidade.md` seção 8.

   > **`raw` fica consultável de propósito.** É a evidência da triplicação para
   > a apresentação — não revogar o acesso nem renomear o schema. Mas nenhum
   > modelo, notebook ou dashboard deve ler de `raw`: leia de `staging`.

3. **`fat_ordem_fabricacao.data_fim` não é a data real de término.** É anterior
   ao último apontamento em 98,7% das ordens encerradas (mediana -43 dias).
   A conclusão real é `max(fat_ordem_movimento.data_apontamento)` por ordem,
   já materializada em `fct_ordem_producao.data_conclusao_real`. O indicador
   muda **41 pontos**: 32,9% no prazo contra 73,7% pelo cálculo ingênuo.

   **`data_abertura` também não é o começo.** Em 24,8% das ordens o primeiro
   apontamento vem antes dela; `lead_time_dias` é negativo em 20%. Use
   `lead_time_producao_dias`, e note que a mediana dele é zero dias — o
   apontamento parece ser feito em lote.

4. **`flag_encerrada = 0` não significa ordem em aberto.** 96,2% dessas ordens
   já produziram. Use `cod_situacao` (1 = ativa, 0 = cancelada) mais apontamento.

5. **`fat_pedido_item.quantidade_saldo` não é saldo em aberto** — 96,6% dos
   itens com saldo positivo já foram faturados. A coluna não é baixada.

6. **`fat_ordem_roteiro.tempo_realizado` está vazio** (2.894 de 3,7M linhas).
   Tempo real vem de `fat_ordem_movimento.tempo_apontado`, preenchido em 91%.

7. **`fat_nota_saida_item_pontuacao.id_ordem_fabricacao` guarda `num_ordem`**,
   não a PK. Junte por `num_ordem`.

8. **`fat_pedido` não tem `id_cliente`.** O cliente do pedido sai por
   `dim_estabelecimento → dim_cliente`. A NF de saída tem cliente direto.

9. **Três dimensões de item, com ids diferentes.** `dim_item` (catálogo global,
   NF e produção), `dim_item_empresa` (por empresa, id próprio, pedido e item de
   NF), `dim_item_ordem` (produção, faz ponte para `dim_item`).

10. **`dim_tipo_nf_saida` tem 412 tipos e só 158 geram financeiro.** Somar
    faturamento sem filtrar mistura remessa, bonificação e devolução com venda.

11. **`fat_pontuacao_producao.id_pontuacao` não é chave de linha**, apesar do
    COMMENT. São 40.423 valores para 101.146 linhas distintas; um único id
    carrega 3.318 linhas, 880 itens e 678 datas — é id de lote. Nunca
    deduplicar por ele. Não há chave natural fora das medidas, então a staging
    deduplica por linha inteira. Mesmo caso em
    `fat_nota_saida_item_pontuacao`.

12. **`ponte_nota_saida_item_servico` tem sentinela `id_nota_saida_item = 0`** —
    8.850 linhas, 22% do bruto, que era a origem dos "22% de órfãos" e de todo
    o excedente sobre o fator 3x. A staging descarta o sentinela. Consequência
    fiscal: **62 dos 84 códigos de serviço da LC 116 (74%) não têm uma única
    nota vinculada** — ISS por tipo de serviço vai mostrá-los zerados sem que
    o DW diga se é ausência de movimento ou vínculo perdido na carga.
    Ver `docs/qualidade.md` seção 9.

## Métricas de negócio inferidas do dicionário

Nenhuma está calculada ainda — são as candidatas que o modelo sustenta.

**Vendas.** Faturamento bruto e líquido (`fat_nota_saida_item.valor_bruto` /
`valor_liquido`, filtrado por tipo de NF que gera financeiro), ticket médio por
nota e por cliente, mix por canal (`dim_cliente.canal_venda`: FLAGSHIP,
MULTIMARCAS, CONTRACT, E-COMMERCE, CONSUMIDOR FINAL), desempenho por
representante, desconto médio (`fat_pedido.valor_desconto / valor_bruto`),
taxa de conversão pedido → NF e o tempo entre elas, carteira em aberto
(quantidade do item menos o faturado pela ponte deduplicada), taxa de
cancelamento (`situacao_pedido = 'C'`), peso das devoluções.

**Produção.** Aderência a prazo (`data_prevista_fim` contra a conclusão real
derivada do apontamento), lead time da abertura ao último apontamento, volume
produzido (`quantidade_produzida`), horas apontadas por centro de trabalho e
operação, previsto contra realizado por operação
(`fat_ordem_roteiro.tempo_previsto` contra `tempo_apontado` do movimento),
pontuação de produção (`fat_pontuacao_producao`, deduplicar).

**Sem base no escopo atual.** Margem e custo — não há coluna de custo nas 34
tabelas, `dim_centro_trabalho.custo_hora` está zerado, e o custo unitário mora
em `fat_estoque_custo`, fora desta fase. Taxa de refugo — `quantidade_refugada`
é maior que a produzida em 54.439 de 54.494 ordens; semântica a confirmar.

## Cobertura temporal

Vendas de 2021-01 a 2026-08. Pedidos de 2020-01 a 2026-08. Ordens de fabricação
abertas de 2020-01 a 2027-11, mas **2027 tem só 28 ordens e 10 pedidos** — a
carteira em aberto está concentrada em 2026.
