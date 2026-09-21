import sqlite3

import pytest

from app.engines.tariff_breakdown import calc_fare
from app.modules import long_km_rate

T = {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2}
LR = {"start_km": 10, "per_km": 4.0}


# ---------- 引擎:两段里程拆解 ----------

def test_long_segments_split():
    r = calc_fare(12, 0, False, T, LR)
    assert r["mileage"] == 17.5       # (10-3)km * 2.5
    assert r["long_mileage"] == 8.0   # (12-10)km * 4.0
    assert r["normal_km"] == 7.0
    assert r["long_km"] == 2.0
    assert r["total"] == 36.5         # 11 + 17.5 + 8 + 0


def test_below_threshold_no_long_fee():
    r = calc_fare(8, 0, False, T, LR)
    assert r["long_mileage"] == 0
    assert r["mileage"] == 12.5       # (8-3)km * 2.5
    assert r["total"] == 23.5


def test_no_rule_single_rate():
    r = calc_fare(18, 12, False, T)
    assert r["long_mileage"] == 0
    assert r["long_km"] == 0
    assert r["mileage"] == 37.5       # (18-3)km * 2.5


def test_long_segments_night_factor():
    r = calc_fare(12, 0, True, T, LR)
    assert r["total"] == round(36.5 * 1.2, 2)
    assert r["long_mileage"] == round(8.0 * 1.2, 2)


def test_slow_fee_unchanged_with_long_rate():
    r = calc_fare(12, 5, False, T, LR)
    assert r["slow_fee"] == 4.0       # 5min * 0.8,仍按现行低速单价


# ---------- 模块:规则落库与校验 ----------

@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE tariff(id INTEGER PRIMARY KEY, start_price REAL, start_include_km REAL, per_km REAL, per_slow_min REAL, night_factor REAL)")
    c.execute("INSERT INTO tariff VALUES (1,11,3,2.5,0.8,1.2)")
    long_km_rate.ensure_table(c)
    yield c
    c.close()


def test_create_list_get_active(conn):
    a = long_km_rate.create_rule(conn, 10, 4.0)
    assert a["active"] == 1
    assert long_km_rate.get_active(conn)["id"] == a["id"]
    assert [r["id"] for r in long_km_rate.list_rules(conn)] == [a["id"]]


def test_create_conflict_names_both(conn):
    a = long_km_rate.create_rule(conn, 10, 4.0)
    with pytest.raises(long_km_rate.ConflictError) as e:
        long_km_rate.create_rule(conn, 12, 5.0)
    msg = str(e.value)
    assert f"#{a['id']}" in msg and "12" in msg
    assert len(long_km_rate.list_rules(conn)) == 1   # 冲突拒绝,未落库


def test_start_km_must_exceed_include(conn):
    with pytest.raises(long_km_rate.ValidationError):
        long_km_rate.create_rule(conn, 3, 4.0)       # 等于含公里也拒绝
    with pytest.raises(long_km_rate.ValidationError):
        long_km_rate.create_rule(conn, 2, 4.0)


def test_per_km_must_be_positive(conn):
    with pytest.raises(long_km_rate.ValidationError):
        long_km_rate.create_rule(conn, 10, 0)
    with pytest.raises(long_km_rate.ValidationError):
        long_km_rate.create_rule(conn, 10, -1.5)


def test_deactivate_then_create_again(conn):
    a = long_km_rate.create_rule(conn, 10, 4.0)
    long_km_rate.deactivate(conn, a["id"])
    assert long_km_rate.get_active(conn) is None
    b = long_km_rate.create_rule(conn, 12, 5.0)      # 停用后可再建
    assert b["active"] == 1


def test_update_values_and_validation(conn):
    a = long_km_rate.create_rule(conn, 10, 4.0)
    b = long_km_rate.update_rule(conn, a["id"], start_km=15, per_km=6.0)
    assert b["start_km"] == 15 and b["per_km"] == 6.0
    with pytest.raises(long_km_rate.ValidationError):
        long_km_rate.update_rule(conn, a["id"], start_km=2)
    with pytest.raises(long_km_rate.ValidationError):
        long_km_rate.update_rule(conn, a["id"], per_km=0)


def test_reactivate_conflict_names_both_ids(conn):
    a = long_km_rate.create_rule(conn, 10, 4.0)
    long_km_rate.deactivate(conn, a["id"])
    b = long_km_rate.create_rule(conn, 12, 5.0)
    with pytest.raises(long_km_rate.ConflictError) as e:
        long_km_rate.update_rule(conn, a["id"], active=True)
    msg = str(e.value)
    assert f"#{a['id']}" in msg and f"#{b['id']}" in msg


def test_update_missing_rule_returns_none(conn):
    assert long_km_rate.update_rule(conn, 999, start_km=10) is None
    assert long_km_rate.deactivate(conn, 999) is None
