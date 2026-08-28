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
    ("fat_ordem_fabricacao", "abertura no futuro",
     f"data_abertura > DATE '{HOJE}'"),
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


def secao_impacto(con):
    """O que a triplicacao faz com um relatorio que le raw direto, e o que a
    camada staging do dbt corrige."""
    tem_staging = n(con, "SELECT count(*) FROM information_schema.schemata "
                        "WHERE schema_name = 'staging'")
    out = [
        "> **Isto afeta relatorios que a empresa ja tenha em producao.** Qualquer "
        "consulta que leia essas 9 tabelas direto da origem — Power BI, Excel, "
        "extracao propria — esta contando cada linha tres vezes. Nao e um "
        "problema desta migracao: a duplicacao vem do Postgres, e a migracao e "
        "single-pass. Numeros ja publicados a partir dessas tabelas precisam ser "
        "reconferidos.",
        "",
        "O que infla, na pratica:",
        "",
        "- vinculo pedido ↔ NF (`ponte_nota_item_pedido_item`, "
        "`fat_nota_saida_item_pedido`) — conversao de pedido em faturamento e "
        "tempo entre venda e faturamento",
        "- vinculo pedido ↔ ordem (`ponte_pedido_configuracao_ordem`) — "
        "qualquer visao que compare vendido com produzido",
        "- pontuacao de producao (`fat_pontuacao_producao`, "
        "`fat_nota_saida_item_pontuacao`) — produtividade da fabrica",
        "- rateio de comissao (`fat_pedido_representante_secundario`)",
        "- contratos de loja (`fat_contrato_loja`, `fat_contrato_loja_parcela`)",
        "- servicos da LC 116 (`ponte_nota_saida_item_servico`) — base de ISS",
        "",
        "A correcao esta na camada `staging` do dbt (`models/staging/`), com "
        "dedup explicita por chave natural. O `raw` fica intacto de proposito: "
        "o defeito da origem precisa continuar visivel e versionado.",
        "",
    ]
    if not tem_staging:
        out += ["_Camada staging ainda nao construida: rode `dbt build`._", ""]
        return out, []

    linhas = [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'staging' ORDER BY table_name").fetchall()]
    out += ["**Efeito medido da correcao**", "",
            "| tabela | raw | staging | removidas | fator |",
            "|--------|----:|--------:|----------:|------:|"]
    for stg in linhas:
        base = stg.removeprefix("stg_")
        bruto = n(con, f"SELECT count(*) FROM raw.{base}")
        limpo = n(con, f"SELECT count(*) FROM staging.{stg}")
        if bruto == limpo:
            continue
        out.append(f"| `{base}` | {bruto:,} | {limpo:,} | {bruto - limpo:,} | "
                   f"{bruto / limpo:.3f}x |")
    out.append("")
    return out, []


def secao_perguntas():
    """O que precisa vir da empresa antes destes numeros virarem indicador."""
    return [
        "### Perguntas para a empresa",
        "",
        "Nenhuma destas se responde com o dado que temos. Levar para a reuniao.",
        "",
        "1. **Quais relatorios consomem essas 9 tabelas hoje?** Power BI, Excel, "
        "extracao propria — precisamos da lista para estimar o erro de cada "
        "numero ja publicado. Enquanto nao soubermos, todo indicador construido "
        "sobre elas esta sob suspeita de estar 3x inflado.",
        "",
        "2. **Qual o grao real de `fat_pontuacao_producao`?** `id_pontuacao` nao "
        "identifica a linha: sao 40.423 valores para 101.146 linhas distintas, e "
        "um unico id cobre 880 itens e 678 datas. Ele e um numero de lote, de "
        "apuracao mensal, de documento? Sem isso a dedup fica travada em linha "
        "inteira e o indicador de produtividade nao tem grao definido.",
        "",
        "3. **O que e `quantidade_refugada` quando e maior que a produzida?** "
        "Acontece em 54.439 das 54.494 ordens com valor preenchido. E refugo "
        "acumulado do roteiro inteiro, sucata em outra unidade de medida, ou "
        "outra grandeza? Enquanto nao souber, nao ha indicador de qualidade de "
        "producao.",
        "",
        "4. **Qual a diferenca entre `flag_encerrada` e `cod_situacao` na ordem "
        "de fabricacao?** 96,2% das ordens com `flag_encerrada = 0` ja "
        "produziram quantidade e 98,9% tem previsao de fim no passado. A flag "
        "parece encerramento administrativo e `cod_situacao` o status real "
        "(1 = ativa, 0 = cancelada), mas isso e leitura nossa. Qual das duas "
        "define \"ordem em aberto\" para a fabrica?",
        "",
        "5. **O que e `origem_pedido = \'SIM\'`?** Sao 176.559 itens de pedido "
        "e R$ 2,6 bilhoes que **nunca geraram uma unica nota fiscal em cinco "
        "anos** — 0,0% de conversao, contra 84,4% da origem PDV. Estao quase "
        "perfeitamente correlacionados com `situacao_pedido = \'PE\'` e "
        "`status_liberacao = \'BLQ\'`. Simulacao, orcamento, pedido de outro "
        "sistema? Somados a carteira, ela salta de R$ 189 milhoes para R$ 2,8 "
        "bilhoes — quatro vezes o faturamento anual.",
        "",
        "6. **Como a fabrica aponta producao?** A mediana do tempo entre o "
        "primeiro e o ultimo apontamento de uma ordem e zero dias: quase tudo "
        "cai no mesmo dia. Se o apontamento e feito em lote no fechamento, o "
        "tempo de ciclo nao esta no dado. E `data_abertura` vem depois do "
        "primeiro apontamento em 24,8% das ordens — o que ela marca de fato?",
        "",
    ], []


def secao_marts(con):
    """Aderencia a prazo e lead time saem do mesmo apontamento mas nao tem o
    mesmo grau de confianca. Separados de proposito."""
    tem = n(con, "SELECT count(*) FROM information_schema.schemata "
                 "WHERE schema_name = 'marts'")
    if not tem:
        return ["_Marts ainda nao construidos: rode `dbt build`._", ""], []

    tot, com_ap, real, ing, m_real, m_ing, lead = con.execute("""
        SELECT count(*),
               count(*) FILTER (WHERE tem_apontamento),
               100.0 * count(*) FILTER (WHERE no_prazo)
                     / nullif(count(*) FILTER (WHERE no_prazo IS NOT NULL), 0),
               100.0 * count(*) FILTER (WHERE atraso_dias_por_data_fim <= 0)
                     / nullif(count(*) FILTER (WHERE atraso_dias_por_data_fim
                                               IS NOT NULL), 0),
               median(atraso_dias), median(atraso_dias_por_data_fim),
               median(lead_time_dias)
        FROM marts.fct_ordem_producao WHERE cod_situacao = 1
    """).fetchone()
    neg, antes, lead_prod = con.execute("""
        SELECT count(*) FILTER (WHERE lead_time_dias < 0),
               count(*) FILTER (WHERE apontamento_antes_da_abertura),
               median(lead_time_producao_dias)
        FROM marts.fct_ordem_producao WHERE tem_apontamento
    """).fetchone()
    fut_2026, fut_2027, fut_2027_ap = con.execute("""
        SELECT count(*) FILTER (WHERE year(data_abertura) = 2026),
               count(*) FILTER (WHERE year(data_abertura) >= 2027),
               count(*) FILTER (WHERE year(data_abertura) >= 2027
                                  AND tem_apontamento)
        FROM marts.fct_ordem_producao WHERE data_abertura > current_date
    """).fetchone()

    return [
        "Duas coisas diferentes saem do apontamento, e elas **nao tem o mesmo "
        "grau de confianca**. A aderencia a prazo esta solida; o tempo de ciclo "
        "nao. Nao descartar as duas juntas.",
        "",
        "### Aderencia a prazo — solida",
        "",
        "Usa `data_prevista_fim` contra `data_conclusao_real`, que e o **ultimo** "
        "apontamento da ordem. O ultimo apontamento e conclusao real "
        "independente de como a fabrica aponta: mesmo que tudo seja lancado de "
        "uma vez no fechamento, a ordem nao esta concluida antes dele. O "
        "indicador vale.",
        "",
        "| | com data_fim (ingenuo) | com o apontamento (real) |",
        "|---|---:|---:|",
        f"| ordens no prazo | **{ing:.1f}%** | **{real:.1f}%** |",
        f"| mediana do atraso | {m_ing:.0f} dias (adiantado) | "
        f"+{m_real:.0f} dias |",
        "",
        f"Base: {tot:,} ordens ativas (`cod_situacao = 1`), {com_ap:,} com "
        f"apontamento ({100 * com_ap / tot:.1f}%).",
        "",
        "A ordem em que o prazo e medido muda o indicador em **41 pontos "
        "percentuais**. O numero ingenuo diz que tres em cada quatro ordens "
        "fecham no prazo, e com folga. O real diz que uma em cada tres fecha no "
        f"prazo, com mediana de {m_real:.0f} dias de atraso. **Se algum "
        "indicador de producao hoje mostra algo perto de 74%, ele esta medindo "
        "o plano contra o plano.**",
        "",
        "### Lead time / tempo de ciclo — comprometido",
        "",
        "Aqui sim ha problema, e ele **nao afeta a aderencia acima**.",
        "",
        f"O tempo do primeiro ao ultimo apontamento "
        f"(`lead_time_producao_dias`) tem mediana de {lead_prod:.0f} dias: "
        "quase toda ordem concentra o apontamento num unico dia. Isso mede a "
        "janela de apontamento, nao o tempo de fabricacao. Se a fabrica aponta "
        "em lote no fechamento, o tempo de ciclo simplesmente nao esta no dado.",
        "",
        f"E o lead time contado da abertura (`lead_time_dias`) e negativo em "
        f"{neg:,} das {com_ap:,} ordens com apontamento "
        f"(**{100 * neg / com_ap:.1f}%**): a producao terminou antes da ordem "
        f"ser aberta. Em {antes:,} ordens (**{100 * antes / com_ap:.1f}%**) o "
        "primeiro apontamento vem antes da abertura, e `data_inicio` ja era "
        "anterior a `data_abertura` em 41% das ordens (secao 3). "
        "**`data_abertura` e um registro administrativo posterior**, nao a "
        "criacao da ordem.",
        "",
        "Por isso o mart traz as duas medidas lado a lado, mais a flag "
        "`apontamento_antes_da_abertura`. **Nao publicar tempo de ciclo** ate a "
        "producao confirmar o habito de apontamento (pergunta 5 da secao 8).",
        "",
        "### Ordens com abertura no futuro",
        "",
        f"{fut_2026:,} ordens tem `data_abertura` entre hoje e o fim de 2026: "
        "isso e programacao normal, nao defeito. Ja as "
        f"{fut_2027} ordens abertas em 2027 (com apenas {fut_2027_ap} "
        "apontamentos) sao o que faz o recorte \"carteira 2027\" parecer "
        "existir. Trate 2027 como residual ate a empresa confirmar.",
        "",
    ], []


def secao_carteira(con):
    """A carteira em aberto so fecha depois de separar origem_pedido."""
    tem = n(con, "SELECT count(*) FROM information_schema.tables "
                 "WHERE table_schema = 'marts' AND table_name = 'fct_pedido'")
    if not tem:
        return ["_fct_pedido ainda nao construido: rode `dbt build`._", ""], []

    linhas = con.execute("""
        SELECT origem_pedido, round(taxa_conversao_da_origem * 100, 1),
               count(*), round(sum(valor_item_liquido) / 1e6, 1),
               round(sum(valor_em_aberto) / 1e6, 1)
        FROM marts.fct_pedido GROUP BY 1, 2 ORDER BY 3 DESC
    """).fetchall()

    total, firme = con.execute("""
        SELECT round(sum(valor_em_aberto) / 1e6, 1),
               round(sum(valor_em_aberto) FILTER (WHERE origem_converte_em_nf)
                     / 1e6, 1)
        FROM marts.fct_pedido WHERE situacao_pedido <> 'C'
    """).fetchone()

    saldo = con.execute("""
        SELECT round(sum(quantidade_saldo_origem_nao_confiavel
                         * valor_unitario_liquido) / 1e6, 1)
        FROM marts.fct_pedido WHERE situacao_pedido <> 'C'
    """).fetchone()[0]

    ano = con.execute("""
        SELECT year(data_entrega_prevista), count(DISTINCT id_pedido),
               round(sum(valor_em_aberto) / 1e6, 1)
        FROM marts.fct_pedido
        WHERE origem_converte_em_nf AND quantidade_em_aberto > 0
          AND situacao_pedido <> 'C'
        GROUP BY 1 ORDER BY 1
    """).fetchall()

    out = [
        "Tres coisas precisam estar certas para a carteira fechar. Duas ja "
        "estavam em `docs/qualidade.md`; a terceira so apareceu ao construir "
        "`fct_pedido`.",
        "",
        "1. `quantidade_saldo` nao serve (secao 7) — a origem nao a baixa.",
        "2. A ponte pedido ↔ NF esta triplicada (secao 6) — deduplicar antes.",
        "3. **`origem_pedido` separa pedido de nao-pedido** — o achado novo.",
        "",
        "### Conversao em nota fiscal por origem",
        "",
        "| origem | conversao em NF | itens | valor do pedido | em aberto |",
        "|---|---:|---:|---:|---:|",
    ]
    for orig, conv, itens, mi_ped, mi_ab in linhas:
        out.append(f"| `{orig}` | **{conv}%** | {itens:,} | R$ {mi_ped} mi | "
                   f"R$ {mi_ab} mi |")
    out += [
        "",
        "**`SIM` nunca gerou uma nota fiscal.** Nao e baixa conversao: e zero, "
        "em cinco anos e 176 mil itens. A origem esta quase perfeitamente "
        "correlacionada com `situacao_pedido = 'PE'` (pendente) e "
        "`status_liberacao = 'BLQ'` (bloqueado). `EXP` e `ORC` idem, mas sao "
        "residuais.",
        "",
        "### O tamanho do erro",
        "",
        "| criterio | carteira |",
        "|---|---:|",
        f"| pela `quantidade_saldo` da origem | R$ {saldo} mi |",
        f"| sem separar origem | R$ {total} mi |",
        f"| **so origens que faturam** | **R$ {firme} mi** |",
        "",
        f"Sem o filtro de origem a carteira daria R$ {total} milhoes — mais que "
        "o dobro de todo o faturamento de 2021 a 2026 somado. Com o filtro, "
        f"R$ {firme} milhoes, que se sustenta contra R$ 301 milhoes faturados "
        "em 2025.",
        "",
        "### Carteira por ano de entrega prevista (so origens que faturam)",
        "",
        "| ano | pedidos | em aberto |",
        "|---|---:|---:|",
    ]
    for a, ped, mi in ano:
        rot = a if a is not None else "sem data"
        out.append(f"| {rot} | {ped:,} | R$ {mi} mi |")
    out += [
        "",
        "O grosso esta em **2026**. 2027 continua residual. E sobra um resto "
        "espalhado por 2021-2025: pedidos antigos que nunca foram faturados nem "
        "cancelados — provavelmente abandono, mas isso tambem e pergunta para a "
        "empresa.",
        "",
    ]
    return out, []


def nota_rodape_servico(con):
    """Catalogo fiscal pre-populado nao e achado. Fica registrado como nota,
    fora da apresentacao."""
    tot, srv = con.execute("""
        SELECT count(*), count(DISTINCT id_servico)
        FROM raw.ponte_nota_saida_item_servico WHERE id_nota_saida_item = 0
    """).fetchone()
    so, parcial, fora = con.execute("""
        WITH d AS (SELECT DISTINCT id_nota_saida_item, id_servico
                   FROM raw.ponte_nota_saida_item_servico),
             g AS (SELECT id_servico,
                          bool_or(id_nota_saida_item = 0) AS tem,
                          bool_and(id_nota_saida_item = 0) AS so
                   FROM d GROUP BY 1)
        SELECT count(*) FILTER (WHERE so),
               count(*) FILTER (WHERE tem AND NOT so),
               count(*) FILTER (WHERE NOT tem) FROM g
    """).fetchone()
    pares_s, pares_u = con.execute("""
        WITH d AS (SELECT DISTINCT id_nota_saida_item, id_servico
                   FROM raw.ponte_nota_saida_item_servico)
        SELECT count(*) FILTER (WHERE id_nota_saida_item = 0),
               count(*) FILTER (WHERE id_nota_saida_item <> 0) FROM d
    """).fetchone()

    return [
        "_Nota tecnica, nao e achado. Nao vai para a apresentacao._",
        "",
        f"O sentinela `id_nota_saida_item = 0` da ponte de servicos ({tot:,} "
        f"linhas, {pares_s} pares distintos) foi verificado: `id_servico` esta "
        "preenchido e valido em todas. A ponte nao carrega valor, entao nao ha "
        "receita em risco.",
        "",
        f"Os {so} codigos da LC 116 que so aparecem no sentinela **nao sao "
        "anomalia**: o catalogo fiscal vem pre-populado com a lista inteira da "
        f"lei, e usar {parcial + fora} de {so + parcial + fora} codigos e o "
        "normal de uma industria. O sentinela apenas carrega o resto do "
        "catalogo.",
        "",
        f"O que importa operacionalmente: os {pares_u:,} pares uteis "
        f"({100 * pares_u / (pares_s + pares_u):.1f}% dos vinculos) ficam em "
        "`stg_ponte_nota_saida_item_servico`, com o sentinela descartado. Era "
        "so isso que os \"22% de orfaos\" da secao 2 significavam.",
        "",
    ], []


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
        ("8. Impacto em relatorios existentes e a correcao no dbt",
         secao_impacto(con)),
        ("", secao_perguntas()),
        ("9. Efeito da correcao de prazo nos marts", secao_marts(con)),
        ("10. Carteira em aberto: o filtro que faltava", secao_carteira(con)),
        ("Apendice — sentinela da ponte de servicos",
         nota_rodape_servico(con)),
    ]:
        out += ([f"## {titulo}", ""] if titulo else []) + linhas + [""]

    (DOCS / "qualidade.md").write_text("\n".join(out), encoding="utf-8")
    print("-> docs/qualidade.md")


if __name__ == "__main__":
    main()
