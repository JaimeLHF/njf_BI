"""Acesso ao DuckDB para o app. Sempre read-only e sempre sobre `marts`.

Regra do projeto: nada aqui lê de `raw` nem de `staging`. `raw` continua
consultável para demonstrar a triplicação, mas não alimenta indicador.
"""
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

BANCO = Path(__file__).resolve().parent.parent / "dados.duckdb"


@st.cache_resource
def conexao():
    return duckdb.connect(str(BANCO), read_only=True)


@st.cache_data(ttl=3600)
def consulta(sql: str, params: tuple = ()) -> pd.DataFrame:
    return conexao().execute(sql, params).df()


@st.cache_data(ttl=3600)
def opcoes(tabela: str, coluna: str, onde: str = "1=1") -> list:
    df = consulta(
        f"SELECT DISTINCT {coluna} AS v FROM marts.{tabela} "
        f"WHERE {onde} AND {coluna} IS NOT NULL ORDER BY 1"
    )
    return df["v"].tolist()


@st.cache_data(ttl=3600)
def periodo(tabela: str, coluna: str) -> tuple:
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
