"""Extrai o catalogo do Postgres (comentarios, colunas, PKs, FKs) e gera:
  - docs/catalogo.json  (insumo dos demais scripts)
  - docs/dicionario.md
Nao imprime dados de negocio: apenas metadados e contagens.
"""
import json
from pathlib import Path

from _db import SCHEMA, query

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

SQL_TABELAS = """
SELECT c.relname AS tabela,
       CASE c.relkind WHEN 'r' THEN 'tabela' WHEN 'p' THEN 'particionada'
            WHEN 'v' THEN 'view' WHEN 'm' THEN 'view materializada' END AS tipo,
       obj_description(c.oid, 'pg_class') AS descricao,
       c.reltuples::bigint AS est_linhas,
       pg_total_relation_size(c.oid) AS bytes
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = %s AND c.relkind IN ('r','p','v','m')
ORDER BY c.relname
"""

SQL_COLUNAS = """
SELECT c.relname AS tabela,
       a.attnum  AS pos,
       a.attname AS coluna,
       format_type(a.atttypid, a.atttypmod) AS tipo,
       NOT a.attnotnull AS aceita_nulo,
       pg_get_expr(d.adbin, d.adrelid) AS padrao,
       col_description(c.oid, a.attnum) AS descricao
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_attribute a ON a.attrelid = c.oid
LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = a.attnum
WHERE n.nspname = %s AND c.relkind IN ('r','p','v','m')
  AND a.attnum > 0 AND NOT a.attisdropped
ORDER BY c.relname, a.attnum
"""

SQL_CONSTRAINTS = """
SELECT con.contype,
       cl.relname  AS tabela,
       con.conname AS nome,
       (SELECT array_agg(att.attname ORDER BY k.ord)
          FROM unnest(con.conkey) WITH ORDINALITY AS k(attnum, ord)
          JOIN pg_attribute att ON att.attrelid = cl.oid AND att.attnum = k.attnum
       ) AS colunas,
       fcl.relname AS tabela_ref,
       (SELECT array_agg(att.attname ORDER BY k.ord)
          FROM unnest(con.confkey) WITH ORDINALITY AS k(attnum, ord)
          JOIN pg_attribute att ON att.attrelid = fcl.oid AND att.attnum = k.attnum
       ) AS colunas_ref
FROM pg_constraint con
JOIN pg_class cl ON cl.oid = con.conrelid
JOIN pg_namespace n ON n.oid = cl.relnamespace
LEFT JOIN pg_class fcl ON fcl.oid = con.confrelid
WHERE n.nspname = %s AND con.contype IN ('p','f','u')
ORDER BY cl.relname, con.contype, con.conname
"""


def fetch(sql):
    cols, rows = query(sql, (SCHEMA,))
    return [dict(zip(cols, r)) for r in rows]


def humano(b):
    if b is None:
        return ""
    for unidade in ("B", "KB", "MB", "GB"):
        if b < 1024 or unidade == "GB":
            return f"{b:.0f} {unidade}" if unidade == "B" else f"{b:.1f} {unidade}"
        b /= 1024


