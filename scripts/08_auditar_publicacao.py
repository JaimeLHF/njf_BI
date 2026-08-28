"""Portão de segurança do arquivo publicado.

Varre dados_pub.duckdb procurando qualquer coisa que identifique uma entidade
individual, e confronta os valores de texto contra as dimensões reais do banco
completo. Sai com código 1 se achar algo — para poder virar passo de CI.

Uso: uv run python scripts/08_auditar_publicacao.py
"""
import re
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "dados_pub.duckdb"
COMPLETO = ROOT / "dados.duckdb"

MIN_GRUPO = 5

# nomes de coluna que não deveriam existir num arquivo agregado
COLUNA_PROIBIDA = re.compile(
    r"(nome_cliente|razao_social|fantasia|cnpj|cpf|endereco|complemento|bairro|"
    r"cep|cod_cliente|id_cliente|cod_item|id_item|cod_familia|num_ordem|"
    r"id_ordem|num_pedido|id_pedido|id_nota|num_nota|usuario|"
    r"nome_representante|cod_representante|id_representante)", re.I)

# grão proibido: uma linha por documento
COLUNA_GRAO = re.compile(r"^(id_|num_)", re.I)

CNPJ = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
# duas ou mais palavras capitalizadas seguidas: assinatura de nome próprio
NOME_PROPRIO = re.compile(r"\b[A-ZÀ-Ú][a-zà-ú]{2,}\s+[A-ZÀ-Ú][a-zà-ú]{2,}")

# textos que sabemos serem rótulos legítimos do painel
ALLOWLIST = {
    "sem canal", "outros", "Outros", "sem representante", "a vencer",
    "sem data prevista", "vencida ha mais de 1 ano", "vencida ha menos de 1 ano",
    "cancelado", "nao faturado", "faturado parcial", "faturado total",
    "1 unidade", "2 a 5", "6 a 20", "21 a 100", "mais de 100",
    "1 a 2", "3 a 5", "6 a 10", "11 ou mais", "vencida",
}

# Categorias de negócio que colidem com algum cadastro homônimo mas não
# identificam ninguém: "CONSUMIDOR FINAL" é canal com centenas de clientes e
# também o nome de um cliente cadastrado. Liberadas explicitamente, uma a uma.
CATEGORIA_HOMONIMA = {"CONSUMIDOR FINAL", "EMPRESA", "INDUSTRIA",
                      "REPRESENTANTE", "CONTRACT"}


