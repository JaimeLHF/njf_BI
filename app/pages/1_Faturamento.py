from datetime import date, timedelta

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import estilo
import tema
from componentes import card_grafico, card_kpi
from dados import (brl, consulta, delta_pct, filtro_lista, numero, opcoes,
                   periodo)

st.set_page_config(page_title="Faturamento", page_icon="💰", layout="wide")
estilo.aplicar()

st.title("Faturamento")
titulo_periodo = st.empty()

# ---------------------------------------------------------------- filtros
inicio_base, fim_base = periodo("fct_faturamento", "data_emissao")
empresas = opcoes("fct_faturamento", "id_empresa")
canais = opcoes("fct_faturamento", "canal_venda")

with st.sidebar:
    st.header("Filtros")
    de, ate = st.date_input(
        "Período",
        value=(max(inicio_base, fim_base.replace(year=fim_base.year - 2)),
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
par_anterior = (de - timedelta(days=dias), de)

# ---------------------------------------------------------------- KPIs
kpi = consulta(f"""
    SELECT sum(valor_liquido) AS receita, count(DISTINCT id_nota_saida) AS notas,
           count(DISTINCT id_cliente) AS clientes, sum(valor_bruto) AS bruto
    FROM marts.fct_faturamento WHERE {w}
""", par).iloc[0]

onde_ant = [o for o in onde if not o.startswith("data_emissao")]
kpi_ant = consulta(f"""
    SELECT sum(valor_liquido) AS receita FROM marts.fct_faturamento
    WHERE data_emissao >= ? AND data_emissao < ? AND {' AND '.join(onde_ant)}
""", par_anterior).iloc[0]

# Devolução sempre sobre o período inteiro, sem os filtros de natureza da
# operação: senão o próprio filtro zera o indicador que deveria explicar.
devolucao = consulta(f"""
    SELECT coalesce(sum(valor_liquido), 0) AS v,
           count(DISTINCT id_nota_saida) AS notas
    FROM marts.fct_faturamento
    WHERE data_emissao BETWEEN ? AND ? AND eh_devolucao_heuristica
      AND {filtro_lista('id_empresa', sel_empresa, empresas)}
      AND {filtro_lista('canal_venda', sel_canal, canais)}
""", par).iloc[0]

titulo_periodo.caption(
    f"Período: **{de:%b/%Y} a {ate:%b/%Y}**. A Home mostra só o ano corrente, "
    "por isso o número lá é menor.")

a, b, c, d = st.columns(4, gap="small")
with a:
    card_kpi("Faturamento líquido", brl(kpi.receita),
             delta_pct(kpi.receita, kpi_ant.receita))
with b:
    card_kpi("Notas emitidas", numero(kpi.notas),
             f"ticket {brl(kpi.receita / kpi.notas)}" if kpi.notas else None)
with c:
    card_kpi("Clientes ativos", numero(kpi.clientes), "distintos no período")
with d:
    card_kpi("Devoluções no período", brl(devolucao.v),
             f"{numero(devolucao.notas)} notas — medido sem os filtros de "
             "natureza da operação" if devolucao.notas else None,
             cor=tema.AMBAR)

st.write("")

# ------------------------------------------------- série ano contra ano
mensal = consulta(f"""
    SELECT year(data_emissao) AS ano, month(data_emissao) AS mes_num,
           sum(valor_liquido) / 1e6 AS receita
    FROM marts.fct_faturamento WHERE {w} GROUP BY 1, 2 ORDER BY 1, 2
""", par)

MESES = ["jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]
mensal["rotulo"] = mensal.mes_num.map(lambda m: MESES[m - 1])
hoje = date.today()
incompleto = (mensal.ano == hoje.year) & (mensal.mes_num == hoje.month)

e, f = st.columns([3, 2], gap="small")
with e:
    fig = go.Figure()
    anos = sorted(mensal.ano.unique())
    for a_ in anos:
        d_ = mensal[mensal.ano == a_]
        atual = a_ == anos[-1]
        fig.add_scatter(
            x=d_.rotulo, y=d_.receita, name=str(a_), mode="lines+markers",
            line=dict(color=tema.AZUL if atual else tema.CINZA,
                      width=2.5 if atual else 1.5,
                      dash=None if atual else "dot"),
            marker=dict(size=6 if atual else 4),
            hovertemplate="R$ %{y:.1f} mi<extra>%{fullData.name}</extra>")
    if incompleto.any():
        ponto = mensal[incompleto].iloc[0]
        fig.add_annotation(x=ponto.rotulo, y=ponto.receita, text="incompleto",
                           showarrow=True, arrowhead=0, arrowcolor=tema.AMBAR,
                           ax=0, ay=-30, font=dict(size=10, color=tema.AMBAR))
    fig.update_yaxes(title="R$ milhões")
    fig.update_xaxes(categoryorder="array", categoryarray=MESES)
    card_grafico(
        "Faturamento mensal, ano contra ano",
        tema.aplicar(fig, tema.ALTURA_LINHA, unificado=True),
        "O ano corrente em azul; anteriores pontilhados. O último ponto é um "
        "mês em andamento — a queda no fim da linha não é queda de vendas.")

with f:
    canal = consulta(f"""
        SELECT coalesce(canal_venda, 'sem canal') AS canal,
               sum(valor_liquido) / 1e6 AS receita
        FROM marts.fct_faturamento WHERE {w} GROUP BY 1 ORDER BY 2 DESC
    """, par)
    fig = px.bar(canal.head(8), x="receita", y="canal", orientation="h")
    fig.update_traces(marker_color=tema.AZUL,
                      hovertemplate="%{y}<br>R$ %{x:.1f} mi<extra></extra>")
    fig.update_yaxes(title=None, autorange="reversed")
    fig.update_xaxes(title="R$ milhões")
    card_grafico("Por canal de venda", tema.aplicar(fig, tema.ALTURA_LINHA))

st.write("")

g, h = st.columns(2, gap="small")
with g:
    canal_mes = consulta(f"""
        SELECT date_trunc('month', data_emissao) AS mes,
               coalesce(canal_venda, 'sem canal') AS canal,
               sum(valor_liquido) / 1e6 AS receita
        FROM marts.fct_faturamento WHERE {w} GROUP BY 1, 2 ORDER BY 1
    """, par)
    top = canal_mes.groupby("canal").receita.sum().nlargest(5).index
    canal_mes["canal"] = canal_mes.canal.where(canal_mes.canal.isin(top),
                                               "outros")
    fig = px.bar(canal_mes.groupby(["mes", "canal"], as_index=False).receita.sum(),
                 x="mes", y="receita", color="canal")
    fig.update_yaxes(title="R$ milhões")
    fig.update_xaxes(title=None)
    card_grafico("Composição mensal por canal", tema.aplicar(fig))

with h:
    # Substituiu o gráfico de famílias: cod_familia não tem descrição em lugar
    # nenhum do DW, e um eixo com "33299, 8430" não comunica nada.
    rep = consulta(f"""
        SELECT coalesce(nome_representante, 'sem representante') AS nome,
               sum(valor_liquido) / 1e6 AS receita,
               count(DISTINCT id_nota_saida) AS notas
        FROM marts.fct_faturamento WHERE {w}
        GROUP BY 1 ORDER BY 2 DESC LIMIT 10
    """, par)
    rep["ticket"] = rep.receita * 1e6 / rep.notas
    fig = px.bar(rep, x="receita", y="nome", orientation="h",
                 custom_data=["notas", "ticket"])
    fig.update_traces(
        marker_color=tema.AZUL,
        hovertemplate="%{y}<br>R$ %{x:.1f} mi<br>%{customdata[0]:,} notas"
                      "<br>ticket R$ %{customdata[1]:,.0f}<extra></extra>")
    fig.update_yaxes(title=None, autorange="reversed")
    fig.update_xaxes(title="R$ milhões")
    card_grafico(
        "Top 10 representantes", tema.aplicar(fig),
        "Não há gráfico por família: são 2.584 famílias sem descrição no DW e "
        "sem nível hierárquico acima — o eixo sairia só com códigos.")

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
