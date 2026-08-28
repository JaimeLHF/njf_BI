import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import tema
from dados import brl, consulta, filtro_lista, numero, opcoes, pct

st.set_page_config(page_title="Carteira", page_icon="📋", layout="wide")
st.title("Carteira em aberto")
st.caption("Posição de **hoje**, não um período: itens de pedido ainda não "
           "faturados nem cancelados, qualquer que seja a data de emissão. "
           "É o mesmo número da Home.")

# ---------------------------------------------------------------- filtros
empresas = opcoes("fct_pedido", "id_empresa")
canais = opcoes("fct_pedido", "canal_venda")
anos = consulta("""
    SELECT DISTINCT year(data_entrega_prevista) AS a FROM marts.fct_pedido
    WHERE data_entrega_prevista IS NOT NULL ORDER BY 1
""").a.tolist()

with st.sidebar:
    st.header("Filtros")
    sel_ano = st.multiselect("Ano de entrega prevista", anos)
    sel_empresa = st.multiselect("Empresa", empresas)
    sel_canal = st.multiselect("Canal de venda", canais)

    st.divider()
    st.caption("**Filtros de integridade**")
    so_converte = st.checkbox(
        "Só origens que faturam", value=True,
        help="A origem SIM são R$ 2,6 bi que nunca geraram nota nem ordem de "
             "fabricação em cinco anos. Sem este filtro a carteira dá R$ 2,8 bi.")
    so_plausivel = st.checkbox(
        "Só quantidade plausível", value=True,
        help="Remove 155 itens com quantidade irreal — digitação duplicada e "
             "quantidade acima de 10x o p99 do próprio item.")

onde = ["situacao_pedido <> 'C'", "quantidade_em_aberto > 0",
        filtro_lista("id_empresa", sel_empresa, empresas),
        filtro_lista("canal_venda", sel_canal, canais)]
if sel_ano:
    onde.append("year(data_entrega_prevista) IN (" +
                ", ".join(str(int(a)) for a in sel_ano) + ")")
if so_converte:
    onde.append("origem_converte_em_nf")
if so_plausivel:
    onde.append("valor_pedido_plausivel")
w = " AND ".join(onde)

AGING = """
    CASE WHEN data_entrega_prevista IS NULL THEN 'sem data prevista'
         WHEN data_entrega_prevista < current_date - INTERVAL 1 YEAR
              THEN 'vencida ha mais de 1 ano'
         WHEN data_entrega_prevista < current_date
              THEN 'vencida ha menos de 1 ano'
         ELSE 'a vencer' END
"""

# ---------------------------------------------------------------- KPIs
kpi = consulta(f"""
    SELECT sum(valor_em_aberto) AS carteira,
           count(DISTINCT id_pedido) AS pedidos,
           100.0 * sum(valor_em_aberto) FILTER (
               WHERE data_entrega_prevista < current_date)
                 / nullif(sum(valor_em_aberto), 0) AS pct_vencida,
           100.0 * sum(valor_em_aberto) FILTER (
               WHERE data_entrega_prevista < current_date - INTERVAL 1 YEAR)
                 / nullif(sum(valor_em_aberto), 0) AS pct_velha,
           (SELECT median(dias_ate_primeiro_faturamento)
              FROM marts.fct_pedido WHERE tem_faturamento) AS dias
    FROM marts.fct_pedido WHERE {w}
""").iloc[0]

a, b, c, d = st.columns(4)
a.metric("Carteira em aberto", brl(kpi.carteira))
b.metric("Pedidos em aberto", numero(kpi.pedidos),
         f"média {brl(kpi.carteira / kpi.pedidos)}" if kpi.pedidos else None)
c.metric("Carteira vencida", pct(kpi.pct_vencida),
         f"{pct(kpi.pct_velha)} há mais de 1 ano" if kpi.pct_velha else None,
         delta_color="inverse",
         help="Entrega prevista já passou e o item continua sem faturamento e "
              "sem cancelamento.")
d.metric("Dias até 1º faturamento",
         f"{kpi.dias:.0f} dias" if kpi.dias is not None else "—",
         delta_color="off", help="Mediana histórica, do pedido à primeira nota.")

if kpi.pct_velha and kpi.pct_velha > 20:
    st.error(
        f"**{kpi.pct_velha:.0f}% da carteira venceu há mais de um ano.** São "
        "pedidos nunca faturados e nunca cancelados — abandono provável, não "
        "compromisso. Sem uma rotina de baixa de pedido não atendido, esse "
        "valor só cresce. É pergunta aberta para a empresa "
        "(`docs/qualidade.md`, seção 8).", icon="🚨")

st.divider()

# ------------------------------------------------- aging (segunda posição)
ordem_aging = ["vencida ha mais de 1 ano", "vencida ha menos de 1 ano",
               "a vencer", "sem data prevista"]
rotulo = {"vencida ha mais de 1 ano": "Vencida há +1 ano<br>(abandono provável)",
          "vencida ha menos de 1 ano": "Vencida há -1 ano<br>(atraso operacional)",
          "a vencer": "A vencer", "sem data prevista": "Sem data prevista"}
cor = {"vencida ha mais de 1 ano": tema.VERMELHO,
       "vencida ha menos de 1 ano": tema.AMBAR,
       "a vencer": tema.AZUL, "sem data prevista": tema.CINZA}

