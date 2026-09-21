"""远程里程单价模块。

规则:超出远程起算公里的部分改用远程每公里单价,含公里到远程起算之间仍走现行每公里。
全库只允许一条启用规则;停用后全程恢复单一每公里,远程里程费为零。
"""
import sqlite3

from app.repositories import tariff as tariff_repo

DDL = """
CREATE TABLE IF NOT EXISTS long_km_rate(
    id INTEGER PRIMARY KEY,
    start_km REAL NOT NULL,
    per_km REAL NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT
);
"""


class LongKmRateError(Exception):
    """远程里程规则错误基类。"""


class ValidationError(LongKmRateError):
    """规则取值非法(单价非正 / 起算公里不超过现行含公里)。"""


class ConflictError(LongKmRateError):
    """启用冲突:已存在另一条启用规则。"""


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.executescript(DDL)


def list_rules(conn: sqlite3.Connection) -> list[dict]:
    ensure_table(conn)
    return [dict(r) for r in conn.execute("SELECT * FROM long_km_rate ORDER BY id").fetchall()]


def get(conn: sqlite3.Connection, rule_id: int) -> dict | None:
    ensure_table(conn)
    row = conn.execute("SELECT * FROM long_km_rate WHERE id=?", (rule_id,)).fetchone()
    return dict(row) if row else None


def get_active(conn: sqlite3.Connection) -> dict | None:
    ensure_table(conn)
    row = conn.execute("SELECT * FROM long_km_rate WHERE active=1 ORDER BY id LIMIT 1").fetchone()
    return dict(row) if row else None


def _validate(conn: sqlite3.Connection, start_km: float, per_km: float) -> None:
    if per_km is None or not float(per_km) > 0:
        raise ValidationError("远程每公里单价必须为正")
    include = float(tariff_repo.get_active(conn).get("start_include_km", 0) or 0)
    if start_km is None or not float(start_km) > include:
        raise ValidationError(f"远程起算公里必须大于现行含公里 {include}")


def create_rule(conn: sqlite3.Connection, start_km: float, per_km: float) -> dict:
    ensure_table(conn)
    _validate(conn, start_km, per_km)
    current = get_active(conn)
    if current:
        raise ConflictError(
            f"远程规则冲突:已启用规则 #{current['id']}(起算 {current['start_km']}km),"
            f"拒绝再启用起算 {start_km}km 的新规则"
        )
    cur = conn.execute(
        "INSERT INTO long_km_rate(start_km,per_km,active,created_at) VALUES (?,?,1,datetime('now'))",
        (float(start_km), float(per_km)),
    )
    conn.commit()
    return get(conn, int(cur.lastrowid))


def update_rule(
    conn: sqlite3.Connection,
    rule_id: int,
    start_km: float | None = None,
    per_km: float | None = None,
    active: bool | None = None,
) -> dict | None:
    rule = get(conn, rule_id)
    if not rule:
        return None
    new_start = float(start_km) if start_km is not None else float(rule["start_km"])
    new_per = float(per_km) if per_km is not None else float(rule["per_km"])
    new_active = int(rule["active"]) if active is None else (1 if active else 0)
    _validate(conn, new_start, new_per)
    if new_active == 1:
        current = get_active(conn)
        if current and int(current["id"]) != int(rule_id):
            raise ConflictError(f"远程规则冲突:#{current['id']} 与 #{rule_id} 只允许一条启用")
    conn.execute(
        "UPDATE long_km_rate SET start_km=?, per_km=?, active=? WHERE id=?",
        (new_start, new_per, new_active, rule_id),
    )
    conn.commit()
    return get(conn, rule_id)


def deactivate(conn: sqlite3.Connection, rule_id: int) -> dict | None:
    rule = get(conn, rule_id)
    if not rule:
        return None
    conn.execute("UPDATE long_km_rate SET active=0 WHERE id=?", (rule_id,))
    conn.commit()
    return get(conn, rule_id)
