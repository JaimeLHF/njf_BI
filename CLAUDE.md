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
models/marts/    fct_faturamento, fct_ordem_producao, fct_pedido
app/       Streamlit: Home + 3 páginas, lendo só de `marts`
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
| `07_gerar_publicacao.py` | agrega e anonimiza para publicar | `dados_pub.duckdb` |
| `08_auditar_publicacao.py` | portão de privacidade | falha se achar PII |
| `09_comparar_publicacao.py` | paridade publicado × completo | falha se divergir |

Depois da migração, construir a camada staging (é ela que corrige a
triplicação; `06_qualidade.py` mede o efeito):

```bash
DBT_PROFILES_DIR=. uv run dbt build
```

**App.** Streamlit, três páginas (faturamento, produção, carteira):

```bash
uv run streamlit run app/Home.py
```

Testar sem navegador, o que roda cada página de verdade e captura exceções:

```bash
cd app && uv run python -c "
from streamlit.testing.v1 import AppTest
for p in ['Home.py','pages/1_Faturamento.py','pages/2_Producao.py','pages/3_Carteira.py']:
    at = AppTest.from_file(p, default_timeout=180).run()
    print(p, at.exception or 'OK')"
```

Convenções do app:

- O filtro que evita o número errado vem **ligado por padrão** e cada página diz
  no rodapé o que ele removeu.
- `brl()` escolhe a unidade pela magnitude (mil / mi / bi). Um ticket de
  R$ 17 mil não pode sair como "R$ 0,017 mi" num painel lido em pé.
- Cada KPI carrega o período no rótulo. A Home usa recortes diferentes das
  páginas de propósito (ano corrente, série completa, posição de hoje), e sem
  o rótulo isso vira pergunta na reunião.
- **Estilo Grafana, tema escuro fixo.** `.streamlit/config.toml` fixa o tema —
  sem ele o Streamlit segue o sistema e a UI fica escura com gráficos claros.
- **Nada de `st.plotly_chart` ou `st.metric` solto.** Todo gráfico vai em
  `card_grafico(titulo, fig, rodape)` e todo indicador em `card_kpi(...)`, de
  `app/componentes.py`. O título vem do card, não da figura — por isso
  `tema.aplicar` não desenha título interno.
- `app/estilo.py` traz o CSS e precisa ser chamado em **toda** página: no
  Streamlit multipage cada página é um script próprio e o CSS não atravessa.
- Alturas padrão em `tema.ALTURA_GRADE` (260px, grade 2×2) e
  `tema.ALTURA_LINHA` (300px, largura cheia). Legenda embaixo, grid só
  horizontal, `unificado=True` para hover de série temporal.
- Os banners de alerta ficam fora dos cards, de propósito.
- **Nada de gráfico com código no eixo.** `cod_familia` (2.584 valores) e
  `cod_linha_producao` (272) não têm descrição em lugar nenhum do DW — não
  viram gráfico. Onde faltava rótulo legível, o corte foi trocado por um que
  comunica: representante, faixa de tamanho da ordem, faixa de operações.
- `app/dados.py` centraliza acesso e formatação; `app/tema.py`, a paleta.
  Nenhuma página lê de `raw` nem de `staging`.

**Marts.** `marts.fct_faturamento` (grão: item de NF de saída, filtro de
natureza da operação exposto em `gera_financeiro`) e `marts.fct_ordem_producao`
(grão: ordem, com `data_conclusao_real` derivada do apontamento) e
`marts.fct_pedido` (grão: item de pedido, com carteira em aberto derivada do
faturamento real).

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

## Publicação

O app roda em dois modos. `MODO_PUBLICACAO=1` troca `dados.duckdb` por
`dados_pub.duckdb`, que tem **uma tabela agregada por gráfico** e nenhum grão de
item, pedido, nota ou ordem.

`app/consultas.py` é a fronteira: uma função por visual, que decide a fonte.
As páginas nunca montam SQL contra os marts direto — se montassem, o modo
publicação quebraria.

Regras de anonimização, garantidas por `07` e verificadas por `08`:

- nada de nome, CNPJ, CPF ou código de cliente; nada de código de item,
  família ou ordem
- representante vira "Representante A", "B", …; o de-para fica em `.local/`
- grupo com menos de 5 registros vira "Outros"
- **um canal só mantém o nome próprio se tiver ao menos 5 clientes distintos.**
  Um canal com um cliente é o nome desse cliente com outro rótulo — foi
  exatamente o que a auditoria pegou na primeira rodada.

Antes de publicar, os três scripts em sequência. `08` confronta todo texto do
arquivo contra os 7.760 nomes reais das dimensões; `09` exige que 17 KPIs
batam com o banco completo. Ambos saem com código 1 se falharem.

