"""Gera docs/modelo.md: mapa do star schema de VENDAS e PRODUCAO a partir dos
relacionamentos inferidos e validados em docs/relacionamentos.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CAT = json.loads((DOCS / "catalogo.json").read_text(encoding="utf-8"))["tabelas"]
REL = json.loads((DOCS / "relacionamentos.json").read_text(encoding="utf-8"))

TEMA = {t: g for g, ts in REL["escopo"].items() for t in ts}

# dim_calendario nao tem FK: e conformada por igualdade de data.
PAPEIS_DATA = {
    "fat_pedido": ["data_emissao", "data_entrega_prevista", "data_inclusao"],
    "fat_nota_saida": ["data_emissao", "data_saida"],
    "fat_ordem_fabricacao": ["data_abertura", "data_prevista_fim", "data_inicio",
                             "data_fim", "data_entrega"],
    "fat_ordem_movimento": ["data_apontamento"],
    "fat_pontuacao_producao": ["data_referencia"],
    "fat_contrato_loja": ["data_contrato", "data_assinatura"],
    "ponte_nota_item_pedido_item": ["data_vinculo"],
}


def validos(temas):
    """Relacionamentos com validacao feita, dentro dos temas pedidos."""
    for r in REL["relacionamentos"]:
        v = r.get("validacao")
        if not v or not r.get("tabela_ref"):
            continue
        if temas and TEMA.get(r["tabela"]) not in temas:
            continue
        yield r


def mermaid(temas, titulo):
    """Arestas dos fatos do tema; arestas dim->dim so entram se ligarem uma
    dimensao que ja aparece no diagrama (evita puxar o schema inteiro)."""
    principais = [r for r in validos(temas) if TEMA.get(r["tabela"]) != "dimensoes"]
    usados = {n for r in principais for n in (r["tabela"], r["tabela_ref"])}
    arestas = list(principais)
    for _ in range(3):  # propaga snowflake ate estabilizar
        novos = [r for r in validos({"dimensoes"})
                 if r not in arestas and r["tabela_ref"] in usados]
        if not novos:
            break
        arestas += novos
        usados |= {n for r in novos for n in (r["tabela"], r["tabela_ref"])}

    linhas = [f"### {titulo}", "", "```mermaid", "graph LR"]
    grupos = [("Dimensoes", "dim_"), ("Fatos", "fat_"), ("Pontes", "ponte_")]
    for nome, pref in grupos:
        membros = sorted(n for n in usados if n.startswith(pref))
        if not membros:
            continue
        linhas.append(f"  subgraph {nome}")
        for n in membros:
            lin = max(CAT[n]["est_linhas"], 0)
            linhas.append(f'    {n}["{n}<br/>{lin:,} linhas"]')
        linhas.append("  end")
    vistas = set()
    for r in sorted(arestas, key=lambda x: (x["tabela_ref"], x["tabela"], x["coluna"])):
        v = r["validacao"]
        rot = r["coluna"] + (f" - {v['pct_orfaos']}% orfaos" if v["orfaos"] else "")
        chave = (r["tabela_ref"], r["tabela"], rot)
        if chave in vistas:
            continue
        vistas.add(chave)
        linhas.append(f'  {r["tabela_ref"]} -->|{rot}| {r["tabela"]}')
    linhas += ["```", ""]
    return linhas


def tabela_rel(temas):
    linhas = ["| de | coluna | para | coluna | linhas | nulos | orfaos |",
              "|----|--------|------|--------|-------:|------:|-------:|"]
    for r in sorted(validos(temas), key=lambda x: (x["tabela"], x["coluna"])):
        v = r["validacao"]
        orf = f"{v['orfaos']:,} ({v['pct_orfaos']}%)" if v["orfaos"] else "0"
        linhas.append(
            f"| `{r['tabela']}` | `{r['coluna']}` | `{r['tabela_ref']}` | "
            f"`{v['coluna_ref']}` | {v['total']:,} | {v['nulos']:,} | {orf} |")
    linhas.append("")
    return linhas


def main():
    out = [
        "# Modelo — star schema de vendas e producao",
        "",
        "> **O banco nao declara nenhuma FOREIGN KEY.** Os relacionamentos abaixo "
        "foram inferidos por convencao de nome (`coluna X` = PK simples da tabela "
        "cuja PK e `X`) e **validados medindo orfaos no proprio Postgres** "
        "(`scripts/02_relacionamentos.py`). A coluna *orfaos* na tabela e a prova.",
        "",
        "Gerado por `scripts/03_modelo.py`.",
        "",
        "## Diagramas",
        "",
    ]
    out += mermaid({"vendas", "dimensoes"}, "Vendas")
    out += mermaid({"producao", "dimensoes"}, "Producao")
    out += mermaid({"vendas", "producao"}, "Ligacao vendas ↔ producao")

    out += [
        "## dim_calendario (dimensao conformada por data)",
        "",
        "`dim_calendario` tem PK `data` e nao aparece como FK em lugar nenhum: "
        "liga por igualdade de data, em varios papeis por fato. Papeis "
        "identificados no escopo:",
        "",
    ]
    for t, cols in PAPEIS_DATA.items():
        out.append(f"- `{t}`: " + ", ".join(f"`{c}`" for c in cols))
    out += ["", "## Relacionamentos validados", "", "### Vendas", ""]
    out += tabela_rel({"vendas"})
    out += ["### Producao", ""]
    out += tabela_rel({"producao"})
    out += ["### Entre dimensoes (snowflake)", ""]
    out += tabela_rel({"dimensoes"})

    out += [
        "## Observacoes de modelagem",
        "",
        "- **Nao existe `id_cliente` em `fat_pedido`.** O cliente do pedido so se "
        "alcanca por `fat_pedido → dim_estabelecimento → dim_cliente`. Ja "
        "`fat_nota_saida` tem `id_cliente` direto. Comparacoes pedido x "
        "faturamento por cliente precisam desse cuidado.",
        "- **Duas dimensoes de item.** `dim_item` e o catalogo global (1 linha por "
        "codigo, usada por NF de saida e producao) e `dim_item_empresa` e o item "
        "por empresa, com **id proprio e diferente** (usada por pedido de venda e "
        "item de NF). `dim_item_ordem` e a visao de producao e faz a ponte para "
        "`dim_item`.",
        "- **`fat_nota_saida_item_pontuacao.id_ordem_fabricacao` guarda "
        "`num_ordem`, nao a PK.** Contra `id_ordem_fabricacao` da 100% de orfaos; "
        "contra `num_ordem`, 0%. Sempre junte por `num_ordem`.",
        "- `ponte_pedido_configuracao_ordem` e o unico caminho pedido ↔ ordem de "
        "fabricacao; grao = pedido x configuracao x ordem.",
        "- `fat_pedido_representante_secundario` tem grao pedido x representante: "
        "somar valor por ela duplica faturamento.",
        "",
    ]
    (DOCS / "modelo.md").write_text("\n".join(out), encoding="utf-8")
    print("-> docs/modelo.md")


if __name__ == "__main__":
    main()
