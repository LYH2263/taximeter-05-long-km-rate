import sqlite3
from datetime import datetime, timezone

DDL = """
CREATE TABLE IF NOT EXISTS long_km_rate(
    id INTEGER PRIMARY KEY,
    label TEXT NOT NULL,
    start_km REAL NOT NULL,
    per_km REAL NOT NULL,
    active INTEGER NOT NULL DEFAULT 0,
    created_at TEXT
);
"""


def init_table(conn: sqlite3.Connection) -> None:
    conn.execute(DDL)


def list_all(conn: sqlite3.Connection) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT * FROM long_km_rate ORDER BY id").fetchall()]


def get(conn: sqlite3.Connection, rate_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM long_km_rate WHERE id=?", (rate_id,)).fetchone()
    return dict(row) if row else None


def get_active(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute("SELECT * FROM long_km_rate WHERE active=1 ORDER BY id LIMIT 1").fetchone()
    return dict(row) if row else None


def insert(conn: sqlite3.Connection, label: str, start_km: float, per_km: float, active: bool) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO long_km_rate(label,start_km,per_km,active,created_at) VALUES (?,?,?,?,?)",
        (label, float(start_km), float(per_km), 1 if active else 0, now),
    )
    conn.commit()
    return get(conn, int(cur.lastrowid))


def update(conn: sqlite3.Connection, rate_id: int, label: str, start_km: float, per_km: float, active: bool) -> dict | None:
    conn.execute(
        "UPDATE long_km_rate SET label=?, start_km=?, per_km=?, active=? WHERE id=?",
        (label, float(start_km), float(per_km), 1 if active else 0, rate_id),
    )
    conn.commit()
    return get(conn, rate_id)


def deactivate(conn: sqlite3.Connection, rate_id: int) -> dict | None:
    conn.execute("UPDATE long_km_rate SET active=0 WHERE id=?", (rate_id,))
    conn.commit()
    return get(conn, rate_id)
