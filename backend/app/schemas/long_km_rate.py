from pydantic import BaseModel

class LongKmRateCreate(BaseModel):
    start_km: float
    per_km: float

class LongKmRateUpdate(BaseModel):
    start_km: float | None = None
    per_km: float | None = None
    active: bool | None = None
