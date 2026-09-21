from fastapi import APIRouter, HTTPException

from app.modules import long_km_rate
from app.schemas.long_km_rate import LongKmRateCreate, LongKmRateUpdate
from app.services.taxi_service import TaxiService

router = APIRouter()


def _http(e: long_km_rate.LongKmRateError) -> HTTPException:
    code = 409 if isinstance(e, long_km_rate.ConflictError) else 400
    return HTTPException(code, str(e))


@router.get("/long-km-rate")
def list_rules():
    with TaxiService() as s:
        return {"items": s.long_km_rates()}


@router.post("/long-km-rate", status_code=201)
def create_rule(body: LongKmRateCreate):
    with TaxiService() as s:
        try:
            return s.create_long_km_rate(body.start_km, body.per_km)
        except long_km_rate.LongKmRateError as e:
            raise _http(e)


@router.put("/long-km-rate/{rule_id}")
def update_rule(rule_id: int, body: LongKmRateUpdate):
    with TaxiService() as s:
        try:
            rule = s.update_long_km_rate(rule_id, body.start_km, body.per_km, body.active)
        except long_km_rate.LongKmRateError as e:
            raise _http(e)
        if not rule:
            raise HTTPException(404)
        return rule


@router.post("/long-km-rate/{rule_id}/deactivate")
def deactivate_rule(rule_id: int):
    with TaxiService() as s:
        rule = s.deactivate_long_km_rate(rule_id)
        if not rule:
            raise HTTPException(404)
        return rule
