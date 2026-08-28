import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import estilo
import tema
from componentes import card_grafico, card_kpi
from dados import consulta, filtro_lista, numero, opcoes, pct, periodo

st.set_page_config(page_title="Produção", page_icon="🏭", layout="wide")
estilo.aplicar()

st.title("Aderência a prazo de produção")
titulo_periodo = st.empty()

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

titulo_periodo.caption(
    f"Ordens concluídas entre **{de:%b/%Y} e {ate:%b/%Y}**. A Home mostra a "
    "série completa desde 2020, por isso o número lá é um pouco diferente.")

a, b, c, d = st.columns(4, gap="small")
with a:
    card_kpi("Ordens no prazo", pct(kpi.pct_real),
             "conclusão real ≤ data prevista de fim", cor=tema.AZUL)
with b:
    card_kpi("Mediana do atraso",
             f"{kpi.mediana:+.0f} dias" if kpi.mediana is not None else "—",
             "positivo = atrasou")
with c:
    card_kpi("Ordens concluídas", numero(kpi.ordens),
             f"{pct(kpi.pct_apontada)} com apontamento"
             if kpi.pct_apontada else None)
with d:
    card_kpi("Pelo cálculo antigo", pct(kpi.pct_antigo),
             "usando data_fim — não é indicador, está aqui para comparação",
             cor=tema.CINZA)

if kpi.pct_real and kpi.pct_antigo:
    st.info(
        f"O mesmo conjunto de ordens dá **{pct(kpi.pct_real)}** de aderência "
        f"medindo pelo apontamento e **{pct(kpi.pct_antigo)}** medindo por "
        f"`data_fim` — **{kpi.pct_antigo - kpi.pct_real:.0f} pontos** de "
        "diferença. O segundo compara o plano com o próprio plano.", icon="📌")

st.write("")

# ---------------------------------------------------------------- gráficos
mensal = consulta(f"""
    SELECT date_trunc('month', data_conclusao_real) AS mes,
           100.0 * count(*) FILTER (WHERE no_prazo)
                 / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS real,
           100.0 * count(*) FILTER (WHERE atraso_dias_por_data_fim <= 0)
                 / nullif(count(*) FILTER (WHERE atraso_dias_por_data_fim IS NOT NULL), 0)
                                                                     AS antigo
    FROM marts.fct_ordem_producao WHERE {w} GROUP BY 1 ORDER BY 1
""", par)

e, f = st.columns([3, 2], gap="small")
with e:
    fig = go.Figure()
    fig.add_scatter(x=mensal.mes, y=mensal.antigo, name="pelo data_fim (antigo)",
                    line=dict(color=tema.CINZA, dash="dot", width=1.5),
                    hovertemplate="%{y:.1f}%<extra>antigo</extra>")
    fig.add_scatter(x=mensal.mes, y=mensal.real, name="pelo apontamento (real)",
                    line=dict(color=tema.AZUL, width=2.5),
                    hovertemplate="%{y:.1f}%<extra>real</extra>")
    fig.update_yaxes(title="% no prazo", range=[0, 100])
    card_grafico("Aderência mensal — as duas medidas",
                 tema.aplicar(fig, tema.ALTURA_LINHA, unificado=True))

with f:
    dist = consulta(f"""
        SELECT atraso_dias FROM marts.fct_ordem_producao
        WHERE {w} AND atraso_dias BETWEEN -120 AND 120
    """, par)
    fig = px.histogram(dist, x="atraso_dias", nbins=60)
    fig.update_traces(marker_color=tema.AZUL_CLARO,
                      hovertemplate="%{x} dias<br>%{y:,} ordens<extra></extra>")
    fig.add_vline(x=0, line_color=tema.VERMELHO, line_width=2)
    fig.update_xaxes(title="dias de atraso (negativo = adiantado)")
    fig.update_yaxes(title="ordens")
    card_grafico("Distribuição do atraso (±120 dias)",
                 tema.aplicar(fig, tema.ALTURA_LINHA))

st.write("")

# Substituíram "Por linha de produção" (272 códigos sem descrição no DW: casa
# com apenas 4 dos 137 centros de trabalho) e a dispersão quantidade x atraso,
# cuja correlação linear de 0,049 respondia "não" a uma pergunta que, em
# faixas, tem resposta "sim".
g, h = st.columns(2, gap="small")
with g:
    tamanho = consulta(f"""
        SELECT CASE WHEN quantidade_prevista <= 1   THEN '1 unidade'
                    WHEN quantidade_prevista <= 5   THEN '2 a 5'
                    WHEN quantidade_prevista <= 20  THEN '6 a 20'
                    WHEN quantidade_prevista <= 100 THEN '21 a 100'
                    ELSE 'mais de 100' END AS faixa,
               min(quantidade_prevista) AS ord, count(*) AS ordens,
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS pct
        FROM marts.fct_ordem_producao WHERE {w} AND quantidade_prevista IS NOT NULL
        GROUP BY 1 ORDER BY 2
    """, par)
    fig = px.bar(tamanho, x="faixa", y="pct", custom_data=["ordens"])
    fig.update_traces(
        marker_color=tema.AZUL,
        hovertemplate="%{x}<br>%{y:.1f}% no prazo<br>%{customdata[0]:,} ordens"
                      "<extra></extra>")
    fig.update_xaxes(title="quantidade prevista na ordem")
    fig.update_yaxes(title="% no prazo", range=[0, 100])
    card_grafico(
        "Ordem acima de 5 unidades atrasa mais — e satura aí",
        tema.aplicar(fig),
        "A queda é de **40% para 22%** entre ordens de até 5 unidades e de 6 a "
        "20. Acima disso não piora: o problema não é o tamanho, é passar do "
        "lote pequeno.")

with h:
    operacoes = consulta(f"""
        SELECT CASE WHEN qtd_operacoes <= 2  THEN '1 a 2'
                    WHEN qtd_operacoes <= 5  THEN '3 a 5'
                    WHEN qtd_operacoes <= 10 THEN '6 a 10'
                    ELSE '11 ou mais' END AS faixa,
               min(qtd_operacoes) AS ord, count(*) AS ordens,
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS pct
        FROM marts.fct_ordem_producao WHERE {w} AND qtd_operacoes IS NOT NULL
        GROUP BY 1 ORDER BY 2
    """, par)
    fig = px.bar(operacoes, x="faixa", y="pct", custom_data=["ordens"])
    fig.update_traces(
        marker_color=tema.AMBAR,
        hovertemplate="%{x}<br>%{y:.1f}% no prazo<br>%{customdata[0]:,} ordens"
                      "<extra></extra>")
    fig.update_xaxes(title="operações no roteiro")
    fig.update_yaxes(title="% no prazo", range=[0, 100])
    card_grafico(
        "Roteiro longo atrasa muito mais que ordem grande",
        tema.aplicar(fig),
        "De **56% para 21%** entre roteiros de 1-2 e de 6-10 operações. A "
        "complexidade do roteiro explica o atraso melhor que a quantidade — é "
        "por aqui que vale procurar o gargalo.")

st.caption(
    "Ordens sem apontamento não têm conclusão real e ficam fora do cálculo de "
    "prazo. `quantidade_refugada` não aparece em lugar nenhum desta página: é "
    "maior que a produzida em 54.439 de 54.494 ordens e a semântica não foi "
    "confirmada com o ERP. Também não há corte por linha de produção: os 272 "
    "códigos não têm descrição no DW.")
