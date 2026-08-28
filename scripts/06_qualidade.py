"""Checks de qualidade sobre o schema raw do DuckDB -> docs/qualidade.md.
Toda checagem retorna contagem; nenhuma linha de dado e impressa.
"""
import json
from datetime import date
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DUCK = ROOT / "dados.duckdb"
REL = json.loads((DOCS / "relacionamentos.json").read_text(encoding="utf-8"))
CAT = json.loads((DOCS / "catalogo.json").read_text(encoding="utf-8"))["tabelas"]
HOJE = date.today()

# --- 1. nulos em campos criticos -------------------------------------------
# chaves de junção e as medidas/datas que sustentam as métricas do escopo.
CRITICOS = {
    "fat_pedido": ["id_pedido", "id_empresa", "id_estabelecimento",
                   "data_emissao", "data_entrega_prevista", "valor_liquido",
                   "situacao_pedido", "id_representante"],
    "fat_pedido_item": ["id_pedido", "id_pedido_item", "id_item_empresa",
                        "quantidade", "valor_unitario_liquido",
                        "quantidade_saldo"],
    "fat_nota_saida": ["id_nota_saida", "id_cliente", "id_empresa",
                       "data_emissao", "data_saida", "id_representante"],
    "fat_nota_saida_item": ["id_nota_saida", "id_item_empresa", "id_item",
                            "quantidade", "valor_liquido", "id_tipo_nf_saida"],
    "fat_ordem_fabricacao": ["id_ordem_fabricacao", "num_ordem", "id_empresa",
                             "id_item_ordem", "data_abertura",
                             "data_prevista_fim", "data_inicio", "data_fim",
                             "data_entrega", "quantidade_prevista",
                             "quantidade_produzida", "cod_situacao"],
    "fat_ordem_roteiro": ["id_ordem_roteiro", "id_ordem_fabricacao",
                          "id_operacao", "id_centro_trabalho",
                          "tempo_previsto", "tempo_realizado"],
    "fat_ordem_movimento": ["id_ordem_movimento", "id_ordem_roteiro",
                            "data_apontamento", "quantidade", "tempo_apontado"],
    "fat_pontuacao_producao": ["id_empresa", "id_item", "data_referencia",
                               "pontuacao", "quantidade"],
    "dim_cliente": ["id_cliente", "nome_cliente", "canal_venda", "tipo_cliente"],
    "dim_item_empresa": ["id_item_empresa", "cod_item", "descricao_item",
                         "cod_familia"],
}

# --- 3. datas incoerentes ---------------------------------------------------
DATAS = [
    ("fat_ordem_fabricacao", "fim antes do inicio",
     "data_fim < data_inicio"),
    ("fat_ordem_fabricacao", "inicio antes da abertura",
     "data_inicio < data_abertura"),
    ("fat_ordem_fabricacao", "previsao de fim antes da abertura",
     "data_prevista_fim < data_abertura"),
    ("fat_ordem_fabricacao", "entrega antes do fim de producao",
     "data_entrega < data_fim"),
    ("fat_ordem_fabricacao", "encerrada sem data_fim",
     "flag_encerrada = 1 AND data_fim IS NULL"),
    ("fat_ordem_fabricacao", "data_fim no futuro",
     f"data_fim > DATE '{HOJE}'"),
    ("fat_nota_saida", "saida antes da emissao",
     "data_saida < data_emissao"),
    ("fat_nota_saida", "emissao no futuro (fato historico)",
     f"data_emissao > DATE '{HOJE}'"),
    ("fat_pedido", "entrega prevista antes da emissao",
     "data_entrega_prevista < data_emissao"),
    ("fat_pedido", "emissao antes da inclusao",
     "data_emissao < data_inclusao"),
    ("fat_ordem_movimento", "apontamento no futuro",
     f"data_apontamento > DATE '{HOJE}'"),
    ("fat_pontuacao_producao", "referencia no futuro",
     f"data_referencia > DATE '{HOJE}'"),
]
# datas fora de faixa plausivel, por coluna
FAIXA = [
    ("fat_pedido", "data_emissao"), ("fat_nota_saida", "data_emissao"),
    ("fat_ordem_fabricacao", "data_abertura"),
    ("fat_ordem_fabricacao", "data_prevista_fim"),
    ("fat_ordem_movimento", "data_apontamento"),
]

