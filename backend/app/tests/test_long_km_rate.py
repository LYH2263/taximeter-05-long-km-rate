import json
import pytest
from app import db, seed
from app.modules.long_km_rate import LongKmRateError
from app.services.taxi_service import TaxiService


@pytest.fixture
def svc(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    seed.init_db()
    with TaxiService() as s:
        yield s


def test_list_initially_empty(svc):
    assert svc.list_long_km_rates() == []


def test_create_active_rule_splits_fare(svc):
    rule = svc.create_long_km_rate("远程规则A", 10, 3.5, True)
    assert rule["active"] == 1
    r = svc.fare(18, 12, False, None, False)
    assert r["mileage"] == 17.5          # (10-3) * 2.5
    assert r["long_mileage"] == 28.0     # (18-10) * 3.5
    assert r["slow_fee"] == 9.6
    assert r["total"] == 66.1
    assert r["long_km_rule_id"] == rule["id"]


def test_only_one_active_conflict_names_both(svc):
    svc.create_long_km_rate("远程规则A", 10, 3.5, True)
    with pytest.raises(LongKmRateError) as ei:
        svc.create_long_km_rate("远程规则B", 12, 4.0, True)
    msg = str(ei.value)
    assert "远程规则A" in msg and "远程规则B" in msg
    assert svc.list_long_km_rates()[0]["active"] == 1  # 冲突不影响存量


def test_inactive_rule_can_coexist(svc):
    svc.create_long_km_rate("远程规则A", 10, 3.5, True)
    b = svc.create_long_km_rate("远程规则B", 12, 4.0, False)
    assert b["active"] == 0


def test_per_km_must_be_positive(svc):
    for bad in (0, -1):
        with pytest.raises(LongKmRateError, match="必须为正数"):
            svc.create_long_km_rate("x", 10, bad, False)


def test_start_km_must_exceed_included_km(svc):
    # 现行含公里为种子运价的 3 公里。
    with pytest.raises(LongKmRateError, match="必须大于现行含公里"):
        svc.create_long_km_rate("x", 3, 3.5, False)
    with pytest.raises(LongKmRateError, match="必须大于现行含公里"):
        svc.create_long_km_rate("x", 2.9, 3.5, False)


def test_label_required(svc):
    with pytest.raises(LongKmRateError, match="标识不能为空"):
        svc.create_long_km_rate("   ", 10, 3.5, False)


def test_update_to_active_conflicts(svc):
    svc.create_long_km_rate("远程规则A", 10, 3.5, True)
    b = svc.create_long_km_rate("远程规则B", 12, 4.0, False)
    with pytest.raises(LongKmRateError, match="远程规则A"):
        svc.update_long_km_rate(b["id"], "远程规则B", 12, 4.0, True)


def test_update_same_rule_staying_active_ok(svc):
    a = svc.create_long_km_rate("远程规则A", 10, 3.5, True)
    svc.update_long_km_rate(a["id"], "远程规则A改", 11, 4.2, True)
    assert svc.list_long_km_rates()[0]["label"] == "远程规则A改"


def test_update_missing_rule_404(svc):
    with pytest.raises(LongKmRateError, match="不存在"):
        svc.update_long_km_rate(999, "x", 10, 3.5, False)


def test_deactivate_restores_single_per_km(svc):
    rule = svc.create_long_km_rate("远程规则A", 10, 3.5, True)
    svc.deactivate_long_km_rate(rule["id"])
    r = svc.fare(18, 12, False, None, False)
    assert r["long_mileage"] == 0.0
    assert r["mileage"] == 37.5          # 全程 (18-3) * 2.5
    assert r["total"] == 58.1
    assert r["long_km_rule_id"] is None


def test_deactivate_missing_rule_404(svc):
    with pytest.raises(LongKmRateError, match="不存在"):
        svc.deactivate_long_km_rate(999)


def test_persisted_run_keeps_snapshot_when_price_changes(svc):
    a = svc.create_long_km_rate("远程规则A", 10, 3.5, True)
    old = svc.fare(20, 0, False, None, True)
    rid = old["run_id"]
    assert old["long_mileage"] == 35.0   # (20-10) * 3.5

    # 后来改远程单价，重算已变，但落库记录保留当时两段。
    svc.update_long_km_rate(a["id"], "远程规则A", 10, 9.9, True)
    snap = json.loads([x for x in svc.history() if x["id"] == rid][0]["result_json"])
    assert snap["long_per_km"] == 3.5
    assert snap["long_mileage"] == 35.0
    assert snap["mileage"] == old["mileage"]


def test_read_only_trial_does_not_persist(svc):
    svc.create_long_km_rate("远程规则A", 10, 3.5, True)
    before = len(svc.history())
    r = svc.fare(20, 5, False, None, False)
    assert r["run_id"] is None
    assert len(svc.history()) == before
