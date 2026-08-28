"""O banco nao tem FK declarada. Este script INFERE os relacionamentos por
convencao de nome (coluna X = PK simples da tabela cuja PK e X), valida cada
candidato medindo orfaos no Postgres e grava docs/relacionamentos.json.
So metadados e contagens sao impressos.
"""
import json
import re
from pathlib import Path

from _db import SCHEMA, query

ROOT = Path(__file__).resolve().parent.parent
CAT = json.loads((ROOT / "docs" / "catalogo.json").read_text(encoding="utf-8"))["tabelas"]

# Tabelas fora do escopo desta fase (contabil/financeiro/compras) e as gigantes
# que o usuario pediu para ignorar.
IGNORAR_ALVO = {"dim_configurador", "dim_mascara"}

# Correcoes manuais confirmadas por medicao no banco: colunas cujo nome sugere
# uma chave mas que na verdade guardam outra.
OVERRIDES = {
    # a coluna guarda o NUMERO da ordem, nao o id surrogate (100% orfao contra
    # id_ordem_fabricacao; 0% orfao contra num_ordem)
    ("fat_nota_saida_item_pontuacao", "id_ordem_fabricacao"):
        ("fat_ordem_fabricacao", "num_ordem"),
}

ESCOPO = {
    "vendas": [
        "fat_pedido", "fat_pedido_item", "fat_pedido_representante_secundario",
        "fat_nota_saida", "fat_nota_saida_item", "fat_nota_saida_item_pedido",
        "fat_nota_saida_item_pontuacao", "ponte_nota_item_pedido_item",
        "ponte_nota_saida_item_servico", "fat_contrato_loja",
        "fat_contrato_loja_parcela",
    ],
    "producao": [
        "fat_ordem_fabricacao", "fat_ordem_roteiro", "fat_ordem_movimento",
        "fat_pontuacao_producao", "ponte_pedido_configuracao_ordem",
    ],
    # dimensoes usadas pelos fatos acima: precisamos das FKs delas tambem
    # (cliente do pedido so aparece via dim_estabelecimento, por exemplo)
    "dimensoes": [
        "dim_empresa", "dim_estabelecimento", "dim_cliente", "dim_representante",
        "dim_item", "dim_item_empresa", "dim_item_ordem", "dim_item_classificacao",
        "dim_tipo_nf_saida", "dim_condicao_pagamento", "dim_condicao_pagamento_parcela",
        "dim_operacao", "dim_centro_trabalho", "dim_centro_custo", "dim_cidade",
        "dim_unidade_medida", "dim_servico_lei", "dim_calendario",
    ],
}
TABELAS_ESCOPO = [t for v in ESCOPO.values() for t in v]


FK_NO_COMENTARIO = re.compile(r"\[FK\s*->\s*([a-z_]+)\.([a-z_]+)\]", re.I)


def fks_declaradas():
    """O banco nao tem FK como constraint, mas os COMMENTs de coluna declaram
    o alvo em texto: `[FK -> dim_empresa.id_empresa]`. Fonte primaria."""
    out = {}
    for nome, t in CAT.items():
        for c in t["colunas"]:
            m = FK_NO_COMENTARIO.search(c["descricao"] or "")
            if m:
                out[(nome, c["coluna"])] = (m.group(1), m.group(2))
    return out


DECLARADAS = fks_declaradas()


def mapa_pk():
    """coluna PK simples -> [tabelas]. Colisoes viram candidatos ambiguos."""
    m = {}
    for nome, t in CAT.items():
        pk = t.get("pk") or []
        if len(pk) == 1:
            m.setdefault(pk[0], []).append(nome)
    return m