def main():
    achados = []
    con = duckdb.connect(str(PUB), read_only=True)
    tabelas = [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'main' ORDER BY 1").fetchall()]

    print(f"Auditando {PUB.name} — {len(tabelas)} tabelas\n")

    # ---------------------------------------------- 1. nomes de coluna
    print("1. Colunas com nome suspeito")
    colunas = con.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns WHERE table_schema = 'main'
        ORDER BY table_name, ordinal_position
    """).fetchall()
    ruins = [(t, c) for t, c, _ in colunas
             if COLUNA_PROIBIDA.search(c) or COLUNA_GRAO.match(c)]
    if ruins:
        for t, c in ruins:
            print(f"   !! {t}.{c}")
            achados.append(f"coluna {t}.{c}")
    else:
        print("   nenhuma.")

    # ---------------------------------------------- 2. conteúdo de texto
    print("\n2. Conteúdo das colunas de texto")
    textuais = [(t, c) for t, c, dt in colunas if dt.upper() in ("VARCHAR", "TEXT")]
    valores_por_coluna = {}
    for t, c in textuais:
        vals = [r[0] for r in con.execute(
            f'SELECT DISTINCT "{c}" FROM "{t}" WHERE "{c}" IS NOT NULL').fetchall()]
        valores_por_coluna[(t, c)] = vals
        for v in vals:
            if v in ALLOWLIST or v.startswith("Representante "):
                continue
            motivo = None
            if CNPJ.search(v):
                motivo = "parece CNPJ"
            elif CPF.search(v):
                motivo = "parece CPF"
            elif NOME_PROPRIO.search(v):
                motivo = "parece nome próprio"
            elif re.fullmatch(r"\d{3,}", v.strip()):
                motivo = "código numérico"
            if motivo:
                print(f"   !! {t}.{c}: {motivo} -> {v[:40]!r}")
                achados.append(f"valor em {t}.{c} ({motivo})")
    print(f"   {len(textuais)} colunas de texto varridas.")

    # ------------------------------- 3. confronto com as dimensões reais
    print("\n3. Confronto com nomes reais do banco completo")
    if COMPLETO.exists():
        # conexão própria em memória: attachar o banco completo na conexão
        # read-only do publicado dá conflito de catálogo
        # O alias tem de ser `dados`: as views de staging foram criadas pelo
        # dbt com esse nome de catálogo e o referenciam internamente.
        aud = duckdb.connect()
        aud.execute(f"ATTACH '{COMPLETO}' AS dados (READ_ONLY)")
        reais = set()
        for consulta in [
            "SELECT DISTINCT nome_cliente FROM dados.staging.stg_dim_cliente",
            "SELECT DISTINCT nome_representante FROM dados.staging.stg_dim_representante",
            "SELECT DISTINCT razao_social FROM dados.staging.stg_dim_empresa",
            "SELECT DISTINCT nome_fantasia FROM dados.staging.stg_dim_empresa",
            "SELECT DISTINCT razao_social FROM dados.staging.stg_dim_estabelecimento",
            "SELECT DISTINCT nome_fantasia FROM dados.staging.stg_dim_estabelecimento",
        ]:
            for (v,) in aud.execute(consulta).fetchall():
                if v and len(str(v).strip()) > 3:
                    reais.add(str(v).strip().upper())
        vazou = []
        for (t, c), vals in valores_por_coluna.items():
            for v in vals:
                alvo = str(v).strip().upper()
                # rótulos do painel e categorias homônimas não contam: existe
                # até um cliente cadastrado com o nome "Outros"
                if (v in ALLOWLIST or v.startswith("Representante ")
                        or alvo in CATEGORIA_HOMONIMA
                        or alvo in {x.upper() for x in ALLOWLIST}):
                    continue
                if alvo in reais:
                    vazou.append((t, c, v))
        if vazou:
            for t, c in sorted(set((t, c) for t, c, _ in vazou)):
                quantos = sum(1 for x, y, _ in vazou if (x, y) == (t, c))
                print(f"   !! {t}.{c}: {quantos} valor(es) batem com nome real")
                achados.append(f"nome real em {t}.{c}")
        else:
            print(f"   nenhum dos {len(reais):,} nomes reais aparece no publicado.")
        aud.close()
    else:
        print("   (banco completo ausente, confronto pulado)")

    # ---------------------------------------------- 4. grupos pequenos
    print(f"\n4. Grupos com menos de {MIN_GRUPO} registros")
    pequenos = []
    for t, c, _ in colunas:
        if c in ("ordens", "pedidos", "notas", "itens"):
            achou = con.execute(
                f'SELECT count(*) FROM "{t}" WHERE "{c}" > 0 AND "{c}" < {MIN_GRUPO}'
            ).fetchone()[0]
            if achou:
                print(f"   !! {t}.{c}: {achou} linha(s) abaixo de {MIN_GRUPO}")
                pequenos.append(f"{t}.{c}")
                achados.append(f"grupo pequeno em {t}.{c}")
    if not pequenos:
        print("   nenhum.")

    # ---------------------------------------------- 5. volume por tabela
    print("\n5. Volume — nenhuma tabela deve ter grão de documento")
    for t in tabelas:
        n = con.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
        marca = " !!" if n > 5000 else ""
        print(f"   {t:<28} {n:>6,} linhas{marca}")
        if n > 5000:
            achados.append(f"{t} com {n} linhas")

    mb = PUB.stat().st_size / 1024**2
    print(f"\nTamanho: {mb:.2f} MB")

    print("\n" + "=" * 60)
    if achados:
        print(f"REPROVADO — {len(achados)} achado(s):")
        for a in achados:
            print(f"  - {a}")
        sys.exit(1)
    print("APROVADO — nada identificável encontrado.")


if __name__ == "__main__":
    main()
