from app.engines.tariff_breakdown import calc_fare


def compare_day_night(distance_km: float, slow_min: float, tariff: dict, long_rate: dict | None = None) -> dict:
    day = calc_fare(distance_km, slow_min, False, tariff, long_rate)
    night = calc_fare(distance_km, slow_min, True, tariff, long_rate)
    return {
        "distance_km": day["distance_km"],
        "slow_min": day["slow_min"],
        "day_total": day["total"],
        "night_total": night["total"],
        "delta": round(night["total"] - day["total"], 2),
        "day": day,
        "night": night,
    }
