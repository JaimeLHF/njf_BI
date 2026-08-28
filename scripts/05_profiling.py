"""Perfila as tabelas migradas para raw no DuckDB e grava um HTML por tabela
em reports/. Amostra as grandes. Colunas com PII sao mascaradas antes de
perfilar: o relatorio mostraria valores reais de cliente.

Uso: uv run python scripts/05_profiling.py [--limite 200000] [--apenas t1 t2]
"""
import argparse
import re
import time
from pathlib import Path

import duckdb
from ydata_profiling import ProfileReport

ROOT = Path(__file__).resolve().parent.parent
DUCK = ROOT / "dados.duckdb"
REPORTS = ROOT / "reports"

# Nomes de coluna que carregam dado pessoal/identificavel de cliente.
PII = re.compile(
    r"(nome|razao_social|fantasia|cnpj|cpf|endereco|complemento|bairro|cep|"
    r"usuario|texto_|pedido_cliente)", re.I)


def mascarar(con, tabela, limite):
    cols = con.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema='raw' AND table_name=? ORDER BY ordinal_position",
        [tabela]).fetchall()
    sel, ocultas = [], []
    for (c,) in cols:
        if PII.search(c):
            # preserva cardinalidade e nulidade sem expor o valor
            sel.append(f"CASE WHEN {c} IS NULL THEN NULL "
                       f"ELSE md5(CAST({c} AS VARCHAR)) END AS {c}")
            ocultas.append(c)
        else:
            sel.append(c)
    amostra = f" USING SAMPLE {limite} ROWS" if limite else ""
    df = con.execute(
        f"SELECT {', '.join(sel)} FROM raw.{tabela}{amostra}").df()
    return df, ocultas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite", type=int, default=200_000,
                    help="linhas por tabela; 0 = tudo")
    ap.add_argument("--apenas", nargs="*")
    a = ap.parse_args()

    REPORTS.mkdir(exist_ok=True)
    con = duckdb.connect(str(DUCK), read_only=True)
    tabelas = a.apenas or [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='raw' ORDER BY table_name").fetchall()]

    for i, t in enumerate(tabelas, 1):
        n = con.execute(f"SELECT count(*) FROM raw.{t}").fetchone()[0]
        limite = a.limite if (a.limite and n > a.limite) else 0
        ini = time.time()
        df, ocultas = mascarar(con, t, limite)
        titulo = f"{t} — {n:,} linhas" + (f" (amostra {limite:,})" if limite else "")
        rel = ProfileReport(df, title=titulo, minimal=True, progress_bar=False,
                            explorative=False)
        rel.to_file(REPORTS / f"{t}.html")
        print(f"[{i:2}/{len(tabelas)}] {t:<42} {len(df):>9,} lin  "
              f"{len(ocultas)} col mascaradas  {time.time() - ini:6.1f}s",
              flush=True)
    print(f"\n-> {len(tabelas)} relatorios em reports/")


if __name__ == "__main__":
    main()
