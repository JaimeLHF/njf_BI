"""Paleta e helpers de gráfico, para as três páginas parecerem a mesma coisa."""
import plotly.graph_objects as go
import plotly.io as pio

AZUL = "#2563eb"
AZUL_CLARO = "#93c5fd"
VERMELHO = "#dc2626"
VERMELHO_CLARO = "#fca5a5"
CINZA = "#94a3b8"
VERDE = "#16a34a"
AMBAR = "#d97706"

CATEGORICA = [AZUL, "#0891b2", VERDE, AMBAR, "#7c3aed", "#db2777",
              "#0d9488", "#ca8a04", "#4f46e5", CINZA]

_base = pio.templates["plotly_white"]
_base.layout.font.family = "system-ui, -apple-system, sans-serif"
_base.layout.colorway = CATEGORICA
_base.layout.margin = dict(l=8, r=8, t=48, b=8)
_base.layout.hoverlabel.font.size = 13
pio.templates["njf"] = _base
pio.templates.default = "njf"


def aplicar(fig: go.Figure, titulo: str = "", altura: int = 340) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=15)),
        height=altura,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#e2e8f0", zerolinecolor="#cbd5e1")
    return fig
