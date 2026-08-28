"""Cards. Nenhuma página chama st.plotly_chart nem st.metric direto."""
import streamlit as st

from estilo import TEXTO


def card_kpi(label: str, valor: str, delta: str | None = None,
             ajuda: str | None = None, cor: str | None = None) -> None:
    """KPI dentro de um card. `cor` pinta só o valor — use para o indicador
    que precisa saltar (carteira vencida, por exemplo)."""
    with st.container(border=True):
        st.markdown(f'<p class="card-titulo">{label}</p>', unsafe_allow_html=True)
        st.markdown(
            f'<p class="kpi-valor" style="color:{cor or TEXTO}">{valor}</p>',
            unsafe_allow_html=True)
        if delta:
            st.markdown(f'<p class="kpi-delta">{delta}</p>',
                        unsafe_allow_html=True)
        if ajuda:
            with st.popover("?", width="content"):
                st.caption(ajuda)


def card_grafico(titulo: str, fig, rodape: str | None = None,
                 chave: str | None = None) -> None:
    """Gráfico dentro de um card. O título vem daqui, não do Plotly — por isso
    `tema.aplicar` não desenha mais título interno."""
    with st.container(border=True):
        st.markdown(f'<p class="card-titulo">{titulo}</p>',
                    unsafe_allow_html=True)
        st.plotly_chart(fig, width="stretch", key=chave,
                        config={"displayModeBar": False})
        if rodape:
            st.markdown(f'<p class="card-rodape">{rodape}</p>',
                        unsafe_allow_html=True)


def card_texto(titulo: str, markdown: str) -> None:
    """Card só com texto, para as notas de leitura ao lado dos gráficos."""
    with st.container(border=True):
        st.markdown(f'<p class="card-titulo">{titulo}</p>',
                    unsafe_allow_html=True)
        st.markdown(markdown)
