from datetime import date

import streamlit as st

from dados import brl, consulta, pct

st.set_page_config(page_title="BI — Vendas e Produção", page_icon="📊",
                   layout="wide")

st.title("BI — Vendas e Produção")
st.caption("Dados do DW `erp_bi`. Todos os números saem da camada `marts`, "
           "que já corrige os defeitos conhecidos da origem.")

ano = date.today().year

resumo = consulta("""
    SELECT
        (SELECT round(sum(valor_liquido) / 1e6, 1) FROM marts.fct_faturamento
          WHERE gera_financeiro AND NOT eh_devolucao_heuristica
            AND year(data_emissao) = year(current_date))            AS fat_ano,
        (SELECT round(100.0 * count(*) FILTER (WHERE no_prazo)
                      / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0), 1)
           FROM marts.fct_ordem_producao WHERE cod_situacao = 1)     AS no_prazo,
        (SELECT round(sum(valor_em_aberto) / 1e6, 1) FROM marts.fct_pedido
          WHERE origem_converte_em_nf AND valor_pedido_plausivel
            AND situacao_pedido <> 'C')                              AS carteira
""").iloc[0]

a, b, c = st.columns(3)
a.metric(f"Faturamento em {ano}", brl(resumo.fat_ano * 1e6),
         help="Só NF que gera financeiro, sem devolução. A página de "
              "Faturamento abre com os últimos 24 meses, por isso mostra um "
              "número maior.")
b.metric("Ordens no prazo — série completa", pct(resumo.no_prazo),
         help="Todas as ordens ativas desde 2020, medidas pela conclusão real "
              "do apontamento. A página de Produção abre com os últimos 24 "
              "meses e mostra um número um pouco diferente.")
c.metric("Carteira em aberto — hoje", brl(resumo.carteira * 1e6),
         help="Só origens que faturam e quantidade plausível. Não depende de "
              "período: é a posição atual.")

st.divider()

st.subheader("As três páginas")
st.page_link("pages/1_Faturamento.py", label="**Faturamento** — evolução, canal e representante", icon="💰")
st.page_link("pages/2_Producao.py", label="**Produção** — aderência a prazo medida pelo apontamento", icon="🏭")
st.page_link("pages/3_Carteira.py", label="**Carteira** — pedidos em aberto e idade da carteira", icon="📋")

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

st.caption(
    "Os três números acima usam recortes diferentes — ano corrente, série "
    "completa e posição de hoje. Cada página abre no seu próprio período, "
    "então os valores não batem com estes por construção. O período está no "
    "rótulo de cada indicador."
)

st.info("Cada página traz, no rodapé, o que os filtros padrão removeram. "
        "Desligar um filtro é legítimo — desligar sem saber o que ele fazia, não.",
        icon="ℹ️")
