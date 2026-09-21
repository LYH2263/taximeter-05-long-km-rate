"""远程里程单价模块：超出远程起算公里的部分改用远程每公里单价，可落库。"""
from app.modules.long_km_rate.repository import (
    deactivate,
    get,
    get_active,
    init_table,
    insert,
    list_all,
    update,
)
from app.modules.long_km_rate.rules import LongKmRateError, ensure_single_active, validate_rule

__all__ = [
    "LongKmRateError",
    "deactivate",
    "ensure_single_active",
    "get",
    "get_active",
    "init_table",
    "insert",
    "list_all",
    "update",
    "validate_rule",
]
