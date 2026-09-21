from fastapi import APIRouter, HTTPException
from app.modules.long_km_rate import LongKmRateError
from app.schemas.long_km_rate import LongKmRateCreate, LongKmRateUpdate
from app.services.taxi_service import TaxiService

router = APIRouter()


@router.get("/long-km-rates")
def list_rates():
    with TaxiService() as s:
        return {"items": s.list_long_km_rates()}


@router.post("/long-km-rates", status_code=201)
def create_rate(body: LongKmRateCreate):
    try:
        with TaxiService() as s:
            return s.create_long_km_rate(body.label, body.start_km, body.per_km, body.active)
    except LongKmRateError as e:
        raise HTTPException(400, str(e))


@router.put("/long-km-rates/{rate_id}")
def update_rate(rate_id: int, body: LongKmRateUpdate):
    try:
        with TaxiService() as s:
            return s.update_long_km_rate(rate_id, body.label, body.start_km, body.per_km, body.active)
    except LongKmRateError as e:
        raise HTTPException(400, str(e))


@router.post("/long-km-rates/{rate_id}/deactivate")
def deactivate_rate(rate_id: int):
    try:
        with TaxiService() as s:
            return s.deactivate_long_km_rate(rate_id)
    except LongKmRateError as e:
        raise HTTPException(404, str(e))
