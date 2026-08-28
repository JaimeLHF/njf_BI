import plotly.express as px
import streamlit as st

import tema
from dados import brl, consulta, delta_pct, filtro_lista, numero, opcoes, periodo

st.set_page_config(page_title="Faturamento", page_icon="💰", layout="wide")
st.title("Faturamento")

# ---------------------------------------------------------------- filtros
inicio_base, fim_base = periodo("fct_faturamento", "data_emissao")
empresas = opcoes("fct_faturamento", "id_empresa")
canais = opcoes("fct_faturamento", "canal_venda")

with st.sidebar:
    st.header("Filtros")
    de, ate = st.date_input(
        "Período", value=(max(inicio_base, fim_base.replace(year=fim_base.year - 2)),
                          fim_base),
        min_value=inicio_base, max_value=fim_base)
    sel_empresa = st.multiselect("Empresa", empresas)
    sel_canal = st.multiselect("Canal de venda", canais)

    st.divider()
    st.caption("**Filtros de natureza da operação**")
    so_financeiro = st.checkbox(
        "Só NF que gera financeiro", value=True,
        help="Dos 412 tipos de NF, só 158 geram financeiro. Sem isso o total "
             "mistura remessa, bonificação e amostra com venda.")
    sem_devolucao = st.checkbox(
        "Excluir devoluções", value=True,
        help="Redundante enquanto o filtro acima estiver ligado: todas as 957 "
             "notas de devolução já são de tipos que não geram financeiro. "
             "Fica aqui porque a classificação é por texto na descrição do "
             "tipo de NF, e a lista definitiva de CFOPs precisa vir da fiscal.")

onde = [
    "data_emissao BETWEEN ? AND ?",
    filtro_lista("id_empresa", sel_empresa, empresas),
    filtro_lista("canal_venda", sel_canal, canais),
]
if so_financeiro:
    onde.append("gera_financeiro")
if sem_devolucao:
    onde.append("NOT eh_devolucao_heuristica")
w = " AND ".join(onde)
par = (de, ate)

dias = (ate - de).days or 1
par_anterior = (de - __import__("datetime").timedelta(days=dias), de)

# ---------------------------------------------------------------- KPIs
kpi = consulta(f"""
    SELECT sum(valor_liquido) AS receita, count(DISTINCT id_nota_saida) AS notas,
           count(DISTINCT id_cliente) AS clientes,
           sum(valor_bruto) AS bruto
    FROM marts.fct_faturamento WHERE {w}
""", par).iloc[0]

onde_ant = [o for o in onde if not o.startswith("data_emissao")]
kpi_ant = consulta(f"""
    SELECT sum(valor_liquido) AS receita
    FROM marts.fct_faturamento
    WHERE data_emissao >= ? AND data_emissao < ? AND {' AND '.join(onde_ant)}
""", par_anterior).iloc[0]

# Devolução é sempre medida sobre o período inteiro, sem os filtros de
# natureza da operação: senão o próprio filtro zera o indicador que ele deveria
# explicar. Todas as devoluções são de tipos que não geram financeiro.
devolucao = consulta(f"""
    SELECT coalesce(sum(valor_liquido), 0) AS v,
           count(DISTINCT id_nota_saida) AS notas
    FROM marts.fct_faturamento
    WHERE data_emissao BETWEEN ? AND ? AND eh_devolucao_heuristica
      AND {filtro_lista('id_empresa', sel_empresa, empresas)}
      AND {filtro_lista('canal_venda', sel_canal, canais)}
""", par).iloc[0]

a, b, c, d = st.columns(4)
a.metric("Faturamento líquido", brl(kpi.receita),
         delta_pct(kpi.receita, kpi_ant.receita))
b.metric("Notas emitidas", numero(kpi.notas),
         f"ticket {brl(kpi.receita / kpi.notas, 3) if kpi.notas else '—'}")
c.metric("Clientes ativos", numero(kpi.clientes))
d.metric("Devoluções no período", brl(devolucao.v),
         f"{numero(devolucao.notas)} notas" if devolucao.notas else None,
         delta_color="inverse",
         help="Medido sobre o período inteiro, independente dos filtros de "
              "natureza da operação — do contrário o filtro zeraria o próprio "
              "indicador.")

st.divider()

