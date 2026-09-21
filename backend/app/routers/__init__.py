from fastapi import APIRouter
from app.routers import dashboard, fare, history, long_km_rate, settings, tariff, trips

api = APIRouter(prefix="/api")
for r in (dashboard, trips, tariff, fare, history, settings, long_km_rate):
    api.include_router(r.router)
