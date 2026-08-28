# njf_BI

BI sobre o data warehouse `erp_bi` de uma indústria de produção sob
configuração. Escopo: **vendas e produção**.

O ponto do projeto não é o painel — é o que foi preciso descobrir para o painel
não mentir. Três exemplos, todos medidos e documentados em
[`docs/qualidade.md`](docs/qualidade.md):

| descoberta | efeito |
|---|---|
| 9 tabelas da origem vieram **triplicadas** (ETL rodado 3x sem truncate) | qualquer soma sobre elas ficava 3x maior |
| `data_fim` da ordem é **anterior ao último apontamento** em 98,7% dos casos | aderência a prazo caía de 73,7% para **32,9%** ao medir certo |
| `origem_pedido = 'SIM'` são R$ 2,6 bi que **nunca geraram nota nem ordem** | carteira caía de R$ 2,8 bi para **R$ 189 mi** |

## Rodar local

Precisa do Postgres com o schema `bi` e de um `.env` com as credenciais
(`PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER`, `PG_PASSWORD`, `PG_SCHEMA`).

```bash
uv sync

cd scripts
uv run python 01_dicionario.py         # dicionário a partir do catálogo
uv run python 02_relacionamentos.py    # resolve e valida as FKs
uv run python 03_modelo.py             # diagramas do star schema
uv run python 04_migrar_duckdb.py      # Postgres -> raw no DuckDB
uv run python 05_profiling.py          # perfilamento em reports/
uv run python 06_qualidade.py          # docs/qualidade.md
cd ..

DBT_PROFILES_DIR=. uv run dbt build    # staging + marts, 62 testes
uv run streamlit run app/Home.py
```

## Rodar a versão publicada

A versão publicada lê `dados_pub.duckdb`, um arquivo agregado e anonimizado.
Para ver como ela fica antes de publicar:

```bash
MODO_PUBLICACAO=1 uv run streamlit run app/Home.py
```

## Publicar no Streamlit Community Cloud

```bash
cd scripts
uv run python 07_gerar_publicacao.py    # gera dados_pub.duckdb (3 MB)
uv run python 08_auditar_publicacao.py  # portão: reprova se achar algo identificável
uv run python 09_comparar_publicacao.py # 17 KPIs têm de bater com o banco completo
```

Depois aponte o Streamlit Cloud para `app/Home.py`, branch `master`. As
dependências saem de `requirements.txt`, com versões fixas — o Cloud não usa
`uv`.

Não é preciso configurar nada além disso: o app detecta o modo pelo arquivo que
existe em disco, e no Cloud só existe `dados_pub.duckdb`, porque
`dados.duckdb` está no `.gitignore`.

> Se quiser forçar explicitamente, `MODO_PUBLICACAO=1` funciona como variável de
> ambiente **e** como secret. Vale saber que **o Streamlit Cloud não exporta
> secrets como variáveis de ambiente** — `os.environ` não os enxerga. Por isso
> `app/dados.py` lê `st.secrets` também, e por isso a detecção por arquivo
> existe: um deploy não deve quebrar por causa de um campo esquecido.

### O que a versão publicada não tem

O arquivo publicado guarda **uma tabela por gráfico, já agregada**. Não existe
nele o grão de item, pedido, nota ou ordem, e portanto não há como reconstruir
uma linha individual.

- sem nome, CNPJ, CPF ou código de cliente
- sem nome de representante: viram "Representante A", "B", … por ordem de
  faturamento; o de-para fica em `.local/`, fora do repo
- sem código de item, família ou ordem
- todo grupo com menos de 5 registros vira "Outros" — e um canal só sobrevive
  com nome próprio se tiver ao menos 5 clientes distintos, porque um canal com
  um cliente é o nome desse cliente com outro rótulo
- filtros desativados: o recorte é fixo (últimos 2 anos), o mesmo que a versão
  local abre por padrão, para os números baterem

`scripts/08_auditar_publicacao.py` confronta todo texto do arquivo publicado
contra os 7.760 nomes reais das dimensões e falha se algum aparecer.

## Estrutura

```
scripts/   pipeline numerado, de 01 a 09
models/    dbt: staging (corrige a origem) e marts (fatos de consumo)
app/       Streamlit: Home + 3 páginas, lendo só de marts
docs/      dicionário, modelo, qualidade e perguntas de negócio
```

Convenções, armadilhas dos dados e decisões de modelagem estão em
[`CLAUDE.md`](CLAUDE.md).
