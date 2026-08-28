"""Compara os KPIs do arquivo publicado com os do banco completo.

O arquivo publicado é agregado; se algum critério divergir do que as páginas
usam por padrão, os números da demonstração deixam de bater com os reais e
ninguém percebe. Este teste é o que impede isso.

Sai com código 1 em qualquer divergência.
"""
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
TOL = 0.01   # 1 centavo / 0,01 ponto percentual


def main():
    con = duckdb.connect()
    con.execute(f"ATTACH '{ROOT / 'dados.duckdb'}' AS dados (READ_ONLY)")
    con.execute(f"ATTACH '{ROOT / 'dados_pub.duckdb'}' AS pub (READ_ONLY)")

    r = con.execute("SELECT * FROM pub.pub_recorte").fetchone()
    fat_de, fat_ate, prod_de, prod_ate = r[0], r[1], r[2], r[3]

    W_FAT = (f"data_emissao BETWEEN DATE '{fat_de}' AND DATE '{fat_ate}' "
             "AND gera_financeiro AND NOT eh_devolucao_heuristica")
    W_PROD = (f"data_conclusao_real BETWEEN DATE '{prod_de}' AND DATE '{prod_ate}' "
              "AND cod_situacao = 1 AND tem_apontamento")
    W_CART = ("situacao_pedido <> 'C' AND quantidade_em_aberto > 0 "
              "AND origem_converte_em_nf AND valor_pedido_plausivel")

    casos = [
        ("faturamento: receita",
         f"SELECT sum(valor_liquido) FROM dados.marts.fct_faturamento WHERE {W_FAT}",
         "SELECT receita FROM pub.pub_fat_kpi"),
        ("faturamento: notas",
         f"SELECT count(DISTINCT id_nota_saida) FROM dados.marts.fct_faturamento WHERE {W_FAT}",
         "SELECT notas FROM pub.pub_fat_kpi"),
        ("faturamento: clientes",
         f"SELECT count(DISTINCT id_cliente) FROM dados.marts.fct_faturamento WHERE {W_FAT}",
         "SELECT clientes FROM pub.pub_fat_kpi"),
        ("faturamento: soma da série mensal",
         f"SELECT sum(valor_liquido) / 1e6 FROM dados.marts.fct_faturamento WHERE {W_FAT}",
         "SELECT sum(receita) FROM pub.pub_fat_mensal"),
        ("faturamento: soma por canal",
         f"SELECT sum(valor_liquido) / 1e6 FROM dados.marts.fct_faturamento WHERE {W_FAT}",
         "SELECT sum(receita) FROM pub.pub_fat_canal"),
        ("produção: ordens",
         f"SELECT count(*) FROM dados.marts.fct_ordem_producao WHERE {W_PROD}",
         "SELECT ordens FROM pub.pub_prod_kpi"),
        ("produção: % no prazo",
         f"""SELECT 100.0 * count(*) FILTER (WHERE no_prazo)
                  / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0)
             FROM dados.marts.fct_ordem_producao WHERE {W_PROD}""",
         "SELECT pct_real FROM pub.pub_prod_kpi"),
        ("produção: % pelo cálculo antigo",
         f"""SELECT 100.0 * count(*) FILTER (WHERE atraso_dias_por_data_fim <= 0)
                  / nullif(count(*) FILTER (WHERE atraso_dias_por_data_fim IS NOT NULL), 0)
             FROM dados.marts.fct_ordem_producao WHERE {W_PROD}""",
         "SELECT pct_antigo FROM pub.pub_prod_kpi"),
        ("produção: mediana do atraso",
         f"SELECT median(atraso_dias) FROM dados.marts.fct_ordem_producao WHERE {W_PROD}",
         "SELECT mediana FROM pub.pub_prod_kpi"),
        ("produção: ordens por faixa de tamanho",
         f"""SELECT count(*) FROM dados.marts.fct_ordem_producao
             WHERE {W_PROD} AND quantidade_prevista IS NOT NULL""",
         "SELECT sum(ordens) FROM pub.pub_prod_tamanho"),
        ("carteira: valor em aberto",
         f"SELECT sum(valor_em_aberto) FROM dados.marts.fct_pedido WHERE {W_CART}",
         "SELECT carteira FROM pub.pub_cart_kpi"),
        ("carteira: pedidos",
         f"SELECT count(DISTINCT id_pedido) FROM dados.marts.fct_pedido WHERE {W_CART}",
         "SELECT pedidos FROM pub.pub_cart_kpi"),
        ("carteira: % vencida",
         f"""SELECT 100.0 * sum(valor_em_aberto) FILTER (
                       WHERE data_entrega_prevista < current_date)
                  / nullif(sum(valor_em_aberto), 0)
             FROM dados.marts.fct_pedido WHERE {W_CART}""",
         "SELECT pct_vencida FROM pub.pub_cart_kpi"),
        ("carteira: soma do aging",
         f"SELECT sum(valor_em_aberto) / 1e6 FROM dados.marts.fct_pedido WHERE {W_CART}",
         "SELECT sum(valor) FROM pub.pub_cart_aging"),
        ("home: faturamento do ano",
         """SELECT round(sum(valor_liquido) / 1e6, 1) FROM dados.marts.fct_faturamento
             WHERE gera_financeiro AND NOT eh_devolucao_heuristica
               AND year(data_emissao) = year(current_date)""",
         "SELECT fat_ano FROM pub.pub_home_kpi"),
        ("home: % no prazo",
         """SELECT round(100.0 * count(*) FILTER (WHERE no_prazo)
                       / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0), 1)
             FROM dados.marts.fct_ordem_producao WHERE cod_situacao = 1""",
         "SELECT no_prazo FROM pub.pub_home_kpi"),
        ("home: carteira",
         """SELECT round(sum(valor_em_aberto) / 1e6, 1) FROM dados.marts.fct_pedido
             WHERE origem_converte_em_nf AND valor_pedido_plausivel
               AND situacao_pedido <> 'C'""",
         "SELECT carteira FROM pub.pub_home_kpi"),
    ]

    falhas = []
    print(f"{'indicador':<42}{'completo':>16}{'publicado':>16}  ok")
    print("-" * 78)
    for nome, sql_full, sql_pub in casos:
        a = con.execute(sql_full).fetchone()[0]
        b = con.execute(sql_pub).fetchone()[0]
        a = float(a) if a is not None else None
        b = float(b) if b is not None else None
        ok = (a is None and b is None) or (
            a is not None and b is not None and abs(a - b) <= TOL)
        if not ok:
            falhas.append((nome, a, b))
        print(f"{nome:<42}{a:>16,.2f}{b:>16,.2f}  {'sim' if ok else 'NAO'}")

    print("-" * 78)
    if falhas:
        print(f"\nREPROVADO — {len(falhas)} divergência(s):")
        for nome, a, b in falhas:
            print(f"  {nome}: completo={a} publicado={b} (dif {abs(a - b):,.4f})")
        sys.exit(1)
    print(f"\nAPROVADO — {len(casos)} indicadores conferem "
          f"(tolerância {TOL}).")


if __name__ == "__main__":
    main()
