from dataclasses import dataclass
from typing import Optional


@dataclass
class Alert:
    """
    Base alert
    """
    field: str

    def flux(self) -> str:
        raise NotImplementedError

    def message(self) -> str:
        raise NotImplementedError


@dataclass
class RangeAlert(Alert):
    """
    Alert that is triggered when a value is outside a range
    """

    min: Optional[float]
    max: Optional[float]

    def __post_init__(self):
        if self.min is None and self.max is None:
            raise ValueError("At least one of min or max must be set")

    def flux(self) -> str:
        crit = []
        if self.min is not None:
            crit.append(f"r.value < {self.min}")
        if self.max is not None:
            crit.append(f"r.value > {self.max}")
        return " or ".join(crit)

    def message(self) -> str:
        bounds = [
            self.min if self.min is not None else "-inf",
            self.max if self.max is not None else "inf",
        ]
        return f"has value `{self.field}` ${{ if r._level == \"crit\" then \"out of\" else \"in\" }} range [{bounds[0]}, {bounds[1]}]: ${{ r.value }}"