# --- 4. duplicatas ----------------------------------------------------------
# PKs declaradas + chave natural presumida das tabelas sem PK
CHAVES = [
    ("fat_pedido", ["id_pedido"]),
    ("fat_pedido_item", ["id_pedido_item"]),
    ("fat_nota_saida", ["id_nota_saida"]),
    ("fat_nota_saida_item", ["id_nota_saida_item"]),
    ("fat_ordem_fabricacao", ["id_ordem_fabricacao"]),
    ("fat_ordem_fabricacao", ["num_ordem", "id_empresa"]),
    ("fat_ordem_roteiro", ["id_ordem_roteiro"]),
    ("fat_ordem_roteiro", ["id_ordem_fabricacao", "num_operacao"]),
    ("fat_ordem_movimento", ["id_ordem_movimento"]),
    ("fat_nota_saida_item_pontuacao",
     ["id_nota_saida_item", "id_ordem_fabricacao"]),
    ("ponte_pedido_configuracao_ordem",
     ["id_pedido", "id_configuracao", "id_ordem_fabricacao"]),
    ("ponte_nota_item_pedido_item", ["id_pedido_item", "id_nota_saida_item"]),
    ("fat_pontuacao_producao", ["id_pontuacao"]),
    ("fat_contrato_loja", ["id_contrato"]),
    ("dim_item_empresa", ["cod_item", "id_empresa"]),
    ("dim_cliente", ["cod_cliente"]),
]

# --- 5. negativos onde nao deveria haver ------------------------------------
NEGATIVOS = [
    ("fat_pedido", ["valor_bruto", "valor_liquido", "valor_desconto"]),
    ("fat_pedido_item", ["quantidade", "valor_unitario",
                         "valor_unitario_liquido", "quantidade_saldo",
                         "quantidade_cancelada", "percentual_desconto"]),
    ("fat_nota_saida_item", ["quantidade", "valor_bruto", "valor_liquido",
                             "valor_ipi", "valor_icms", "valor_desconto"]),
    ("fat_ordem_fabricacao", ["quantidade_prevista", "quantidade_produzida",
                              "quantidade_refugada", "quantidade_cancelada"]),
    ("fat_ordem_roteiro", ["tempo_previsto", "tempo_realizado", "tempo_setup"]),
    ("fat_ordem_movimento", ["tempo_apontado"]),
    ("fat_pontuacao_producao", ["quantidade", "pontuacao", "pontos"]),
]


def n(con, sql):
    return con.execute(sql).fetchone()[0]


def secao_nulos(con):
    linhas = ["| tabela | coluna | linhas | nulos | % |",
              "|--------|--------|-------:|------:|--:|"]
    achados = []
    for t, cols in CRITICOS.items():
        tot = n(con, f"SELECT count(*) FROM raw.{t}")
        for c in cols:
            nl = n(con, f"SELECT count(*) FROM raw.{t} WHERE {c} IS NULL")
            if nl == 0:
                continue
            pct = 100 * nl / tot
            linhas.append(f"| `{t}` | `{c}` | {tot:,} | {nl:,} | {pct:.1f}% |")
            achados.append((pct, t, c, nl, tot))
    if len(linhas) == 2:
        linhas = ["Nenhum campo critico com nulo."]
    return linhas, achados


def secao_orfaos():
    linhas = ["| de | coluna | para | total | orfaos | % |",
              "|----|--------|------|------:|-------:|--:|"]
    achados = []
    for r in REL["relacionamentos"]:
        v = r.get("validacao")
        if not v or not v["orfaos"]:
            continue
        linhas.append(
            f"| `{r['tabela']}` | `{r['coluna']}` | `{r['tabela_ref']}` | "
            f"{v['total']:,} | {v['orfaos']:,} | {v['pct_orfaos']}% |")
        achados.append((v["pct_orfaos"], r["tabela"], r["coluna"], v["orfaos"]))
    if len(linhas) == 2:
        linhas = ["Nenhum orfao nas 51 relacoes inferidas."]
    return linhas, achados


