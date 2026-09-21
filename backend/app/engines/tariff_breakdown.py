def calc_fare(distance_km: float, slow_min: float, night: bool, tariff: dict, long_rate: dict | None = None) -> dict:
    base = float(tariff["start_price"])
    include = float(tariff["start_include_km"])
    per_km = float(tariff["per_km"])
    per_slow = float(tariff["per_slow_min"])
    night_f = float(tariff.get("night_factor", 1.0)) if night else 1.0
    dist = max(0.0, float(distance_km) - include)
    long_start = None
    long_per = None
    long_km = 0.0
    if long_rate:
        long_start = float(long_rate["start_km"])
        long_per = float(long_rate["per_km"])
        if long_start > include:
            long_km = max(0.0, float(distance_km) - long_start)
    normal_km = dist - long_km
    mile = normal_km * per_km
    long_mile = long_km * long_per if long_per is not None else 0.0
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
        "normal_km": round(normal_km, 2),
        "long_km": round(long_km, 2),
        "long_start_km": long_start,
        "long_per_km": long_per,
    }
