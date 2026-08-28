"""Uma função por visual. Cada uma decide de onde vem o dado.

No modo local, monta o SQL sobre os marts com os filtros escolhidos.
No modo publicação, lê a tabela agregada correspondente e ignora os filtros —
o arquivo publicado é um recorte fixo, gerado por scripts/07_gerar_publicacao.py
com exatamente os mesmos critérios que as páginas usam por padrão.

É por isso que os números publicados batem com os locais: mesma definição,
calculada uma vez.
"""
from dados import PUBLICACAO, consulta


# ============================================================ FATURAMENTO
def fat_kpi(w, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_fat_kpi").iloc[0]
    return consulta(f"""
        SELECT sum(valor_liquido) AS receita,
               count(DISTINCT id_nota_saida) AS notas,
               count(DISTINCT id_cliente) AS clientes, sum(valor_bruto) AS bruto
        FROM marts.fct_faturamento WHERE {w}
    """, par).iloc[0]


def fat_kpi_anterior(onde, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_fat_kpi_anterior").iloc[0]
    return consulta(f"""
        SELECT sum(valor_liquido) AS receita FROM marts.fct_faturamento
        WHERE data_emissao >= ? AND data_emissao < ? AND {onde}
    """, par).iloc[0]


def fat_devolucao(onde_dim, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_fat_devolucao").iloc[0]
    return consulta(f"""
        SELECT coalesce(sum(valor_liquido), 0) AS v,
               count(DISTINCT id_nota_saida) AS notas
        FROM marts.fct_faturamento
        WHERE data_emissao BETWEEN ? AND ? AND eh_devolucao_heuristica
          AND {onde_dim}
    """, par).iloc[0]


def fat_mensal(w, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_fat_mensal ORDER BY ano, mes_num")
    return consulta(f"""
        SELECT year(data_emissao) AS ano, month(data_emissao) AS mes_num,
               sum(valor_liquido) / 1e6 AS receita
        FROM marts.fct_faturamento WHERE {w} GROUP BY 1, 2 ORDER BY 1, 2
    """, par)


def fat_canal(w, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_fat_canal ORDER BY receita DESC")
    return consulta(f"""
        SELECT coalesce(canal_venda, 'sem canal') AS canal,
               sum(valor_liquido) / 1e6 AS receita
        FROM marts.fct_faturamento WHERE {w} GROUP BY 1 ORDER BY 2 DESC
    """, par)


def fat_canal_mes(w, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_fat_canal_mes ORDER BY mes")
    df = consulta(f"""
        SELECT date_trunc('month', data_emissao) AS mes,
               coalesce(canal_venda, 'sem canal') AS canal,
               sum(valor_liquido) / 1e6 AS receita
        FROM marts.fct_faturamento WHERE {w} GROUP BY 1, 2 ORDER BY 1
    """, par)
    top = df.groupby("canal").receita.sum().nlargest(5).index
    df["canal"] = df.canal.where(df.canal.isin(top), "outros")
    return df.groupby(["mes", "canal"], as_index=False).receita.sum()


def fat_representante(w, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_fat_representante ORDER BY posicao")
    df = consulta(f"""
        SELECT coalesce(nome_representante, 'sem representante') AS nome,
               sum(valor_liquido) / 1e6 AS receita,
               count(DISTINCT id_nota_saida) AS notas
        FROM marts.fct_faturamento WHERE {w} GROUP BY 1 ORDER BY 2 DESC LIMIT 10
    """, par)
    df["ticket"] = df.receita * 1e6 / df.notas
    return df


def fat_removido(onde_dim, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_fat_removido").iloc[0]
    return consulta(f"""
        SELECT count(DISTINCT id_nota_saida) FILTER (WHERE NOT gera_financeiro)
                   AS sem_fin,
               count(DISTINCT id_nota_saida) FILTER (WHERE eh_devolucao_heuristica)
                   AS devol
        FROM marts.fct_faturamento
        WHERE data_emissao BETWEEN ? AND ? AND {onde_dim}
    """, par).iloc[0]


# ============================================================== PRODUÇÃO
def prod_kpi(w, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_prod_kpi").iloc[0]
    return consulta(f"""
        SELECT count(*) AS ordens,
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0)
                   AS pct_real,
               100.0 * count(*) FILTER (WHERE atraso_dias_por_data_fim <= 0)
                     / nullif(count(*) FILTER (WHERE atraso_dias_por_data_fim
                                               IS NOT NULL), 0) AS pct_antigo,
               median(atraso_dias) AS mediana,
               100.0 * count(*) FILTER (WHERE tem_apontamento) / count(*)
                   AS pct_apontada
        FROM marts.fct_ordem_producao WHERE {w}
    """, par).iloc[0]


def prod_mensal(w, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_prod_mensal ORDER BY mes")
    return consulta(f"""
        SELECT date_trunc('month', data_conclusao_real) AS mes,
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0)
                   AS real,
               100.0 * count(*) FILTER (WHERE atraso_dias_por_data_fim <= 0)
                     / nullif(count(*) FILTER (WHERE atraso_dias_por_data_fim
                                               IS NOT NULL), 0) AS antigo
        FROM marts.fct_ordem_producao WHERE {w} GROUP BY 1 ORDER BY 1
    """, par)


def prod_atraso(w, par):
    """No publicado o histograma já vem binado de 4 em 4 dias."""
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_prod_atraso_bins ORDER BY bin_inicio")
    return consulta(f"""
        SELECT atraso_dias FROM marts.fct_ordem_producao
        WHERE {w} AND atraso_dias BETWEEN -120 AND 120
    """, par)


def prod_tamanho(w, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_prod_tamanho ORDER BY ord")
    return consulta(f"""
        SELECT CASE WHEN quantidade_prevista <= 1   THEN '1 unidade'
                    WHEN quantidade_prevista <= 5   THEN '2 a 5'
                    WHEN quantidade_prevista <= 20  THEN '6 a 20'
                    WHEN quantidade_prevista <= 100 THEN '21 a 100'
                    ELSE 'mais de 100' END AS faixa,
               min(quantidade_prevista) AS ord, count(*) AS ordens,
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS pct
        FROM marts.fct_ordem_producao
        WHERE {w} AND quantidade_prevista IS NOT NULL GROUP BY 1 ORDER BY 2
    """, par)


def prod_operacoes(w, par):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_prod_operacoes ORDER BY ord")
    return consulta(f"""
        SELECT CASE WHEN qtd_operacoes <= 2  THEN '1 a 2'
                    WHEN qtd_operacoes <= 5  THEN '3 a 5'
                    WHEN qtd_operacoes <= 10 THEN '6 a 10'
                    ELSE '11 ou mais' END AS faixa,
               min(qtd_operacoes) AS ord, count(*) AS ordens,
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS pct
        FROM marts.fct_ordem_producao
        WHERE {w} AND qtd_operacoes IS NOT NULL GROUP BY 1 ORDER BY 2
    """, par)


# ============================================================== CARTEIRA
AGING = """
    CASE WHEN data_entrega_prevista IS NULL THEN 'sem data prevista'
         WHEN data_entrega_prevista < current_date - INTERVAL 1 YEAR
              THEN 'vencida ha mais de 1 ano'
         WHEN data_entrega_prevista < current_date
              THEN 'vencida ha menos de 1 ano'
         ELSE 'a vencer' END
"""


def cart_kpi(w):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_cart_kpi").iloc[0]
    return consulta(f"""
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


def cart_aging(w):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_cart_aging")
    return consulta(f"""
        SELECT {AGING} AS faixa, sum(valor_em_aberto) / 1e6 AS valor,
               count(DISTINCT id_pedido) AS pedidos
        FROM marts.fct_pedido WHERE {w} GROUP BY 1
    """)


def cart_mensal(w):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_cart_mensal ORDER BY mes")
    return consulta(f"""
        SELECT date_trunc('month', data_entrega_prevista) AS mes,
               data_entrega_prevista < current_date AS vencida,
               sum(valor_em_aberto) / 1e6 AS valor
        FROM marts.fct_pedido
        WHERE {w} AND data_entrega_prevista IS NOT NULL
          AND data_entrega_prevista >= current_date - INTERVAL 3 YEAR
        GROUP BY 1, 2 ORDER BY 1
    """)


def cart_canal(w):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_cart_canal ORDER BY valor DESC")
    return consulta(f"""
        SELECT coalesce(canal_venda, 'sem canal') AS canal,
               sum(valor_em_aberto) / 1e6 AS valor
        FROM marts.fct_pedido WHERE {w} GROUP BY 1 ORDER BY 2 DESC LIMIT 10
    """)


def cart_funil(onde_funil):
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_cart_funil ORDER BY itens DESC")
    return consulta(f"""
        SELECT status_faturamento, count(*) AS itens,
               sum(valor_item_liquido) / 1e6 AS valor
        FROM marts.fct_pedido WHERE {onde_funil} GROUP BY 1 ORDER BY 2 DESC
    """)


def cart_removido():
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_cart_removido").iloc[0]
    return consulta("""
        SELECT (SELECT round(sum(valor_item_liquido) / 1e6, 0)
                  FROM marts.fct_pedido WHERE NOT origem_converte_em_nf)
                   AS mi_origem,
               (SELECT count(*) FROM marts.fct_pedido
                 WHERE NOT valor_pedido_plausivel) AS itens_implausiveis
    """).iloc[0]


# ================================================================== HOME
def home_kpi():
    if PUBLICACAO:
        return consulta("SELECT * FROM pub_home_kpi").iloc[0]
    return consulta("""
        SELECT
            (SELECT round(sum(valor_liquido) / 1e6, 1) FROM marts.fct_faturamento
              WHERE gera_financeiro AND NOT eh_devolucao_heuristica
                AND year(data_emissao) = year(current_date))          AS fat_ano,
            (SELECT round(100.0 * count(*) FILTER (WHERE no_prazo)
                          / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0), 1)
               FROM marts.fct_ordem_producao WHERE cod_situacao = 1)   AS no_prazo,
            (SELECT round(sum(valor_em_aberto) / 1e6, 1) FROM marts.fct_pedido
              WHERE origem_converte_em_nf AND valor_pedido_plausivel
                AND situacao_pedido <> 'C')                            AS carteira
    """).iloc[0]