def secao_datas(con):
    linhas = ["| tabela | problema | linhas | % da tabela |",
              "|--------|----------|-------:|------------:|"]
    achados = []
    for t, nome, cond in DATAS:
        tot = n(con, f"SELECT count(*) FROM raw.{t}")
        q = n(con, f"SELECT count(*) FROM raw.{t} WHERE {cond}")
        if q == 0:
            continue
        pct = 100 * q / tot
        linhas.append(f"| `{t}` | {nome} | {q:,} | {pct:.2f}% |")
        achados.append((pct, t, nome, q))
    linhas += ["", "**Faixa observada das datas principais**", "",
               "| tabela | coluna | min | max | fora de 1990–2035 |",
               "|--------|--------|-----|-----|------------------:|"]
    for t, c in FAIXA:
        mn, mx, fora = con.execute(
            f"SELECT min({c}), max({c}), "
            f"count(*) FILTER (WHERE {c} < DATE '1990-01-01' "
            f"OR {c} > DATE '2035-12-31') FROM raw.{t}").fetchone()
        linhas.append(f"| `{t}` | `{c}` | {mn} | {mx} | {fora:,} |")
    return linhas, achados


def secao_duplicatas(con):
    linhas = ["| tabela | chave | linhas | chaves distintas | duplicadas |",
              "|--------|-------|-------:|-----------------:|-----------:|"]
    achados = []
    for t, cols in CHAVES:
        k = ", ".join(cols)
        tot, dist = con.execute(
            f"SELECT count(*), count(DISTINCT ({k})) FROM raw.{t}").fetchone()
        dup = tot - dist
        marca = "" if dup == 0 else " ⚠"
        linhas.append(f"| `{t}` | `{k}`{marca} | {tot:,} | {dist:,} | {dup:,} |")
        if dup:
            achados.append((100 * dup / tot, t, k, dup))
    return linhas, achados


def secao_negativos(con):
    linhas = ["| tabela | coluna | linhas | negativos | % |",
              "|--------|--------|-------:|----------:|--:|"]
    achados = []
    for t, cols in NEGATIVOS:
        tot = n(con, f"SELECT count(*) FROM raw.{t}")
        for c in cols:
            neg = n(con, f"SELECT count(*) FROM raw.{t} WHERE {c} < 0")
            if neg == 0:
                continue
            pct = 100 * neg / tot
            linhas.append(f"| `{t}` | `{c}` | {tot:,} | {neg:,} | {pct:.2f}% |")
            achados.append((pct, t, c, neg))
    if len(linhas) == 2:
        linhas = ["Nenhum valor negativo nas colunas de quantidade, valor e tempo."]
    return linhas, achados


