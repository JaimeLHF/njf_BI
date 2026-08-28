"""Gera dados_pub.duckdb: uma tabela por visual, já agregada.

Regras que este script garante, e que a checagem em 08_auditar_publicacao.py
verifica depois:
  - nenhuma tabela em grão de item, pedido, nota ou ordem
  - nenhum nome de cliente, CNPJ, CPF ou código de cliente
  - representante vira "Representante A", "B", ... por ordem de faturamento;
    o de-para fica em .local/, que está no .gitignore
  - nenhum código de item, família ou ordem
  - todo grupo com menos de MIN_GRUPO registros vira "Outros"

O recorte da publicação é o MESMO que as páginas abrem por padrão, para os
números publicados baterem com os locais.
"""
import csv
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
ORIGEM = ROOT / "dados.duckdb"
DESTINO = ROOT / "dados_pub.duckdb"
LOCAL = ROOT / ".local"

MIN_GRUPO = 5          # abaixo disso o grupo vira "Outros"
TOP_REPRESENTANTES = 10
ANOS_RECORTE = 2       # o mesmo default das páginas


def main():
    LOCAL.mkdir(exist_ok=True)
    if DESTINO.exists():
        DESTINO.unlink()

    con = duckdb.connect(str(DESTINO))
    con.execute(f"ATTACH '{ORIGEM}' AS fonte (READ_ONLY)")

    # ------------------------------------------------ recorte, igual ao do app
    fim_fat = con.execute(
        "SELECT max(data_emissao) FROM fonte.marts.fct_faturamento").fetchone()[0]
    ini_fat = fim_fat.replace(year=fim_fat.year - ANOS_RECORTE)
    fim_prod = con.execute(
        "SELECT max(data_conclusao_real) FROM fonte.marts.fct_ordem_producao"
    ).fetchone()[0]
    ini_prod = fim_prod.replace(year=fim_prod.year - ANOS_RECORTE)

    W_FAT = (f"data_emissao BETWEEN DATE '{ini_fat}' AND DATE '{fim_fat}' "
             "AND gera_financeiro AND NOT eh_devolucao_heuristica")
    W_PROD = (f"data_conclusao_real BETWEEN DATE '{ini_prod}' AND DATE '{fim_prod}' "
              "AND cod_situacao = 1 AND tem_apontamento")
    W_CART = ("situacao_pedido <> 'C' AND quantidade_em_aberto > 0 "
              "AND origem_converte_em_nf AND valor_pedido_plausivel")

    con.execute(f"""
        CREATE TABLE pub_recorte AS SELECT
            DATE '{ini_fat}'  AS faturamento_de,  DATE '{fim_fat}'  AS faturamento_ate,
            DATE '{ini_prod}' AS producao_de,     DATE '{fim_prod}' AS producao_ate,
            {ANOS_RECORTE}    AS anos,            {MIN_GRUPO} AS min_grupo
    """)

    # ------------------------------------------------ de-para de representante
    # O nome real nunca entra no arquivo publicado. O de-para fica em .local/.
    con.execute(f"""
        CREATE TEMP TABLE depara AS
        WITH r AS (
            SELECT coalesce(nome_representante, 'sem representante') AS nome,
                   sum(valor_liquido) AS receita,
                   count(DISTINCT id_nota_saida) AS notas
            FROM fonte.marts.fct_faturamento WHERE {W_FAT}
            GROUP BY 1 HAVING count(DISTINCT id_nota_saida) >= {MIN_GRUPO}
        )
        SELECT nome, receita, notas,
               'Representante ' || chr(64 + CAST(
                   row_number() OVER (ORDER BY receita DESC) AS INTEGER)) AS apelido,
               row_number() OVER (ORDER BY receita DESC) AS posicao
        FROM r QUALIFY posicao <= {TOP_REPRESENTANTES}
    """)
    with open(LOCAL / "depara_representantes.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["apelido", "nome_real", "posicao"])
        for ap, nome, pos in con.execute(
                "SELECT apelido, nome, posicao FROM depara ORDER BY posicao"
        ).fetchall():
            w.writerow([ap, nome, pos])

    # ============================================================ FATURAMENTO
    con.execute(f"""
        CREATE TABLE pub_fat_kpi AS
        SELECT sum(valor_liquido) AS receita,
               count(DISTINCT id_nota_saida) AS notas,
               count(DISTINCT id_cliente) AS clientes,
               sum(valor_bruto) AS bruto
        FROM fonte.marts.fct_faturamento WHERE {W_FAT}
    """)
    # período anterior, para a variação do KPI
    con.execute(f"""
        CREATE TABLE pub_fat_kpi_anterior AS
        SELECT sum(valor_liquido) AS receita
        FROM fonte.marts.fct_faturamento
        WHERE data_emissao >= DATE '{ini_fat}' - INTERVAL '{ANOS_RECORTE}' YEAR
          AND data_emissao < DATE '{ini_fat}'
          AND gera_financeiro AND NOT eh_devolucao_heuristica
    """)
    con.execute(f"""
        CREATE TABLE pub_fat_devolucao AS
        SELECT coalesce(sum(valor_liquido), 0) AS v,
               count(DISTINCT id_nota_saida) AS notas
        FROM fonte.marts.fct_faturamento
        WHERE data_emissao BETWEEN DATE '{ini_fat}' AND DATE '{fim_fat}'
          AND eh_devolucao_heuristica
    """)
    con.execute(f"""
        CREATE TABLE pub_fat_mensal AS
        SELECT year(data_emissao) AS ano, month(data_emissao) AS mes_num,
               sum(valor_liquido) / 1e6 AS receita
        FROM fonte.marts.fct_faturamento WHERE {W_FAT}
        GROUP BY 1, 2 ORDER BY 1, 2
    """)
    # Canal só sobrevive com nome próprio se tiver MIN_GRUPO notas E
    # MIN_GRUPO clientes distintos. Um canal com um cliente só é o nome desse
    # cliente com outro rótulo — foi o caso que a auditoria pegou.
    con.execute(f"""
        CREATE TEMP TABLE canais_publicaveis AS
        SELECT coalesce(canal_venda, 'sem canal') AS canal
        FROM fonte.marts.fct_faturamento WHERE {W_FAT}
        GROUP BY 1
        HAVING count(DISTINCT id_nota_saida) >= {MIN_GRUPO}
           AND count(DISTINCT id_cliente) >= {MIN_GRUPO}
    """)

    con.execute(f"""
        CREATE TABLE pub_fat_canal AS
        WITH base AS (
            SELECT CASE WHEN coalesce(canal_venda, 'sem canal')
                             IN (SELECT canal FROM canais_publicaveis)
                        THEN coalesce(canal_venda, 'sem canal')
                        ELSE 'Outros' END AS canal,
                   sum(valor_liquido) / 1e6 AS receita
            FROM fonte.marts.fct_faturamento WHERE {W_FAT} GROUP BY 1
        )
        SELECT canal, sum(receita) AS receita FROM base GROUP BY 1 ORDER BY 2 DESC
    """)
    con.execute(f"""
        CREATE TABLE pub_fat_canal_mes AS
        WITH grandes AS (
            SELECT canal FROM canais_publicaveis
            WHERE canal IN (
                SELECT coalesce(canal_venda, 'sem canal')
                FROM fonte.marts.fct_faturamento WHERE {W_FAT}
                GROUP BY 1 ORDER BY sum(valor_liquido) DESC LIMIT 5)
        ),
        base AS (
            SELECT date_trunc('month', data_emissao) AS mes,
                   CASE WHEN coalesce(canal_venda, 'sem canal')
                             IN (SELECT canal FROM grandes)
                        THEN coalesce(canal_venda, 'sem canal')
                        ELSE 'outros' END AS canal,
                   sum(valor_liquido) / 1e6 AS receita,
                   count(DISTINCT id_nota_saida) AS notas
            FROM fonte.marts.fct_faturamento WHERE {W_FAT} GROUP BY 1, 2
        )
        SELECT mes, CASE WHEN notas >= {MIN_GRUPO} THEN canal ELSE 'outros' END AS canal,
               sum(receita) AS receita
        FROM base GROUP BY 1, 2 ORDER BY 1
    """)
    con.execute("""
        CREATE TABLE pub_fat_representante AS
        SELECT apelido AS nome, receita / 1e6 AS receita, notas,
               receita / notas AS ticket, posicao
        FROM depara ORDER BY posicao
    """)

    # ============================================================== PRODUÇÃO
    con.execute(f"""
        CREATE TABLE pub_prod_kpi AS
        SELECT count(*) AS ordens,
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS pct_real,
               100.0 * count(*) FILTER (WHERE atraso_dias_por_data_fim <= 0)
                     / nullif(count(*) FILTER (WHERE atraso_dias_por_data_fim IS NOT NULL), 0)
                                                                     AS pct_antigo,
               median(atraso_dias) AS mediana,
               100.0 * count(*) FILTER (WHERE tem_apontamento) / count(*) AS pct_apontada
        FROM fonte.marts.fct_ordem_producao WHERE {W_PROD}
    """)
    con.execute(f"""
        CREATE TABLE pub_prod_mensal AS
        SELECT date_trunc('month', data_conclusao_real) AS mes,
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS real,
               100.0 * count(*) FILTER (WHERE atraso_dias_por_data_fim <= 0)
                     / nullif(count(*) FILTER (WHERE atraso_dias_por_data_fim IS NOT NULL), 0)
                                                                     AS antigo
        FROM fonte.marts.fct_ordem_producao WHERE {W_PROD}
        GROUP BY 1 HAVING count(*) >= {MIN_GRUPO} ORDER BY 1
    """)
    # histograma já binado: 60 bins entre -120 e 120, como no app
    con.execute(f"""
        CREATE TABLE pub_prod_atraso_bins AS
        SELECT CAST(floor(atraso_dias / 4) * 4 AS INTEGER) AS bin_inicio,
               count(*) AS ordens
        FROM fonte.marts.fct_ordem_producao
        WHERE {W_PROD} AND atraso_dias BETWEEN -120 AND 120
        GROUP BY 1 HAVING count(*) >= {MIN_GRUPO} ORDER BY 1
    """)
    con.execute(f"""
        CREATE TABLE pub_prod_tamanho AS
        SELECT CASE WHEN quantidade_prevista <= 1   THEN '1 unidade'
                    WHEN quantidade_prevista <= 5   THEN '2 a 5'
                    WHEN quantidade_prevista <= 20  THEN '6 a 20'
                    WHEN quantidade_prevista <= 100 THEN '21 a 100'
                    ELSE 'mais de 100' END AS faixa,
               min(quantidade_prevista) AS ord, count(*) AS ordens,
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS pct
        FROM fonte.marts.fct_ordem_producao
        WHERE {W_PROD} AND quantidade_prevista IS NOT NULL
        GROUP BY 1 HAVING count(*) >= {MIN_GRUPO} ORDER BY 2
    """)
    con.execute(f"""
        CREATE TABLE pub_prod_operacoes AS
        SELECT CASE WHEN qtd_operacoes <= 2  THEN '1 a 2'
                    WHEN qtd_operacoes <= 5  THEN '3 a 5'
                    WHEN qtd_operacoes <= 10 THEN '6 a 10'
                    ELSE '11 ou mais' END AS faixa,
               min(qtd_operacoes) AS ord, count(*) AS ordens,
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0) AS pct
        FROM fonte.marts.fct_ordem_producao
        WHERE {W_PROD} AND qtd_operacoes IS NOT NULL
        GROUP BY 1 HAVING count(*) >= {MIN_GRUPO} ORDER BY 2
    """)

    # ============================================================== CARTEIRA
    con.execute(f"""
        CREATE TABLE pub_cart_kpi AS
        SELECT sum(valor_em_aberto) AS carteira,
               count(DISTINCT id_pedido) AS pedidos,
               100.0 * sum(valor_em_aberto) FILTER (
                   WHERE data_entrega_prevista < current_date)
                     / nullif(sum(valor_em_aberto), 0) AS pct_vencida,
               100.0 * sum(valor_em_aberto) FILTER (
                   WHERE data_entrega_prevista < current_date - INTERVAL 1 YEAR)
                     / nullif(sum(valor_em_aberto), 0) AS pct_velha,
               (SELECT median(dias_ate_primeiro_faturamento)
                  FROM fonte.marts.fct_pedido WHERE tem_faturamento) AS dias
        FROM fonte.marts.fct_pedido WHERE {W_CART}
    """)
    con.execute(f"""
        CREATE TABLE pub_cart_aging AS
        SELECT CASE WHEN data_entrega_prevista IS NULL THEN 'sem data prevista'
                    WHEN data_entrega_prevista < current_date - INTERVAL 1 YEAR
                         THEN 'vencida ha mais de 1 ano'
                    WHEN data_entrega_prevista < current_date
                         THEN 'vencida ha menos de 1 ano'
                    ELSE 'a vencer' END AS faixa,
               sum(valor_em_aberto) / 1e6 AS valor,
               count(DISTINCT id_pedido) AS pedidos
        FROM fonte.marts.fct_pedido WHERE {W_CART}
        GROUP BY 1 HAVING count(DISTINCT id_pedido) >= {MIN_GRUPO}
    """)
    con.execute(f"""
        CREATE TABLE pub_cart_mensal AS
        SELECT date_trunc('month', data_entrega_prevista) AS mes,
               data_entrega_prevista < current_date AS vencida,
               sum(valor_em_aberto) / 1e6 AS valor,
               count(DISTINCT id_pedido) AS pedidos
        FROM fonte.marts.fct_pedido
        WHERE {W_CART} AND data_entrega_prevista IS NOT NULL
          AND data_entrega_prevista >= current_date - INTERVAL 3 YEAR
        GROUP BY 1, 2 HAVING count(DISTINCT id_pedido) >= {MIN_GRUPO} ORDER BY 1
    """)
    con.execute(f"""
        CREATE TABLE pub_cart_canal AS
        WITH publicaveis AS (
            SELECT coalesce(canal_venda, 'sem canal') AS canal
            FROM fonte.marts.fct_pedido WHERE {W_CART} GROUP BY 1
            HAVING count(DISTINCT id_pedido) >= {MIN_GRUPO}
               AND count(DISTINCT id_cliente) >= {MIN_GRUPO}
        ),
        base AS (
            SELECT CASE WHEN coalesce(canal_venda, 'sem canal')
                             IN (SELECT canal FROM publicaveis)
                        THEN coalesce(canal_venda, 'sem canal')
                        ELSE 'Outros' END AS canal,
                   sum(valor_em_aberto) / 1e6 AS valor
            FROM fonte.marts.fct_pedido WHERE {W_CART} GROUP BY 1
        )
        SELECT canal, sum(valor) AS valor FROM base GROUP BY 1 ORDER BY 2 DESC LIMIT 10
    """)
    con.execute(f"""
        CREATE TABLE pub_cart_funil AS
        SELECT status_faturamento, count(*) AS itens,
               sum(valor_item_liquido) / 1e6 AS valor
        FROM fonte.marts.fct_pedido
        WHERE situacao_pedido <> 'C' AND origem_converte_em_nf
          AND valor_pedido_plausivel
        GROUP BY 1 HAVING count(*) >= {MIN_GRUPO} ORDER BY 2 DESC
    """)
    con.execute(f"""
        CREATE TABLE pub_cart_removido AS
        SELECT (SELECT round(sum(valor_item_liquido) / 1e6, 0)
                  FROM fonte.marts.fct_pedido WHERE NOT origem_converte_em_nf) AS mi_origem,
               (SELECT count(*) FROM fonte.marts.fct_pedido
                 WHERE NOT valor_pedido_plausivel) AS itens_implausiveis
    """)
    con.execute(f"""
        CREATE TABLE pub_fat_removido AS
        SELECT count(DISTINCT id_nota_saida) FILTER (WHERE NOT gera_financeiro) AS sem_fin,
               count(DISTINCT id_nota_saida) FILTER (WHERE eh_devolucao_heuristica) AS devol
        FROM fonte.marts.fct_faturamento
        WHERE data_emissao BETWEEN DATE '{ini_fat}' AND DATE '{fim_fat}'
    """)
    # KPIs da Home
    con.execute(f"""
        CREATE TABLE pub_home_kpi AS
        SELECT
            (SELECT round(sum(valor_liquido) / 1e6, 1)
               FROM fonte.marts.fct_faturamento
              WHERE gera_financeiro AND NOT eh_devolucao_heuristica
                AND year(data_emissao) = year(current_date))          AS fat_ano,
            (SELECT round(100.0 * count(*) FILTER (WHERE no_prazo)
                          / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0), 1)
               FROM fonte.marts.fct_ordem_producao WHERE cod_situacao = 1) AS no_prazo,
            (SELECT round(sum(valor_em_aberto) / 1e6, 1)
               FROM fonte.marts.fct_pedido
              WHERE origem_converte_em_nf AND valor_pedido_plausivel
                AND situacao_pedido <> 'C')                           AS carteira
    """)

    con.execute("DETACH fonte")
    for tmp in ("depara", "canais_publicaveis"):
        con.execute(f"DROP TABLE IF EXISTS {tmp}")  # temp, mas explícito
    tabelas = [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'main' AND table_name LIKE 'pub_%' ORDER BY 1"
    ).fetchall()]
    print(f"{len(tabelas)} tabelas geradas:")
    for t in tabelas:
        n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        print(f"  {t:<28} {n:>7,} linhas")
    con.close()

    mb = DESTINO.stat().st_size / 1024**2
    print(f"\n{DESTINO.name}: {mb:.2f} MB (alvo: < 20 MB)")
    print(f"de-para de representantes: {LOCAL / 'depara_representantes.csv'} "
          "(fora do repo)")


if __name__ == "__main__":
    main()
