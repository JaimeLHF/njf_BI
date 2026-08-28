import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import tema
from dados import consulta, filtro_lista, numero, opcoes, pct, periodo

st.set_page_config(page_title="Produção", page_icon="🏭", layout="wide")
st.title("Aderência a prazo de produção")

st.warning(
    "**Esta página não mostra tempo de ciclo.** O apontamento parece ser feito "
    "em lote: a mediana entre o primeiro e o último apontamento de uma ordem é "
    "zero dias. A aderência a prazo abaixo continua válida — ela usa o *último* "
    "apontamento, que é conclusão real de qualquer forma. Ver "
    "`docs/qualidade.md`, seção 9.", icon="⚠️")

# ---------------------------------------------------------------- filtros
inicio, fim = periodo("fct_ordem_producao", "data_conclusao_real")
empresas = opcoes("fct_ordem_producao", "id_empresa")
tipos = opcoes("fct_ordem_producao", "tipo_ordem")

with st.sidebar:
    st.header("Filtros")
    de, ate = st.date_input(
        "Conclusão real entre",
        value=(max(inicio, fim.replace(year=fim.year - 2)), fim),
        min_value=inicio, max_value=fim)
    sel_empresa = st.multiselect("Empresa", empresas)
    sel_tipo = st.multiselect("Tipo de ordem", tipos)

    st.divider()
    st.caption("**Recorte de ordens**")
    so_ativas = st.checkbox(
        "Só ordens ativas", value=True,
        help="cod_situacao = 1. As de situação 0 praticamente não produziram: "
             "132 de 54.539.")
    so_apontadas = st.checkbox(
        "Só ordens com apontamento", value=True,
        help="Sem apontamento não há conclusão real, e a ordem não entra no "
             "cálculo de prazo de nenhum jeito.")

onde = [
    "data_conclusao_real BETWEEN ? AND ?",
    filtro_lista("id_empresa", sel_empresa, empresas),
    filtro_lista("tipo_ordem", sel_tipo, tipos),
]
if so_ativas:
    onde.append("cod_situacao = 1")
if so_apontadas:
    onde.append("tem_apontamento")
w = " AND ".join(onde)
par = (de, ate)

# ---------------------------------------------------------------- KPIs
kpi = consulta(f"""
    SELECT count(*) AS ordens,
           100.0 * count(*) FILTER (WHERE no_prazo)
                 / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS pct_real,
           100.0 * count(*) FILTER (WHERE atraso_dias_por_data_fim <= 0)
                 / nullif(count(*) FILTER (WHERE atraso_dias_por_data_fim IS NOT NULL), 0)
                                                                     AS pct_antigo,
           median(atraso_dias) AS mediana,
           100.0 * count(*) FILTER (WHERE tem_apontamento) / count(*) AS pct_apontada
    FROM marts.fct_ordem_producao WHERE {w}
""", par).iloc[0]

a, b, c, d = st.columns(4)
a.metric("Ordens no prazo", pct(kpi.pct_real),
         help="data_conclusao_real <= data_prevista_fim. A conclusão real é o "
              "último apontamento de produção da ordem.")
b.metric("Mediana do atraso",
         f"{kpi.mediana:+.0f} dias" if kpi.mediana is not None else "—",
         delta_color="off")
c.metric("Ordens concluídas", numero(kpi.ordens),
         f"{pct(kpi.pct_apontada)} com apontamento" if kpi.pct_apontada else None)
d.metric("Pelo cálculo antigo", pct(kpi.pct_antigo),
         delta_color="off",
         help="Usando data_fim, que é anterior ao último apontamento em 98,7% "
              "das ordens. Está aqui só para comparação — não é indicador.")

if kpi.pct_real and kpi.pct_antigo:
    st.info(
        f"O mesmo conjunto de ordens dá **{pct(kpi.pct_real)}** de aderência "
        f"medindo pelo apontamento e **{pct(kpi.pct_antigo)}** medindo por "
        f"`data_fim` — **{kpi.pct_antigo - kpi.pct_real:.0f} pontos** de "
        "diferença. O segundo compara o plano com o próprio plano.", icon="📌")

