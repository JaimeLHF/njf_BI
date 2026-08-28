import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import consultas
import estilo
import tema
from componentes import card_grafico, card_kpi, card_texto
from dados import (PUBLICACAO, brl, consulta, filtro_lista, numero, opcoes,
                   pct, rodape_publicacao)

st.set_page_config(page_title="Carteira", page_icon="📋", layout="wide")
estilo.aplicar()

st.title("Carteira em aberto")
st.caption("Posição de **hoje**, não um período: itens de pedido ainda não "
           "faturados nem cancelados, qualquer que seja a data de emissão. "
           "É o mesmo número da Home.")

# ---------------------------------------------------------------- filtros
empresas = opcoes("fct_pedido", "id_empresa")
canais = opcoes("fct_pedido", "canal_venda")
anos = [] if PUBLICACAO else consulta("""
    SELECT DISTINCT year(data_entrega_prevista) AS a FROM marts.fct_pedido
    WHERE data_entrega_prevista IS NOT NULL ORDER BY 1
""").a.tolist()

with st.sidebar:
    st.header("Filtros")
    if PUBLICACAO:
        sel_ano, sel_empresa, sel_canal = [], [], []
        so_converte = so_plausivel = True
        st.info(
            "Recorte fixo: itens em aberto, só de origens que faturam e com "
            "quantidade plausível.\n\nA versão publicada usa um arquivo "
            "agregado, sem o grão do item de pedido — por isso não há filtros. "
            "Os critérios são os mesmos que a versão local abre por padrão.",
            icon="🔒")
    else:
        sel_ano = st.multiselect("Ano de entrega prevista", anos)
        sel_empresa = st.multiselect("Empresa", empresas)
        sel_canal = st.multiselect("Canal de venda", canais)

        st.divider()
        st.caption("**Filtros de integridade**")
        so_converte = st.checkbox(
            "Só origens que faturam", value=True,
            help="A origem SIM são R$ 2,6 bi que nunca geraram nota nem ordem "
                 "de fabricação em cinco anos. Sem este filtro a carteira dá "
                 "R$ 2,8 bi.")
        so_plausivel = st.checkbox(
            "Só quantidade plausível", value=True,
            help="Remove 155 itens com quantidade irreal — digitação duplicada "
                 "e quantidade acima de 10x o p99 do próprio item.")

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
kpi = consultas.cart_kpi(w)

a, b, c, d = st.columns(4, gap="small")
with a:
    card_kpi("Carteira em aberto", brl(kpi.carteira), "posição de hoje")
with b:
    card_kpi("Pedidos em aberto", numero(kpi.pedidos),
             f"média {brl(kpi.carteira / kpi.pedidos)}" if kpi.pedidos else None)
with c:
    card_kpi("Carteira vencida", pct(kpi.pct_vencida),
             f"{pct(kpi.pct_velha)} há mais de 1 ano" if kpi.pct_velha else None,
             cor=tema.VERMELHO)
with d:
    card_kpi("Dias até 1º faturamento",
             f"{kpi.dias:.0f} dias" if kpi.dias is not None else "—",
             "mediana histórica, do pedido à primeira nota")

if kpi.pct_velha and kpi.pct_velha > 20:
    st.error(
        f"**{kpi.pct_velha:.0f}% da carteira venceu há mais de um ano.** São "
        "pedidos nunca faturados e nunca cancelados — abandono provável, não "
        "compromisso. Sem uma rotina de baixa de pedido não atendido, esse "
        "valor só cresce. É pergunta aberta para a empresa "
        "(`docs/qualidade.md`, seção 8).", icon="🚨")

st.write("")

# ------------------------------------------------- aging (segunda posição)
ordem_aging = ["vencida ha mais de 1 ano", "vencida ha menos de 1 ano",
               "a vencer", "sem data prevista"]
rotulo = {"vencida ha mais de 1 ano": "Vencida há +1 ano",
          "vencida ha menos de 1 ano": "Vencida há -1 ano",
          "a vencer": "A vencer", "sem data prevista": "Sem data prevista"}
