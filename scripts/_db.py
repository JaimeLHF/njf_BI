"""Conexao read-only com o Postgres do DW. Le credenciais do .env."""
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

PG = {
    "host": os.environ["PG_HOST"],
    "port": os.environ["PG_PORT"],
    "dbname": os.environ["PG_DB"],
    "user": os.environ["PG_USER"],
    "password": os.environ["PG_PASSWORD"],
}
SCHEMA = os.environ.get("PG_SCHEMA", "bi")


def connect():
    conn = psycopg2.connect(**PG)
    conn.set_session(readonly=True, autocommit=True)
    return conn


def query(sql, params=None):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        return cols, cur.fetchall()
