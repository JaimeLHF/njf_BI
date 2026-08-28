"""Acesso ao DuckDB para o app. Sempre read-only e sempre sobre `marts`.

Regra do projeto: nada aqui lê de `raw` nem de `staging`. `raw` continua
consultável para demonstrar a triplicação, mas não alimenta indicador.

Dois modos:
  - local (padrão): `dados.duckdb`, no grão dos marts, filtros livres.
  - publicação: `dados_pub.duckdb`, só tabelas agregadas, recorte fixo.
    É o que vai para o Streamlit Community Cloud.

O modo é decidido em três etapas, nesta ordem:

  1. variável de ambiente `MODO_PUBLICACAO=1` — é o que se usa no shell local
  2. secret `MODO_PUBLICACAO = "1"` — o Streamlit Cloud NÃO exporta secrets
     como variável de ambiente, então é preciso ler `st.secrets` também
  3. se nenhuma das duas disser nada: usa o arquivo que existir. No Cloud só
     existe `dados_pub.duckdb`, porque `dados.duckdb` está no .gitignore

A etapa 3 é o que torna o deploy à prova de configuração esquecida — sem ela,
o app subia apontando para um arquivo inexistente e quebrava na primeira
consulta.

As páginas não sabem em qual modo estão: perguntam a `consultas.py`.
"""
import os
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
COMPLETO = RAIZ / "dados.duckdb"
AGREGADO = RAIZ / "dados_pub.duckdb"


def _secret(nome: str) -> str | None:
    """st.secrets levanta exceção quando não há secrets.toml nenhum."""
    try:
        return st.secrets.get(nome)
    except Exception:
        return None


def _modo_publicacao() -> bool:
    for valor in (os.environ.get("MODO_PUBLICACAO"), _secret("MODO_PUBLICACAO")):
        if valor is not None:
            return str(valor).strip() == "1"
    # ninguém disse nada: decide pelo que existe no disco
    return not COMPLETO.exists() and AGREGADO.exists()


PUBLICACAO = _modo_publicacao()
BANCO = AGREGADO if PUBLICACAO else COMPLETO

AVISO_PUBLICACAO = (
    "Versão de demonstração com dados agregados e anonimizados."
)


@st.cache_resource
def conexao():
    if not BANCO.exists():
        st.error(
            f"Banco não encontrado: `{BANCO.name}`.\n\n"
            "No Streamlit Cloud isso significa que `dados_pub.duckdb` não subiu "
            "com o repositório. Local, rode `scripts/04_migrar_duckdb.py` e "
            "`dbt build` para gerar `dados.duckdb`.")
        st.stop()
    return duckdb.connect(str(BANCO), read_only=True)


@st.cache_data(ttl=3600)
def consulta(sql: str, params: tuple = ()) -> pd.DataFrame:
    return conexao().execute(sql, params).df()


@st.cache_data(ttl=3600)
def recorte() -> dict:
    """Janela fixa do arquivo publicado. No modo local devolve vazio."""
    if not PUBLICACAO:
        return {}
    return consulta("SELECT * FROM pub_recorte").iloc[0].to_dict()


@st.cache_data(ttl=3600)
def opcoes(tabela: str, coluna: str, onde: str = "1=1") -> list:
    """Vazio no modo publicação: o arquivo agregado não tem o grão para
    alimentar filtro, e as páginas escondem os multiselect nesse modo."""
    if PUBLICACAO:
        return []
    df = consulta(
        f"SELECT DISTINCT {coluna} AS v FROM marts.{tabela} "
        f"WHERE {onde} AND {coluna} IS NOT NULL ORDER BY 1"
    )
    return df["v"].tolist()


@st.cache_data(ttl=3600)
def periodo(tabela: str, coluna: str) -> tuple:
    """No modo publicação vem de pub_recorte, a janela fixa do arquivo."""
    if PUBLICACAO:
        r = recorte()
        if tabela == "fct_faturamento":
            return r["faturamento_de"], r["faturamento_ate"]
        return r["producao_de"], r["producao_ate"]
    df = consulta(f"SELECT min({coluna}) a, max({coluna}) b FROM marts.{tabela}")
    return df["a"].iloc[0], df["b"].iloc[0]


def filtro_lista(coluna: str, selecionados: list, todos: list) -> str:
    """Vira SQL só quando o usuário restringiu de fato."""
    if not selecionados or len(selecionados) == len(todos):
        return "1=1"
    valores = ", ".join(
        "'" + str(v).replace("'", "''") + "'" for v in selecionados
    )
    return f"{coluna} IN ({valores})"


def rodape_publicacao() -> None:
    """Aviso no pé de toda página, só no modo publicação."""
    if PUBLICACAO:
        st.caption(f":gray[{AVISO_PUBLICACAO}]")


def brl(v, casas=1) -> str:
    """R$ na unidade que a magnitude pede. Um ticket médio de R$ 17 mil não
    pode sair como 'R$ 0,017 mi' num painel que alguém lê em pé numa reunião."""
    if v is None or pd.isna(v):
        return "—"
    sinal = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1e9:
        corpo, unidade = v / 1e9, " bi"
    elif v >= 1e6:
        corpo, unidade = v / 1e6, " mi"
    elif v >= 1e3:
        corpo, unidade = v / 1e3, " mil"
    else:
        # abaixo de mil já são reais e centavos, não faz sentido 1 casa
        corpo, unidade, casas = v, "", 2
    texto = f"{corpo:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{sinal}R$ {texto}{unidade}"


def numero(v) -> str:
    if v is None or pd.isna(v):
        return "—"
    return f"{v:,.0f}".replace(",", ".")


def pct(v, casas=1) -> str:
    if v is None or pd.isna(v):
        return "—"
    return f"{v:.{casas}f}%".replace(".", ",")


def delta_pct(atual, anterior) -> str | None:
    if not anterior or pd.isna(anterior) or pd.isna(atual):
        return None
    v = (atual / anterior - 1) * 100
    return f"{v:+.1f}% vs período anterior".replace(".", ",")