cor = {"vencida ha mais de 1 ano": tema.VERMELHO,
       "vencida ha menos de 1 ano": tema.AMBAR,
       "a vencer": tema.AZUL, "sem data prevista": tema.CINZA}

aging = consultas.cart_aging(w)
aging["ord"] = aging.faixa.map({f: i for i, f in enumerate(ordem_aging)})
aging = aging.sort_values("ord")

e, f = st.columns([3, 2], gap="small")
with e:
    fig = go.Figure()
    for _, r in aging.iterrows():
        fig.add_bar(x=[r.valor], y=[rotulo.get(r.faixa, r.faixa)],
                    orientation="h", marker_color=cor.get(r.faixa, tema.CINZA),
                    hovertemplate=f"R$ {r.valor:.1f} mi<br>{r.pedidos:,} pedidos"
                                  "<extra></extra>")
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title="R$ milhões")
    fig.update_yaxes(title=None, autorange="reversed")
    fig = tema.aplicar(fig, tema.ALTURA_LINHA)
    fig.update_layout(showlegend=False, margin_b=40)
    card_grafico("Idade da carteira", fig,
                 "Vencido há mais de um ano é outra natureza: abandono "
                 "provável, não atraso.")

with f:
    card_texto("Como ler", """
**Vencida há mais de 1 ano** é abandono provável: passou da entrega prevista,
nunca foi faturada e nunca foi cancelada. Tratar como compromisso superestima
a carteira.

**Vencida há menos de 1 ano** é atraso operacional — ainda pode virar nota, e
é aqui que dá para agir.

**A vencer** é a carteira no sentido estrito: compromisso com data futura.
""")

st.write("")

g, h = st.columns(2, gap="small")
with g:
    mensal = consultas.cart_mensal(w)
    mensal["situacao"] = mensal.vencida.map({True: "vencida", False: "a vencer"})
    fig = px.bar(mensal, x="mes", y="valor", color="situacao",
                 color_discrete_map={"vencida": tema.VERMELHO,
                                     "a vencer": tema.AZUL})
    fig.update_yaxes(title="R$ milhões")
    fig.update_xaxes(title=None)
    card_grafico("Carteira por mês de entrega prevista", tema.aplicar(fig))

with h:
    canal = consultas.cart_canal(w)
    fig = px.bar(canal, x="valor", y="canal", orientation="h")
    fig.update_traces(marker_color=tema.AZUL,
                      hovertemplate="%{y}<br>R$ %{x:.1f} mi<extra></extra>")
    fig.update_yaxes(title=None, autorange="reversed")
    fig.update_xaxes(title="R$ milhões")
    card_grafico("Carteira por canal", tema.aplicar(fig))

st.write("")

onde_funil = [o for o in onde if o != "quantidade_em_aberto > 0"]
funil = consultas.cart_funil(" AND ".join(onde_funil))
fig = px.bar(funil, x="status_faturamento", y="itens", text="itens",
             custom_data=["valor"])
fig.update_traces(marker_color=tema.AZUL, texttemplate="%{text:,}",
                  textposition="outside",
                  hovertemplate="%{x}<br>%{y:,} itens<br>R$ %{customdata[0]:.1f} mi"
                                "<extra></extra>")
fig.update_xaxes(title=None)
fig.update_yaxes(title="itens de pedido")
card_grafico("Conversão do pedido em faturamento", tema.aplicar(fig, 280),
             "Todos os itens do recorte, não só os em aberto.")

# ---------------------------------------------------------------- rodapé
removido = consultas.cart_removido()
partes = []
if so_converte:
    partes.append(f"**R$ {removido.mi_origem:,.0f} mi** de origens que nunca "
                  "geram NF (`SIM`, `EXP`, `ORC`)".replace(",", "."))
if so_plausivel:
    partes.append(f"**{removido.itens_implausiveis} itens** com quantidade "
                  "implausível")
st.caption("Os filtros padrão removeram " + " e ".join(partes) + "."
           if partes else
           "Nenhum filtro de integridade ativo — a carteira inclui origens que "
           "nunca faturam e itens com quantidade irreal.")

rodape_publicacao()