st.divider()

# ---------------------------------------------------------------- gráficos
mensal = consulta(f"""
    SELECT date_trunc('month', data_conclusao_real) AS mes,
           100.0 * count(*) FILTER (WHERE no_prazo)
                 / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS real,
           100.0 * count(*) FILTER (WHERE atraso_dias_por_data_fim <= 0)
                 / nullif(count(*) FILTER (WHERE atraso_dias_por_data_fim IS NOT NULL), 0)
                                                                     AS antigo,
           count(*) AS ordens
    FROM marts.fct_ordem_producao WHERE {w} GROUP BY 1 ORDER BY 1
""", par)

e, f = st.columns([3, 2])
with e:
    fig = go.Figure()
    fig.add_scatter(x=mensal.mes, y=mensal.antigo, name="pelo data_fim (antigo)",
                    line=dict(color=tema.CINZA, dash="dot"))
    fig.add_scatter(x=mensal.mes, y=mensal.real, name="pelo apontamento (real)",
                    line=dict(color=tema.AZUL, width=3))
    fig.update_yaxes(title="% no prazo", range=[0, 100])
    st.plotly_chart(tema.aplicar(fig, "Aderência mensal — as duas medidas"),
                    width='stretch')

with f:
    dist = consulta(f"""
        SELECT atraso_dias FROM marts.fct_ordem_producao
        WHERE {w} AND atraso_dias BETWEEN -120 AND 120
    """, par)
    fig = px.histogram(dist, x="atraso_dias", nbins=60)
    fig.update_traces(marker_color=tema.AZUL_CLARO)
    fig.add_vline(x=0, line_color=tema.VERMELHO, line_width=2)
    fig.update_xaxes(title="dias de atraso (negativo = adiantado)")
    fig.update_yaxes(title="ordens")
    st.plotly_chart(tema.aplicar(fig, "Distribuição do atraso (±120 dias)"),
                    width='stretch')

g, h = st.columns(2)
with g:
    linha = consulta(f"""
        SELECT CAST(cod_linha_producao AS VARCHAR) AS linha, count(*) AS ordens,
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS pct
        FROM marts.fct_ordem_producao WHERE {w} AND cod_linha_producao IS NOT NULL
        GROUP BY 1 HAVING count(*) >= 50 ORDER BY ordens DESC LIMIT 15
    """, par)
    fig = px.bar(linha.sort_values("pct"), x="pct", y="linha", orientation="h",
                 hover_data=["ordens"])
    fig.update_traces(marker_color=tema.AZUL)
    fig.update_yaxes(title=None, type="category")
    fig.update_xaxes(title="% no prazo", range=[0, 100])
    st.plotly_chart(
        tema.aplicar(fig, "Por linha de produção (15 maiores, mín. 50 ordens)"),
        width='stretch')

with h:
    disp = consulta(f"""
        SELECT quantidade_prevista, atraso_dias, qtd_operacoes
        FROM marts.fct_ordem_producao
        WHERE {w} AND atraso_dias BETWEEN -200 AND 200
          AND quantidade_prevista BETWEEN 1 AND 500
        USING SAMPLE 8000 ROWS
    """, par)
    fig = px.scatter(disp, x="quantidade_prevista", y="atraso_dias",
                     opacity=0.25, color_discrete_sequence=[tema.AZUL])
    fig.add_hline(y=0, line_color=tema.VERMELHO, line_width=2)
    fig.update_xaxes(title="quantidade prevista")
    fig.update_yaxes(title="dias de atraso")
    st.plotly_chart(
        tema.aplicar(fig, "Ordem maior atrasa mais? (amostra de 8 mil)"),
        width='stretch')

st.caption(
    "Ordens sem apontamento não têm conclusão real e ficam fora do cálculo de "
    "prazo. `quantidade_refugada` não aparece em lugar nenhum desta página: é "
    "maior que a produzida em 54.439 de 54.494 ordens e a semântica não foi "
    "confirmada com o ERP.")
