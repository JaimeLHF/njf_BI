from datetime import date

import streamlit as st

import estilo
from componentes import card_kpi
import consultas
from dados import PUBLICACAO, brl, pct, rodape_publicacao

st.set_page_config(page_title="BI — Vendas e Produção", page_icon="📊",
                   layout="wide")
estilo.aplicar()

st.title("BI — Vendas e Produção")
st.caption("Dados do DW `erp_bi`. Todos os números saem da camada `marts`, "
           "que já corrige os defeitos conhecidos da origem.")

ano = date.today().year

resumo = consultas.home_kpi()

a, b, c = st.columns(3, gap="small")
with a:
    card_kpi(f"Faturamento em {ano}", brl(resumo.fat_ano * 1e6),
             "só NF que gera financeiro, sem devolução")
with b:
    card_kpi("Ordens no prazo — série completa", pct(resumo.no_prazo),
             "desde 2020, pela conclusão real do apontamento")
with c:
    card_kpi("Carteira em aberto — hoje", brl(resumo.carteira * 1e6),
             "origens que faturam, quantidade plausível")

st.caption(
    "Os três números acima usam recortes diferentes — ano corrente, série "
    "completa e posição de hoje. Cada página abre no seu próprio período, "
    "então os valores não batem com estes por construção. O período está "
    "sempre no rótulo.")

st.divider()

st.subheader("As três páginas")
st.page_link("pages/1_Faturamento.py",
             label="**Faturamento** — evolução, canal e representante", icon="💰")
st.page_link("pages/2_Producao.py",
             label="**Produção** — aderência a prazo medida pelo apontamento",
             icon="🏭")
st.page_link("pages/3_Carteira.py",
             label="**Carteira** — pedidos em aberto e idade da carteira",
             icon="📋")

st.divider()

st.subheader("Antes de usar estes números")
st.markdown("""
Três correções separam estes painéis do que sai de uma consulta direta ao banco.
Todas estão medidas em `docs/qualidade.md`.

**A origem entrega 9 tabelas triplicadas.** O ETL do DW rodou três vezes sem
truncate, e são exatamente as tabelas sem chave primária. A camada `staging`
deduplica; qualquer relatório que leia a origem direto conta cada linha três
vezes.

**Prazo de produção não se mede por `data_fim`.** Essa coluna é anterior ao
último apontamento em 98,7% das ordens — é plano, não realizado. A aderência
aqui usa a conclusão real derivada do apontamento, e o número cai de 73,7%
para 32,9%.

**Carteira não se mede por `quantidade_saldo`, nem sem separar a origem do
pedido.** A coluna de saldo não é baixada no faturamento, e a origem `SIM` são
R$ 2,6 bilhões que nunca geraram nota nem ordem de fabricação. Com os dois
cuidados, a carteira é R$ 189 milhões em vez de R$ 2,8 bilhões.
""")

if PUBLICACAO:
    st.info(
        "**Versão de demonstração.** Os dados são agregados e anonimizados: "
        "não há nome de cliente, representante, produto ou qualquer chave que "
        "identifique uma entidade. Os filtros ficam desativados porque o "
        "arquivo publicado é um recorte fixo — os últimos dois anos, com os "
        "mesmos critérios que a versão local abre por padrão. Os números são "
        "os mesmos.", icon="🔒")
else:
    st.info("Cada página traz, no rodapé, o que os filtros padrão removeram. "
            "Desligar um filtro é legítimo — desligar sem saber o que ele "
            "fazia, não.", icon="ℹ️")

rodape_publicacao()