def candidatos():
    pks = mapa_pk()
    out = []
    for nome in TABELAS_ESCOPO:
        t = CAT[nome]
        pk_propria = set(t.get("pk") or [])
        for c in t["colunas"]:
            col = c["coluna"]
            alvos = [a for a in pks.get(col, []) if a != nome]
            if not alvos or col in pk_propria and len(alvos) == 0:
                continue
            # prefere dimensao quando ha empate
            decl = DECLARADAS.get((nome, col))
            if decl:
                escolha = decl[0]
            else:
                dims = [a for a in alvos if a.startswith("dim_")]
                escolha = (dims[0] if len(dims) == 1
                           else (alvos[0] if len(alvos) == 1 else None))
            out.append({
                "tabela": nome, "coluna": col,
                "tabela_ref": escolha, "ambiguo": alvos if escolha is None else None,
                "candidatos": alvos,
                "declarada_no_comentario": bool(DECLARADAS.get((nome, col))),
            })
    # o COMMENT pode declarar FK que a convencao de nome nao pega
    # (fat_pedido.id_empresa_faturamento -> dim_empresa.id_empresa)
    cobertos = {(c["tabela"], c["coluna"]) for c in out}
    for (tab, col), (ref, _) in DECLARADAS.items():
        if tab in TABELAS_ESCOPO and (tab, col) not in cobertos:
            out.append({"tabela": tab, "coluna": col, "tabela_ref": ref,
                        "ambiguo": None, "candidatos": [ref],
                        "declarada_no_comentario": True})
    return out


def validar(c):
    """Mede cobertura da FK candidata: total, nulos, orfaos."""
    ref = c["tabela_ref"]
    if ref is None or ref in IGNORAR_ALVO:
        return None
    ov = OVERRIDES.get((c["tabela"], c["coluna"]))
    decl = DECLARADAS.get((c["tabela"], c["coluna"]))
    col_ref = ov[1] if ov else (decl[1] if decl else CAT[ref]["pk"][0])
    c["nota"] = ("coluna guarda o valor de "
                 f"{ref}.{col_ref}, nao a PK") if ov else None
    sql = f"""
    SELECT count(*) AS total,
           count(*) FILTER (WHERE f.{c['coluna']} IS NULL) AS nulos,
           count(*) FILTER (WHERE f.{c['coluna']} IS NOT NULL
                              AND d.{col_ref} IS NULL) AS orfaos,
           count(DISTINCT f.{c['coluna']}) AS distintos
    FROM {SCHEMA}.{c['tabela']} f
    LEFT JOIN (SELECT DISTINCT {col_ref} FROM {SCHEMA}.{ref}) d
           ON d.{col_ref} = f.{c['coluna']}
    """
    _, rows = query(sql)
    total, nulos, orfaos, distintos = rows[0]
    return {"total": total, "nulos": nulos, "orfaos": orfaos, "distintos": distintos,
            "coluna_ref": col_ref,
            "pct_orfaos": round(100 * orfaos / total, 3) if total else 0.0}


def main():
    cands = candidatos()
    print(f"{len(cands)} candidatos a FK no escopo\n")
    for c in cands:
        v = validar(c)
        c["validacao"] = v
        if v is None:
            print(f"  ~ {c['tabela']}.{c['coluna']} -> "
                  f"{c['tabela_ref'] or c['ambiguo']} (ignorado/ambiguo)")
            continue
        marca = "OK " if v["pct_orfaos"] == 0 else ("!! " if v["pct_orfaos"] > 1 else " ~ ")
        print(f"{marca}{c['tabela']}.{c['coluna']} -> {c['tabela_ref']}"
              f"  total={v['total']:,} nulos={v['nulos']:,} "
              f"orfaos={v['orfaos']:,} ({v['pct_orfaos']}%)")

    # o que o COMMENT declara e o escopo nao cobriu
    cobertos = {(c["tabela"], c["coluna"]) for c in cands}
    fora = sorted(k for k in DECLARADAS if k not in cobertos
                  and k[0] in TABELAS_ESCOPO)
    if fora:
        print(f"\nFKs declaradas em COMMENT dentro do escopo mas nao inferidas "
              f"por nome ({len(fora)}):")
        for t, col in fora:
            print(f"  {t}.{col} -> {'.'.join(DECLARADAS[(t, col)])}")

    (ROOT / "docs" / "relacionamentos.json").write_text(
        json.dumps({"escopo": ESCOPO, "relacionamentos": cands},
                   ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("\n-> docs/relacionamentos.json")


if __name__ == "__main__":
    main()
