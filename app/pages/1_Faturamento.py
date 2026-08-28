import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import tema
from dados import brl, consulta, delta_pct, filtro_lista, numero, opcoes, periodo

st.set_page_config(page_title="Faturamento", page_icon="💰", layout="wide")
st.title("Faturamento")
titulo_periodo = st.empty()

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
         f"ticket {brl(kpi.receita / kpi.notas) if kpi.notas else '—'}")
c.metric("Clientes ativos", numero(kpi.clientes))
d.metric("Devoluções no período", brl(devolucao.v),
         f"{numero(devolucao.notas)} notas" if devolucao.notas else None,
         delta_color="inverse",
         help="Medido sobre o período inteiro, independente dos filtros de "
              "natureza da operação — do contrário o filtro zeraria o próprio "
              "indicador.")

titulo_periodo.caption(
    f"Período: **{de:%b/%Y} a {ate:%b/%Y}**. A Home mostra só o ano corrente, "
    "por isso o número lá é menor.")

st.divider()

# ---------------------------------------------------------------- gráficos
# Série por mês do ano, para sobrepor os anos no mesmo eixo.
mensal = consulta(f"""
    SELECT year(data_emissao) AS ano, month(data_emissao) AS mes_num,
           sum(valor_liquido) / 1e6 AS receita
    FROM marts.fct_faturamento WHERE {w} GROUP BY 1, 2 ORDER BY 1, 2
""", par)

MESES = ["jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]
mensal["rotulo"] = mensal.mes_num.map(lambda m: MESES[m - 1])

# O mês corrente está incompleto: sem marcar isso a queda no fim da série
# parece colapso de vendas.
hoje = __import__("datetime").date.today()
incompleto = (mensal.ano == hoje.year) & (mensal.mes_num == hoje.month)

e, f = st.columns([3, 2])
with e:
    fig = go.Figure()
    anos = sorted(mensal.ano.unique())
    for i, a_ in enumerate(anos):
        d = mensal[mensal.ano == a_]
        atual = a_ == anos[-1]
        fig.add_scatter(
            x=d.rotulo, y=d.receita, name=str(a_), mode="lines+markers",
            line=dict(color=tema.AZUL if atual else tema.CINZA,
                      width=3 if atual else 1.5,
                      dash=None if atual else "dot"),
            marker=dict(size=7 if atual else 4),
            hovertemplate=f"{a_} %{{x}}<br>R$ %{{y:.1f}} mi<extra></extra>")
    if incompleto.any():
        ponto = mensal[incompleto].iloc[0]
        fig.add_scatter(
            x=[ponto.rotulo], y=[ponto.receita], mode="markers", name="incompleto",
            marker=dict(size=14, color="white", line=dict(color=tema.AMBAR, width=3)),
            hovertemplate=f"{ponto.rotulo} — mês em andamento<extra></extra>")
        fig.add_annotation(x=ponto.rotulo, y=ponto.receita, text="mês<br>incompleto",
                           showarrow=True, arrowhead=0, ax=0, ay=-38,
                           font=dict(size=11, color=tema.AMBAR))
    fig.update_yaxes(title="R$ milhões")
    fig.update_xaxes(title=None, categoryorder="array", categoryarray=MESES)
    st.plotly_chart(tema.aplicar(fig, "Faturamento mensal, ano contra ano"),
                    width='stretch')

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
    # Substituiu o gráfico de famílias: cod_familia não tem descrição em lugar
    # nenhum do DW, e um eixo com "33299, 8430, 44879" não comunica nada.
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
    st.plotly_chart(tema.aplicar(fig, "Top 10 representantes"), width='stretch')

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
st.caption("Não há gráfico por família de produto: são 2.584 famílias sem "
           "descrição no DW e sem nível hierárquico acima, então o eixo sairia "
           "só com códigos. Ver `docs/qualidade.md`, pergunta 7.")

st.caption("Os filtros padrão removeram " + " e ".join(partes) + "."
           if partes else "Nenhum filtro de natureza da operação está ativo — "
                          "o total mistura venda com remessa e devolução.")
