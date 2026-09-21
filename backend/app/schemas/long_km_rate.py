from pydantic import BaseModel, Field


class LongKmRateCreate(BaseModel):
    label: str
    start_km: float = Field(0, gt=0)
    per_km: float = Field(0, gt=0)
    active: bool = True


class LongKmRateUpdate(BaseModel):
    label: str
    start_km: float = Field(0, gt=0)
    per_km: float = Field(0, gt=0)
    active: bool = False
