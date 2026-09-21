def calc_fare(distance_km: float, slow_min: float, night: bool, tariff: dict, long_km: dict | None = None) -> dict:
    base = float(tariff["start_price"])
    include = float(tariff["start_include_km"])
    per_km = float(tariff["per_km"])
    per_slow = float(tariff["per_slow_min"])
    night_f = float(tariff.get("night_factor", 1.0)) if night else 1.0

    # 含公里内仍走起步；超出部分默认全程走现行每公里。
    billable_km = max(0.0, float(distance_km) - include)
    normal_km = billable_km
    remote_km = 0.0
    remote_rate = 0.0
    remote_start = None
    if long_km:
        # 含公里~远程起算走现行单价，超出远程起算改走远程单价。
        remote_start = float(long_km["start_km"])
        remote_rate = float(long_km["per_km"])
        normal_km = max(0.0, min(float(distance_km), remote_start) - include)
        remote_km = max(0.0, float(distance_km) - remote_start)

    mile = normal_km * per_km
    long_mile = remote_km * remote_rate
    slow = float(slow_min) * per_slow
    sub = base + mile + long_mile + slow
    return {
        "distance_km": round(float(distance_km), 2),
        "slow_min": round(float(slow_min), 1),
        "night": night,
        "night_factor": night_f,
        "start": round(base * night_f, 2),
        "mileage": round(mile * night_f, 2),
        "long_mileage": round(long_mile * night_f, 2),
        "slow_fee": round(slow * night_f, 2),
        "total": round(sub * night_f, 2),
        "long_km_rule_id": long_km["id"] if long_km else None,
        "long_start_km": round(remote_start, 2) if remote_start is not None else None,
        "long_per_km": remote_rate if long_km else None,
        "normal_billable_km": round(normal_km, 2),
        "remote_billable_km": round(remote_km, 2),
    }