## Convenção de severidade nos testes dbt

- **`error`** — só para o que quebra a lógica do modelo: duplicata de chave
  primária, órfão em join obrigatório, nulo em coluna que entra em cálculo.
  Nesses casos o número sai errado sem ninguém perceber, então o build tem que
  parar.

- **`warn`** — defeito conhecido da origem, já documentado em
  `docs/qualidade.md`, que não temos como corrigir na fonte. Não quebra o
  build; serve para avisar se a proporção mudar, o que indicaria alteração na
  carga ou um lote novo do mesmo erro.

Exemplo de `warn`: `tests/proporcao_quantidade_atipica.sql` avisa se os itens
com quantidade implausível passarem de 0,1% (linha de base: 0,04%).

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

   **A aderência a prazo continua válida mesmo com apontamento em lote** — o
   último apontamento é conclusão real de qualquer jeito. O que fica
   comprometido é só o tempo de ciclo: `data_abertura` vem depois do primeiro
   apontamento em 24,8% das ordens, `lead_time_dias` é negativo em 20%, e a
   mediana de `lead_time_producao_dias` é zero dias. **Não publicar tempo de
   ciclo** até a produção confirmar o hábito de apontamento; a aderência pode
   ir para a apresentação.

4. **`flag_encerrada = 0` não significa ordem em aberto.** 96,2% dessas ordens
   já produziram. Use `cod_situacao` (1 = ativa, 0 = cancelada) mais apontamento.

5. **`fat_pedido_item.quantidade_saldo` não é saldo em aberto** — 96,6% dos
   itens com saldo positivo já foram faturados. A coluna não é baixada.
   Carteira real está em `fct_pedido.valor_em_aberto`.

   **E `origem_pedido` separa pedido de não-pedido.** `SIM` são 116.429
   pedidos e R$ 2,6 bilhões que nunca geraram **nem nota fiscal nem ordem de
   fabricação**, e estão **100% em `PE` + `BLQ`** — zero exceções em cinco
   anos, contra 84,4% de conversão de `PDV`. Não é espelho de `PDV` (clientes
   e canais diferentes: `SIM` é 90% MULTIMARCAS, `PDV` é FLAGSHIP). Leitura de
   trabalho: simulação ou pedido em negociação nunca liberado. Sem filtrar por
   `origem_converte_em_nf` a carteira dá R$ 2,8 bi em vez de R$ 189 mi.

13. **`fat_pedido` tem 155 itens com quantidade irreal** (0,04%), R$ 1.626 mi.
    Marcados em `fct_pedido` por `valor_pedido_plausivel`, sem limiar em reais:
    `flag_quantidade_igual_valor_unitario` (mesmo número nos dois campos, piso
    de 100 unidades) e `flag_quantidade_atipica` (acima de 10× o p99 do item).

    Dois cuidados que custaram uma iteração cada. O p99 de referência **precisa
    ser calculado sobre base limpa** (`quantidade <= 500`), senão se contamina
    com o próprio defeito — um item com seis pedidos falsos de 40.000 tinha
    p99 = 40.000 e passava ileso. E quantidade redonda **não** é sinal de erro:
    5.000 unidades aparecem 19 vezes em `PDV` somando R$ 0,07 mi, legítimo.

    O erro existe nas duas origens — `SIM` concentra o valor (63 itens), `PDV`
    tem mais casos (92). Não afeta a carteira. Ver `docs/qualidade.md` seção 11.

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
    As 957 notas de devolução (R$ 7,6 mi) são **todas** de tipos que não geram
    financeiro — filtrar por `gera_financeiro` já as exclui, então medir
    devolução exige tirar esse filtro, senão o indicador zera a si mesmo.

11. **`fat_pontuacao_producao.id_pontuacao` não é chave de linha**, apesar do
    COMMENT. São 40.423 valores para 101.146 linhas distintas; um único id
    carrega 3.318 linhas, 880 itens e 678 datas — é id de lote. Nunca
    deduplicar por ele. Não há chave natural fora das medidas, então a staging
    deduplica por linha inteira. Mesmo caso em
    `fat_nota_saida_item_pontuacao`.

12. **`ponte_nota_saida_item_servico` tem sentinela `id_nota_saida_item = 0`** —
    8.850 linhas, 22% do bruto, que era a origem dos "22% de órfãos" e de todo
    o excedente sobre o fator 3x. A staging descarta o sentinela. Os 62 códigos
    da LC 116 que só aparecem nele **não são anomalia**: o catálogo fiscal vem
    pré-populado com a lista inteira da lei. Ver o apêndice de
    `docs/qualidade.md`.

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