aging = consulta(f"""
    SELECT {AGING} AS faixa, sum(valor_em_aberto) / 1e6 AS valor,
           count(DISTINCT id_pedido) AS pedidos
    FROM marts.fct_pedido WHERE {w} GROUP BY 1
""")
aging["ord"] = aging.faixa.map({f: i for i, f in enumerate(ordem_aging)})
aging = aging.sort_values("ord")

e, f = st.columns([3, 2])
with e:
    fig = go.Figure()
    for _, r in aging.iterrows():
        fig.add_bar(x=[r.valor], y=[rotulo.get(r.faixa, r.faixa)],
                    orientation="h", marker_color=cor.get(r.faixa, tema.CINZA),
                    name=rotulo.get(r.faixa, r.faixa),
                    hovertemplate=f"R$ {r.valor:.1f} mi<br>{r.pedidos:,} pedidos"
                                  "<extra></extra>")
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title="R$ milhões")
    fig.update_yaxes(title=None, autorange="reversed")
    fig = tema.aplicar(fig, "Idade da carteira — vencido há +1 ano é outra natureza")
    fig.update_layout(showlegend=False, margin_b=8)
    st.plotly_chart(fig, width='stretch')

with f:
    st.markdown("#### Como ler")
    st.markdown("""
**Vencida há mais de 1 ano** é abandono provável: o pedido passou da entrega
prevista, nunca foi faturado e nunca foi cancelado. Tratar como compromisso
superestima a carteira.

**Vencida há menos de 1 ano** é atraso operacional — ainda pode virar nota, e
é aqui que dá para agir.

**A vencer** é a carteira no sentido estrito: compromisso com data futura.
""")

# ---------------------------------------------------------------- gráficos
g, h = st.columns(2)
with g:
    mensal = consulta(f"""
        SELECT date_trunc('month', data_entrega_prevista) AS mes,
               sum(valor_em_aberto) / 1e6 AS valor,
               data_entrega_prevista < current_date AS vencida
        FROM marts.fct_pedido
        WHERE {w} AND data_entrega_prevista IS NOT NULL
          AND data_entrega_prevista >= current_date - INTERVAL 3 YEAR
        GROUP BY 1, 3 ORDER BY 1
    """)
    mensal["situacao"] = mensal.vencida.map({True: "vencida", False: "a vencer"})
    fig = px.bar(mensal, x="mes", y="valor", color="situacao",
                 color_discrete_map={"vencida": tema.VERMELHO_CLARO,
                                     "a vencer": tema.AZUL})
    fig.update_yaxes(title="R$ milhões")
    fig.update_xaxes(title=None)
    st.plotly_chart(tema.aplicar(fig, "Carteira por mês de entrega prevista"),
                    width='stretch')

with h:
    canal = consulta(f"""
        SELECT coalesce(canal_venda, 'sem canal') AS canal,
               sum(valor_em_aberto) / 1e6 AS valor
        FROM marts.fct_pedido WHERE {w} GROUP BY 1 ORDER BY 2 DESC LIMIT 10
    """)
    fig = px.bar(canal, x="valor", y="canal", orientation="h")
    fig.update_traces(marker_color=tema.AZUL)
    fig.update_yaxes(title=None, autorange="reversed")
    fig.update_xaxes(title="R$ milhões")
    st.plotly_chart(tema.aplicar(fig, "Carteira por canal"),
                    width='stretch')

# ---------------------------------------------------------------- funil
onde_funil = [o for o in onde if o != "quantidade_em_aberto > 0"]
funil = consulta(f"""
    SELECT status_faturamento, count(*) AS itens,
           sum(valor_item_liquido) / 1e6 AS valor
    FROM marts.fct_pedido WHERE {' AND '.join(onde_funil)}
    GROUP BY 1 ORDER BY 2 DESC
""")
fig = px.bar(funil, x="status_faturamento", y="itens", text="itens",
             hover_data=["valor"])
fig.update_traces(marker_color=tema.AZUL, texttemplate="%{text:,}")
fig.update_xaxes(title=None)
fig.update_yaxes(title="itens de pedido")
st.plotly_chart(
    tema.aplicar(fig, "Conversão do pedido em faturamento (todos os itens, "
                      "não só os em aberto)", 300),
    width='stretch')

# ---------------------------------------------------------------- rodapé
partes = []
if so_converte:
    r = consulta("""
        SELECT round(sum(valor_item_liquido) / 1e6, 0) AS v
        FROM marts.fct_pedido WHERE NOT origem_converte_em_nf
    """).iloc[0].v
    partes.append(f"**R$ {r:,.0f} mi** de origens que nunca geram NF (`SIM`, "
                  "`EXP`, `ORC`)".replace(",", "."))
if so_plausivel:
    r = consulta("""
        SELECT count(*) AS n FROM marts.fct_pedido WHERE NOT valor_pedido_plausivel
    """).iloc[0].n
    partes.append(f"**{r} itens** com quantidade implausível")
st.caption("Os filtros padrão removeram " + " e ".join(partes) + "."
           if partes else
           "Nenhum filtro de integridade ativo — a carteira inclui origens que "
           "nunca faturam e itens com quantidade irreal.")