def main():
    tabelas = fetch(SQL_TABELAS)
    colunas = fetch(SQL_COLUNAS)
    constraints = fetch(SQL_CONSTRAINTS)

    por_tabela = {t["tabela"]: {**t, "colunas": [], "pk": [], "fks": [], "uks": []}
                  for t in tabelas}
    for c in colunas:
        por_tabela[c["tabela"]]["colunas"].append(c)
    for con in constraints:
        alvo = por_tabela.get(con["tabela"])
        if not alvo:
            continue
        if con["contype"] == "p":
            alvo["pk"] = con["colunas"]
        elif con["contype"] == "f":
            alvo["fks"].append({
                "nome": con["nome"], "colunas": con["colunas"],
                "tabela_ref": con["tabela_ref"], "colunas_ref": con["colunas_ref"],
            })
        else:
            alvo["uks"].append({"nome": con["nome"], "colunas": con["colunas"]})

    (DOCS / "catalogo.json").write_text(
        json.dumps({"schema": SCHEMA, "tabelas": por_tabela}, ensure_ascii=False,
                   indent=2, default=str), encoding="utf-8")

    prefixos = [("dim_", "Dimensoes"), ("fat_", "Fatos"),
                ("ponte_", "Pontes"), ("vw_", "Views")]
    linhas = [
        "# Dicionario de dados — schema `bi`",
        "",
        "Gerado por `scripts/01_dicionario.py` a partir do catalogo do Postgres "
        "(`obj_description` / `col_description`). Descricoes sao as do proprio banco; "
        "onde estao vazias, o banco nao tem COMMENT.",
        "",
        f"- Objetos: **{len(tabelas)}**",
        "",
        "## Indice",
        "",
    ]
    for pref, titulo in prefixos:
        nomes = [t["tabela"] for t in tabelas if t["tabela"].startswith(pref)]
        linhas.append(f"**{titulo}** ({len(nomes)}): " +
                      ", ".join(f"[{n}](#{n.replace('_','-')})" for n in nomes))
        linhas.append("")

    for pref, titulo in prefixos:
        grupo = [t for t in tabelas if t["tabela"].startswith(pref)]
        if not grupo:
            continue
        linhas += [f"## {titulo}", ""]
        for t in grupo:
            info = por_tabela[t["tabela"]]
            linhas += [f"### {t['tabela']}", ""]
            if t["descricao"]:
                linhas += [f"> {t['descricao']}", ""]
            meta = [f"tipo: {t['tipo']}"]
            if t["tipo"] != "view":
                meta.append(f"linhas (estimativa): {max(t['est_linhas'], 0):,}")
                meta.append(f"tamanho: {humano(t['bytes'])}")
            linhas += ["`" + " | ".join(meta) + "`", ""]
            if info["pk"]:
                linhas += [f"**PK:** `{', '.join(info['pk'])}`", ""]
            if info["uks"]:
                for u in info["uks"]:
                    linhas.append(f"**UNIQUE:** `{', '.join(u['colunas'])}`")
                linhas.append("")
            if info["fks"]:
                linhas += ["**FKs:**", ""]
                for fk in info["fks"]:
                    linhas.append(
                        f"- `{', '.join(fk['colunas'])}` → "
                        f"`{fk['tabela_ref']}({', '.join(fk['colunas_ref'])})`")
                linhas.append("")
            linhas += ["| # | coluna | tipo | nulo | descricao |",
                       "|---|--------|------|------|-----------|"]
            pk = set(info["pk"] or [])
            fkcols = {c for fk in info["fks"] for c in fk["colunas"]}
            for c in info["colunas"]:
                marca = "🔑" if c["coluna"] in pk else ("🔗" if c["coluna"] in fkcols else "")
                desc = (c["descricao"] or "").replace("\n", " ").replace("|", "\\|")
                linhas.append(
                    f"| {c['pos']} | {marca}`{c['coluna']}` | `{c['tipo']}` | "
                    f"{'sim' if c['aceita_nulo'] else 'nao'} | {desc} |")
            linhas.append("")

    (DOCS / "dicionario.md").write_text("\n".join(linhas), encoding="utf-8")

    com_com_tab = sum(1 for t in tabelas if t["descricao"])
    com_com_col = sum(1 for c in colunas if c["descricao"])
    print(f"objetos: {len(tabelas)} (com COMMENT: {com_com_tab})")
    print(f"colunas: {len(colunas)} (com COMMENT: {com_com_col})")
    print(f"PKs: {sum(1 for t in por_tabela.values() if t['pk'])} | "
          f"FKs: {sum(len(t['fks']) for t in por_tabela.values())}")
    print("-> docs/dicionario.md, docs/catalogo.json")


if __name__ == "__main__":
    main()
