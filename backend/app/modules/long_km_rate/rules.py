class LongKmRateError(Exception):
    """远程里程规则校验失败；message 直接面向用户。"""


def validate_rule(label: str, start_km: float, per_km: float, tariff: dict) -> None:
    """校验单条规则自身合法性：标识非空、单价为正、远程起算大于现行含公里。"""
    if not (label and str(label).strip()):
        raise LongKmRateError("规则标识不能为空")
    if per_km is None or float(per_km) <= 0:
        raise LongKmRateError(f"远程每公里单价必须为正数，当前为 {per_km}")
    include = float((tariff or {}).get("start_include_km", 0))
    if start_km is None or float(start_km) <= include:
        raise LongKmRateError(f"远程起算公里({start_km})必须大于现行含公里({include})")


def ensure_single_active(active_row: dict | None, candidate_label: str) -> None:
    """只允许一条启用；冲突时拒绝并点名两条标识。"""
    if active_row:
        raise LongKmRateError(
            f"只允许一条启用规则：「{candidate_label}」与已启用的「{active_row['label']}」冲突，"
            f"请先停用「{active_row['label']}」"
        )
