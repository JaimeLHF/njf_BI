"""CSS do app, em estilo Grafana: cards com borda sutil sobre fundo escuro.

Precisa ser chamado em TODA página, não só na Home: no Streamlit multipage
cada página é um script próprio e o CSS não atravessa de uma para outra.
"""
import streamlit as st

FUNDO = "#0f1116"
CARD = "#181b20"
BORDA = "#2a2e39"
TEXTO = "#d8d9da"
TEXTO_FRACO = "#8e9297"

CSS = f"""
<style>
/* menos respiro vertical: cabe mais painel na primeira dobra */
.block-container {{
    padding-top: 2.2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}}

/* o container com borda do Streamlit é a base do card */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {CARD};
    border: 1px solid {BORDA};
    border-radius: 5px;
    padding: 0.7rem 0.9rem;
}}

/* título do card: pequeno, caixa alta discreta, como Grafana */
.card-titulo {{
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: {TEXTO_FRACO};
    margin: 0 0 0.35rem 0;
    line-height: 1.3;
}}

.card-rodape {{
    font-size: 0.72rem;
    color: {TEXTO_FRACO};
    margin: 0.4rem 0 0 0;
    line-height: 1.45;
}}

/* KPI */
.kpi-valor {{
    font-size: 1.9rem;
    font-weight: 600;
    line-height: 1.15;
    margin: 0.1rem 0 0 0;
    font-variant-numeric: tabular-nums;
}}
.kpi-delta {{
    font-size: 0.76rem;
    color: {TEXTO_FRACO};
    margin: 0.2rem 0 0 0;
}}

/* o gráfico encosta na borda do card sem margem extra */
div[data-testid="stVerticalBlockBorderWrapper"] .stPlotlyChart {{
    margin-bottom: -0.4rem;
}}

/* sidebar um pouco mais discreta */
section[data-testid="stSidebar"] {{
    border-right: 1px solid {BORDA};
}}

/* separadores mais sutis */
hr {{ border-color: {BORDA}; }}
</style>
"""


def aplicar():
    st.markdown(CSS, unsafe_allow_html=True)
