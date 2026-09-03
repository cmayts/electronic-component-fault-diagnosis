from dataclasses import asdict, dataclass
from enum import Enum


class Status(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


@dataclass(frozen=True)
class DiagnosticResult:
    reference: str
    component_type: str
    status: Status
    fault: str
    deviation_percent: float | None
    message: str

    def as_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data
