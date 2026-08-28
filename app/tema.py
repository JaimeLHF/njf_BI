"""Paleta e template do Plotly. Os títulos agora vêm do card (componentes.py),
não da figura — por isso `aplicar` não desenha título nenhum.
"""
import plotly.graph_objects as go
import plotly.io as pio

# séries — mantidas do tema claro, todas legíveis sobre #181b20
AZUL = "#4c8dff"
AZUL_CLARO = "#93c5fd"
VERMELHO = "#f2584d"
VERMELHO_CLARO = "#fca5a5"
CINZA = "#8e9297"
VERDE = "#3fb950"
AMBAR = "#e0a336"

# superfícies, iguais às de estilo.py
CARD = "#181b20"
BORDA = "#2a2e39"
TEXTO = "#d8d9da"
TEXTO_FRACO = "#8e9297"
GRID = "#23262e"

CATEGORICA = [AZUL, "#3fb0c9", VERDE, AMBAR, "#a371f7", "#f778ba",
              "#2dd4bf", "#d4a72c", "#7c8cff", CINZA]

ALTURA_GRADE = 260   # gráficos em grade 2x2
ALTURA_LINHA = 300   # gráficos de largura cheia

_t = go.layout.Template()
_t.layout.font = dict(family="system-ui, -apple-system, sans-serif",
                      size=11, color=TEXTO)
_t.layout.paper_bgcolor = "rgba(0,0,0,0)"
_t.layout.plot_bgcolor = "rgba(0,0,0,0)"
_t.layout.colorway = CATEGORICA
_t.layout.hoverlabel = dict(bgcolor=CARD, bordercolor=BORDA,
                            font=dict(size=12, color=TEXTO))
_t.layout.xaxis = dict(showgrid=False, linecolor=BORDA, zeroline=False,
                       tickfont=dict(size=11, color=TEXTO_FRACO),
                       title=dict(font=dict(size=11, color=TEXTO_FRACO)))
_t.layout.yaxis = dict(showgrid=True, gridcolor=GRID, gridwidth=1,
                       linecolor="rgba(0,0,0,0)", zerolinecolor=BORDA,
                       tickfont=dict(size=11, color=TEXTO_FRACO),
                       title=dict(font=dict(size=11, color=TEXTO_FRACO)))
pio.templates["njf"] = _t
pio.templates.default = "njf"


def aplicar(fig: go.Figure, altura: int = ALTURA_GRADE,
            unificado: bool = False) -> go.Figure:
    """`unificado`: hover de série temporal, que mostra todas as séries do
    mesmo x de uma vez."""
    tem_legenda = len(fig.data) > 1 and any(
        getattr(t, "name", None) for t in fig.data)
    fig.update_layout(
        height=altura,
        showlegend=tem_legenda,
        legend=dict(orientation="h", yanchor="top", y=-0.22, x=0,
                    xanchor="left", font=dict(size=11, color=TEXTO_FRACO),
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=20, t=10, b=62 if tem_legenda else 40),
        hovermode="x unified" if unificado else "closest",
    )
    return fig
