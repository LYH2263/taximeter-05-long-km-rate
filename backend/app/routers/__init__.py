from fastapi import APIRouter
from app.routers import dashboard, fare, history, long_km_rate, settings, tariff, trips

api = APIRouter(prefix="/api")
for r in (dashboard, trips, tariff, long_km_rate, fare, history, settings):
    api.include_router(r.router)
