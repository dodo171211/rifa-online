"""Operacoes do banco da rifa (SQLite)."""
import os
import sqlite3
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
SCHEMA_PATH = BASE / "schema.sql"


def get_db_path() -> Path:
    """Caminho do banco (local ou pasta persistente na nuvem)."""
    env = os.environ.get("RIFA_DB_PATH")
    if env:
        path = Path(env)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    return BASE / "rifa.db"

NUMEROS_PRE_RESERVADOS = [
    3, 6, 10, 122, 146, 166, 190, 251, 257, 295, 354, 372, 379, 385, 406, 438,
    451, 506, 528, 604, 629, 652, 668, 685, 698,
]


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    if not db_path.exists():
        init_database()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = sqlite3.connect(get_db_path())
    try:
        conn.executescript(schema)
        conn.executemany(
            "INSERT OR IGNORE INTO numeros_rifa (numero, status) VALUES (?, 'disponivel')",
            [(n,) for n in range(1, 701)],
        )
        reservados = conn.execute(
            "SELECT COUNT(*) FROM numeros_rifa WHERE status = 'reservado'"
        ).fetchone()[0]
        if reservados == 0 and NUMEROS_PRE_RESERVADOS:
            cur = conn.execute(
                "INSERT INTO compradores (nome, telefone, email) VALUES (?, ?, ?)",
                ("Reserva anterior", "-", None),
            )
            comprador_id = cur.lastrowid
            for numero in NUMEROS_PRE_RESERVADOS:
                conn.execute(
                    """
                    UPDATE numeros_rifa
                    SET status = 'reservado', comprador_id = ?,
                        reservado_em = datetime('now', 'localtime')
                    WHERE numero = ? AND status = 'disponivel'
                    """,
                    (comprador_id, numero),
                )
        conn.commit()
    finally:
        conn.close()


def get_estatisticas() -> dict[str, Any]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT numero FROM numeros_rifa WHERE status = 'reservado' ORDER BY numero"
        ).fetchall()
        reservados = [r["numero"] for r in rows]
        total = 700
        return {
            "total": total,
            "reservados": reservados,
            "reservados_count": len(reservados),
            "disponiveis": total - len(reservados),
        }
    finally:
        conn.close()


def reservar_numeros(
    nome: str, telefone: str, numeros: list[int], email: str | None = None
) -> dict[str, Any]:
    if not nome.strip():
        raise ValueError("Nome e obrigatorio.")
    if not telefone.strip():
        raise ValueError("Telefone e obrigatorio.")
    if not numeros:
        raise ValueError("Informe pelo menos um numero.")

    unicos = sorted(set(int(n) for n in numeros))
    for n in unicos:
        if n < 1 or n > 700:
            raise ValueError(f"Numero invalido: {n}. Use de 1 a 700.")

    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        placeholders = ",".join("?" * len(unicos))
        rows = conn.execute(
            f"SELECT numero, status FROM numeros_rifa WHERE numero IN ({placeholders})",
            unicos,
        ).fetchall()

        if len(rows) != len(unicos):
            raise ValueError("Algum numero nao existe no banco.")

        ocupados = [r["numero"] for r in rows if r["status"] != "disponivel"]
        if ocupados:
            raise ValueError(
                f"Numeros ja escolhidos por outra pessoa: {', '.join(map(str, ocupados))}"
            )

        cur = conn.execute(
            "INSERT INTO compradores (nome, telefone, email) VALUES (?, ?, ?)",
            (nome.strip(), telefone.strip(), (email or "").strip() or None),
        )
        comprador_id = cur.lastrowid

        for numero in unicos:
            updated = conn.execute(
                """
                UPDATE numeros_rifa
                SET status = 'reservado', comprador_id = ?,
                    reservado_em = datetime('now', 'localtime')
                WHERE numero = ? AND status = 'disponivel'
                """,
                (comprador_id, numero),
            ).rowcount
            if updated != 1:
                raise ValueError(f"Numero {numero} foi reservado por outro usuario agora.")

        conn.commit()
        return {
            "comprador_id": comprador_id,
            "nome": nome.strip(),
            "telefone": telefone.strip(),
            "email": (email or "").strip() or None,
            "numeros": unicos,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def listar_compras() -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM vw_compras").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