def secao_carga_duplicada(con):
    """Linha INTEIRA repetida: sintoma de carga executada mais de uma vez.
    Diferente de duplicata de chave — aqui nenhuma coluna distingue as copias."""
    tabelas = [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='raw' ORDER BY table_name").fetchall()]
    linhas = ["| tabela | linhas | linhas distintas | fator | tem PK? |",
              "|--------|-------:|-----------------:|------:|---------|"]
    achados = []
    for t in tabelas:
        tot = n(con, f"SELECT count(*) FROM raw.{t}")
        dist = n(con, f"SELECT count(*) FROM (SELECT DISTINCT * FROM raw.{t})")
        if tot == dist:
            continue
        pk = "sim" if (CAT.get(t) or {}).get("pk") else "**nao**"
        linhas.append(f"| `{t}` | {tot:,} | {dist:,} | **{tot / dist:.2f}x** | {pk} |")
        achados.append((tot / dist, t, tot - dist))
    if len(linhas) == 2:
        linhas = ["Nenhuma tabela com linha inteira repetida."]
    return linhas, achados


def secao_semantica(con):
    """Colunas cujo nome promete uma coisa e o dado mostra outra. Cada item traz
    a medicao que sustenta a afirmacao."""
    out = []

    # data_fim nao e a data real de termino: e anterior ao ultimo apontamento
    r = con.execute("""
        WITH ult AS (
            SELECT r.id_ordem_fabricacao, max(m.data_apontamento) AS ult_apont
            FROM raw.fat_ordem_roteiro r
            JOIN raw.fat_ordem_movimento m USING (id_ordem_roteiro)
            GROUP BY 1)
        SELECT count(*),
               count(*) FILTER (WHERE o.data_fim < u.ult_apont),
               median(datediff('day', u.ult_apont, o.data_fim))
        FROM raw.fat_ordem_fabricacao o JOIN ult u USING (id_ordem_fabricacao)
        WHERE o.flag_encerrada = 1
    """).fetchone()
    out += [
        "### `fat_ordem_fabricacao.data_fim` nao e a data real de termino",
        "",
        f"Em {r[0]:,} ordens encerradas com apontamento, **{r[1]:,} "
        f"({100 * r[1] / r[0]:.1f}%)** tem `data_fim` ANTERIOR ao ultimo "
        f"apontamento de producao. Mediana: {r[2]:.0f} dias.",
        "",
        "A data real de conclusao e "
        "`max(fat_ordem_movimento.data_apontamento)` por ordem, via "
        "`fat_ordem_roteiro`. Aderencia a prazo calculada com `data_fim` "
        "mede o plano contra o plano, nao o realizado.",
        "",
    ]

    # flag_encerrada nao separa carteira em aberto
    r = con.execute("""
        SELECT count(*),
               count(*) FILTER (WHERE quantidade_produzida > 0),
               count(*) FILTER (WHERE data_prevista_fim < current_date)
        FROM raw.fat_ordem_fabricacao WHERE flag_encerrada = 0
    """).fetchone()
    out += [
        "### `flag_encerrada = 0` nao significa \"ordem em aberto\"",
        "",
        f"{r[0]:,} ordens tem `flag_encerrada = 0`, mas **{r[1]:,} "
        f"({100 * r[1] / r[0]:.1f}%)** ja produziram quantidade e "
        f"**{r[2]:,} ({100 * r[2] / r[0]:.1f}%)** tem previsao de fim no "
        "passado. A flag parece marcar encerramento administrativo, nao "
        "status de producao. Use `cod_situacao` + apontamento para status real.",
        "",
    ]

    # quantidade_saldo nao e saldo em aberto
    r = con.execute("""
        WITH fat AS (
            SELECT DISTINCT id_pedido_item
            FROM (SELECT DISTINCT * FROM raw.ponte_nota_item_pedido_item)
            WHERE id_nota_saida_item IS NOT NULL)
        SELECT count(*),
               count(*) FILTER (WHERE f.id_pedido_item IS NOT NULL)
        FROM raw.fat_pedido_item i
        LEFT JOIN fat f ON f.id_pedido_item = i.id_pedido_item
        WHERE i.quantidade_saldo > 0
    """).fetchone()
    out += [
        "### `fat_pedido_item.quantidade_saldo` nao e saldo em aberto",
        "",
        f"De {r[0]:,} itens com `quantidade_saldo > 0`, **{r[1]:,} "
        f"({100 * r[1] / r[0]:.1f}%) ja foram faturados** "
        "(tem vinculo em `ponte_nota_item_pedido_item`). A coluna guarda a "
        "quantidade original do pedido e nao e baixada no faturamento. "
        "Carteira em aberto = quantidade do item menos o faturado pela ponte "
        "**deduplicada**.",
        "",
    ]

    # cod_situacao do pedido / da ordem
    r = con.execute("""
        SELECT cod_situacao, count(*), count(*) FILTER (WHERE quantidade_produzida > 0)
        FROM raw.fat_ordem_fabricacao GROUP BY 1 ORDER BY 2 DESC
    """).fetchall()
    out += ["### `fat_ordem_fabricacao.cod_situacao`", "",
            "| cod_situacao | ordens | com producao | leitura |",
            "|---|-------:|-------------:|---------|"]
    for cod, tot, prod in r:
        leitura = ("ativa" if prod / tot > 0.5
                   else "cancelada/nao executada (praticamente nenhuma produziu)")
        out.append(f"| {cod} | {tot:,} | {prod:,} | {leitura} |")
    out.append("")
    return out, []


def main():
    con = duckdb.connect(str(DUCK), read_only=True)
    out = [
        "# Qualidade dos dados — vendas e producao",
        "",
        f"Gerado por `scripts/06_qualidade.py` em {HOJE} sobre o schema `raw` "
        "do `dados.duckdb`. Nenhuma linha de dado aparece aqui: so contagens.",
        "",
    ]
    for titulo, (linhas, _) in [
        ("1. Nulos em campos criticos", secao_nulos(con)),
        ("2. Orfaos de chave estrangeira", secao_orfaos()),
        ("3. Datas incoerentes", secao_datas(con)),
        ("4. Duplicatas de chave", secao_duplicatas(con)),
        ("5. Valores negativos", secao_negativos(con)),
        ("6. Duplicacao de carga (linha inteira repetida)",
         secao_carga_duplicada(con)),
        ("7. Colunas que nao significam o que o nome sugere",
         secao_semantica(con)),
    ]:
        out += [f"## {titulo}", ""] + linhas + [""]

    (DOCS / "qualidade.md").write_text("\n".join(out), encoding="utf-8")
    print("-> docs/qualidade.md")


if __name__ == "__main__":
    main()
