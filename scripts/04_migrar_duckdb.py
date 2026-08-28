"""Copia do Postgres para dados.duckdb (schema `raw`) apenas as tabelas dos
temas vendas e producao mais as dimensoes que elas referenciam.

Idempotente: CREATE OR REPLACE por tabela. Ao final valida contagem
origem vs destino. Nao imprime dados: so nomes e contagens.

Uso:
    uv run python scripts/04_migrar_duckdb.py            # migra tudo
    uv run python scripts/04_migrar_duckdb.py --listar   # so mostra o plano
    uv run python scripts/04_migrar_duckdb.py --validar  # so revalida contagens
"""
import argparse
import os
import time
from pathlib import Path

import duckdb
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SCHEMA = os.environ.get("PG_SCHEMA", "bi")
DUCK = ROOT / "dados.duckdb"

# Lista derivada de docs/modelo.md (FKs inferidas e validadas em 02).
TABELAS = {
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
    "dimensoes": [
        "dim_calendario", "dim_empresa", "dim_cidade", "dim_estabelecimento",
        "dim_cliente", "dim_representante", "dim_condicao_pagamento",
        "dim_condicao_pagamento_parcela", "dim_tipo_nf_saida", "dim_item",
        "dim_item_empresa", "dim_item_ordem", "dim_item_classificacao",
        "dim_unidade_medida", "dim_servico_lei", "dim_operacao",
        "dim_centro_trabalho", "dim_centro_custo",
    ],
}
TODAS = [t for g in TABELAS.values() for t in g]


def dsn():
    return (f"host={os.environ['PG_HOST']} port={os.environ['PG_PORT']} "
            f"dbname={os.environ['PG_DB']} user={os.environ['PG_USER']} "
            f"password={os.environ['PG_PASSWORD']}")


def conectar():
    con = duckdb.connect(str(DUCK))
    con.execute("INSTALL postgres; LOAD postgres;")
    con.execute(f"ATTACH '{dsn()}' AS pg (TYPE postgres, READ_ONLY)")
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    return con


def migrar(con, tabelas):
    for i, t in enumerate(tabelas, 1):
        ini = time.time()
        con.execute(f"CREATE OR REPLACE TABLE raw.{t} AS "
                    f"SELECT * FROM pg.{SCHEMA}.{t}")
        n = con.execute(f"SELECT count(*) FROM raw.{t}").fetchone()[0]
        print(f"[{i:2}/{len(tabelas)}] {t:<42} {n:>10,} linhas  "
              f"{time.time() - ini:6.1f}s", flush=True)


def validar(con, tabelas):
    print(f"\n{'tabela':<42} {'origem':>11} {'destino':>11}  ok")
    problemas = []
    for t in tabelas:
        org = con.execute(f"SELECT count(*) FROM pg.{SCHEMA}.{t}").fetchone()[0]
        dst = con.execute(f"SELECT count(*) FROM raw.{t}").fetchone()[0]
        ok = org == dst
        if not ok:
            problemas.append((t, org, dst))
        print(f"{t:<42} {org:>11,} {dst:>11,}  {'sim' if ok else 'NAO'}")
    print(f"\n{len(tabelas) - len(problemas)}/{len(tabelas)} tabelas conferem")
    if problemas:
        raise SystemExit(f"divergencia em: {[p[0] for p in problemas]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--validar", action="store_true")
    ap.add_argument("--apenas", nargs="*", help="migrar so estas tabelas")
    a = ap.parse_args()

    alvo = a.apenas or TODAS
    if a.listar:
        for g, ts in TABELAS.items():
            print(f"\n{g} ({len(ts)}):")
            for t in ts:
                print(f"  - {t}")
        print(f"\ntotal: {len(TODAS)} tabelas -> {DUCK}")
        return

    con = conectar()
    if not a.validar:
        migrar(con, alvo)
    validar(con, alvo)
    tam = DUCK.stat().st_size / 1024**3
    print(f"\n{DUCK.name}: {tam:.2f} GB")


if __name__ == "__main__":
    main()
