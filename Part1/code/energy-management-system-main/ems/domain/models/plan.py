from dataclasses import dataclass, field
from typing import Optional

from ems.domain.models.types import MetricKey


@dataclass(slots=True)
class Plan:
    """Representation of a computed plan"""
    success: bool = True
    used_fallback: bool = False
    updates: dict[MetricKey, object] = field(default_factory=dict)
    reason: Optional[str] = None