# ---------------------------------------------------------------- gráficos
mensal = consulta(f"""
    SELECT date_trunc('month', data_emissao) AS mes,
           sum(valor_liquido) / 1e6 AS receita,
           count(DISTINCT id_nota_saida) AS notas
    FROM marts.fct_faturamento WHERE {w} GROUP BY 1 ORDER BY 1
""", par)

e, f = st.columns([3, 2])
with e:
    fig = px.line(mensal, x="mes", y="receita", markers=True)
    fig.update_traces(line_color=tema.AZUL, hovertemplate="%{x|%b/%Y}<br>R$ %{y:.1f} mi")
    fig.update_yaxes(title="R$ milhões")
    fig.update_xaxes(title=None)
    st.plotly_chart(tema.aplicar(fig, "Faturamento mensal"), width='stretch')

with f:
    canal = consulta(f"""
        SELECT coalesce(canal_venda, 'sem canal') AS canal,
               sum(valor_liquido) / 1e6 AS receita
        FROM marts.fct_faturamento WHERE {w} GROUP BY 1 ORDER BY 2 DESC
    """, par)
    fig = px.bar(canal.head(8), x="receita", y="canal", orientation="h")
    fig.update_traces(marker_color=tema.AZUL, hovertemplate="%{y}<br>R$ %{x:.1f} mi")
    fig.update_yaxes(title=None, autorange="reversed")
    fig.update_xaxes(title="R$ milhões")
    st.plotly_chart(tema.aplicar(fig, "Por canal de venda"), width='stretch')

g, h = st.columns(2)
with g:
    canal_mes = consulta(f"""
        SELECT date_trunc('month', data_emissao) AS mes,
               coalesce(canal_venda, 'sem canal') AS canal,
               sum(valor_liquido) / 1e6 AS receita
        FROM marts.fct_faturamento WHERE {w} GROUP BY 1, 2 ORDER BY 1
    """, par)
    top = canal_mes.groupby("canal").receita.sum().nlargest(5).index
    canal_mes["canal"] = canal_mes.canal.where(canal_mes.canal.isin(top), "outros")
    fig = px.bar(canal_mes.groupby(["mes", "canal"], as_index=False).receita.sum(),
                 x="mes", y="receita", color="canal")
    fig.update_yaxes(title="R$ milhões")
    fig.update_xaxes(title=None)
    st.plotly_chart(tema.aplicar(fig, "Composição mensal por canal"),
                    width='stretch')

with h:
    fam = consulta(f"""
        SELECT CAST(cod_familia AS VARCHAR) AS familia,
               sum(valor_liquido) / 1e6 AS receita
        FROM marts.fct_faturamento WHERE {w} AND cod_familia IS NOT NULL
        GROUP BY 1 ORDER BY 2 DESC LIMIT 15
    """, par)
    fig = px.bar(fam, x="receita", y="familia", orientation="h")
    fig.update_traces(marker_color=tema.AZUL_CLARO)
    fig.update_yaxes(title=None, autorange="reversed", type="category")
    fig.update_xaxes(title="R$ milhões")
    st.plotly_chart(
        tema.aplicar(fig, "Top 15 famílias — 2.584 no total, sem hierarquia acima"),
        width='stretch')

# ---------------------------------------------------------------- rodapé
removido = consulta(f"""
    SELECT count(DISTINCT id_nota_saida) FILTER (WHERE NOT gera_financeiro) AS sem_fin,
           count(DISTINCT id_nota_saida) FILTER (WHERE eh_devolucao_heuristica) AS devol
    FROM marts.fct_faturamento
    WHERE data_emissao BETWEEN ? AND ?
      AND {filtro_lista('id_empresa', sel_empresa, empresas)}
      AND {filtro_lista('canal_venda', sel_canal, canais)}
""", par).iloc[0]

partes = []
if so_financeiro:
    partes.append(f"**{numero(removido.sem_fin)} notas** de tipos que não geram "
                  "financeiro (remessa, bonificação, amostra)")
if sem_devolucao:
    partes.append(f"**{numero(removido.devol)} notas** de devolução")
st.caption("Os filtros padrão removeram " + " e ".join(partes) + "."
           if partes else "Nenhum filtro de natureza da operação está ativo — "
                          "o total mistura venda com remessa e devolução.")
