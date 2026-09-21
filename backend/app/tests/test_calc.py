from app.engines.night_compare import compare_day_night
from app.engines.tariff_breakdown import calc_fare

T = {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2}
LONG = {"id": 7, "start_km": 10, "per_km": 3.5}

def test_day_short():
    r = calc_fare(5, 2, False, T)
    assert r["total"] == 17.6
    assert r["mileage"] == 5.0

def test_night_long():
    r = calc_fare(18, 12, True, T)
    assert r["total"] == 69.72

def test_compare_delta():
    c = compare_day_night(18, 12, T)
    assert c["night_total"] > c["day_total"]

def test_no_rule_has_no_long_fee():
    r = calc_fare(18, 12, False, T)
    assert r["long_mileage"] == 0.0
    assert r["remote_billable_km"] == 0.0
    assert r["normal_billable_km"] == 15.0
    assert r["long_km_rule_id"] is None

def test_split_two_segments():
    # 含公里3内走起步；3~10走现行2.5；10以上走远程3.5。
    r = calc_fare(18, 12, False, T, LONG)
    assert r["normal_billable_km"] == 7.0
    assert r["remote_billable_km"] == 8.0
    assert r["mileage"] == 17.5
    assert r["long_mileage"] == 28.0
    assert r["slow_fee"] == 9.6
    assert r["total"] == 11 + 17.5 + 28 + 9.6
    assert r["long_km_rule_id"] == 7

def test_below_remote_start_long_fee_zero():
    r = calc_fare(8, 0, False, T, LONG)
    assert r["normal_billable_km"] == 5.0
    assert r["remote_billable_km"] == 0.0
    assert r["mileage"] == 12.5
    assert r["long_mileage"] == 0.0
    assert r["total"] == 23.5

def test_remote_boundary_is_exclusive():
    # 恰好等于远程起算公里时，远程段为 0。
    r = calc_fare(10, 0, False, T, LONG)
    assert r["normal_billable_km"] == 7.0
    assert r["remote_billable_km"] == 0.0
    assert r["long_mileage"] == 0.0

def test_slow_fee_keeps_current_rate_under_rule():
    a = calc_fare(20, 10, False, T, LONG)
    b = calc_fare(20, 10, False, T)
    assert a["slow_fee"] == b["slow_fee"] == 8.0

def test_night_applies_to_both_segments():
    day = calc_fare(18, 0, False, T, LONG)
    night = calc_fare(18, 0, True, T, LONG)
    assert night["mileage"] == round(day["mileage"] * 1.2, 2)
    assert night["long_mileage"] == round(day["long_mileage"] * 1.2, 2)
