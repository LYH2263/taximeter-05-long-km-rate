from app.db import connect
from app.engines.night_compare import compare_day_night
from app.engines.tariff_breakdown import calc_fare
from app.modules.long_km_rate import LongKmRateError, ensure_single_active, validate_rule
from app.modules.long_km_rate import repository as long_km_repo
from app.repositories import runs, settings, tariff, trips

class TaxiService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_trips(self): return trips.list_all(self._c)
    def trip(self, tid): return trips.get(self._c, tid)
    def tariff(self): return tariff.get_active(self._c)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)

    # ---- 远程里程单价规则 ----
    def list_long_km_rates(self):
        return long_km_repo.list_all(self._c)

    def create_long_km_rate(self, label, start_km, per_km, active):
        t = tariff.get_active(self._c)
        validate_rule(label, start_km, per_km, t)
        if active:
            ensure_single_active(long_km_repo.get_active(self._c), label)
        return long_km_repo.insert(self._c, label.strip(), start_km, per_km, active)

    def update_long_km_rate(self, rate_id, label, start_km, per_km, active):
        existing = long_km_repo.get(self._c, rate_id)
        if not existing:
            raise LongKmRateError(f"远程里程规则不存在：id={rate_id}")
        t = tariff.get_active(self._c)
        validate_rule(label, start_km, per_km, t)
        if active:
            other = long_km_repo.get_active(self._c)
            if other and other["id"] != rate_id:
                ensure_single_active(other, label)
        return long_km_repo.update(self._c, rate_id, label.strip(), start_km, per_km, active)

    def deactivate_long_km_rate(self, rate_id):
        existing = long_km_repo.get(self._c, rate_id)
        if not existing:
            raise LongKmRateError(f"远程里程规则不存在：id={rate_id}")
        return long_km_repo.deactivate(self._c, rate_id)

    def _active_long_km(self):
        """启用中的远程规则；停用时为 None，全程恢复单一每公里。"""
        return long_km_repo.get_active(self._c)

    def fare(self, distance_km, slow_min, night, trip_id, persist):
        t = tariff.get_active(self._c)
        rule = self._active_long_km()
        r = calc_fare(distance_km, slow_min, night, t, rule)
        rid = runs.insert(self._c, "fare", {"distance_km": distance_km, "slow_min": slow_min, "night": night}, r, trip_id) if persist else None
        return {"run_id": rid, **r}

    def compare(self, distance_km, slow_min, persist):
        t = tariff.get_active(self._c)
        rule = self._active_long_km()
        r = compare_day_night(distance_km, slow_min, t, rule)
        rid = runs.insert(self._c, "compare", {"distance_km": distance_km, "slow_min": slow_min}, r, None) if persist else None
        return {"run_id": rid, **r}

    def dashboard(self):
        items = trips.list_all(self._c)
        clean = [x for x in items if "种子" not in x["label"]]
        dirty = [x for x in items if "种子" in x["label"]]
        return {"trip_count": len(items), "clean": len(clean), "dirty": len(dirty)}
