from collections.abc import Mapping

from .models import DiagnosticResult, Status


def _number(row: Mapping[str, str], name: str, required: bool = True) -> float | None:
    raw = row.get(name, "").strip()
    if not raw:
        if required:
            raise ValueError(f"{name} is required")
        return None
    try:
        return float(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be numeric") from error


def _result(row, status, fault, message, deviation=None):
    return DiagnosticResult(
        reference=row.get("reference", "").strip(),
        component_type=row.get("component_type", "").strip().lower(),
        status=status,
        fault=fault,
        deviation_percent=round(deviation, 2) if deviation is not None else None,
        message=message,
    )


def diagnose_resistor(row: Mapping[str, str]) -> DiagnosticResult:
    nominal = _number(row, "nominal_value")
    measured = _number(row, "measured_value")
    tolerance = _number(row, "tolerance_percent")
    assert nominal is not None and measured is not None and tolerance is not None
    if nominal <= 0 or tolerance < 0:
        raise ValueError("nominal_value must be positive and tolerance_percent non-negative")
    if measured < max(0.5, nominal * 0.001):
        return _result(row, Status.FAIL, "SHORT_CIRCUIT", "Measured resistance indicates a short circuit.")
    if measured > nominal * 100:
        return _result(row, Status.FAIL, "OPEN_CIRCUIT", "Measured resistance indicates an open circuit.")
    deviation = (measured - nominal) / nominal * 100
    if abs(deviation) > tolerance:
        return _result(row, Status.FAIL, "OUT_OF_TOLERANCE", "Resistance is outside the specified tolerance.", deviation)
    return _result(row, Status.PASS, "NONE", "Resistance is within tolerance.", deviation)


def diagnose_capacitor(row: Mapping[str, str]) -> DiagnosticResult:
    nominal = _number(row, "nominal_value")
    measured = _number(row, "measured_value")
    tolerance = _number(row, "tolerance_percent")
    assert nominal is not None and measured is not None and tolerance is not None
    if nominal <= 0 or tolerance < 0:
        raise ValueError("nominal_value must be positive and tolerance_percent non-negative")
    if measured <= nominal * 0.001:
        return _result(row, Status.FAIL, "SHORT_OR_NO_CAPACITANCE", "Measured capacitance is effectively zero.")
    if measured > nominal * 100:
        return _result(row, Status.FAIL, "INVALID_OR_SHORTED", "Measured capacitance is implausibly high.")
    deviation = (measured - nominal) / nominal * 100
    if abs(deviation) > tolerance:
        return _result(row, Status.FAIL, "OUT_OF_TOLERANCE", "Capacitance is outside the specified tolerance.", deviation)
    esr = _number(row, "esr_ohm", required=False)
    max_esr = _number(row, "max_esr_ohm", required=False)
    if esr is not None and max_esr is not None and esr > max_esr:
        return _result(row, Status.WARNING, "HIGH_ESR", "Capacitance passes, but ESR exceeds the configured limit.", deviation)
    return _result(row, Status.PASS, "NONE", "Capacitance is within tolerance.", deviation)


def diagnose_diode(row: Mapping[str, str]) -> DiagnosticResult:
    forward = _number(row, "forward_voltage_v")
    leakage = _number(row, "reverse_leakage_ua", required=False)
    assert forward is not None
    if forward < 0.1:
        return _result(row, Status.FAIL, "SHORT_CIRCUIT", "Forward voltage indicates a shorted diode.")
    if forward > 2.5:
        return _result(row, Status.FAIL, "OPEN_CIRCUIT", "Forward voltage indicates an open or incorrectly connected diode.")
    if not 0.45 <= forward <= 1.2:
        return _result(row, Status.WARNING, "ABNORMAL_FORWARD_VOLTAGE", "Forward voltage is outside the typical silicon/LED screening range.")
    if leakage is not None and leakage > 10:
        return _result(row, Status.WARNING, "HIGH_REVERSE_LEAKAGE", "Reverse leakage exceeds the default screening limit.")
    return _result(row, Status.PASS, "NONE", "Diode measurements pass the screening limits.")


def diagnose(row: Mapping[str, str]) -> DiagnosticResult:
    reference = row.get("reference", "").strip()
    if not reference:
        raise ValueError("reference is required")
    kind = row.get("component_type", "").strip().lower()
    handlers = {"resistor": diagnose_resistor, "capacitor": diagnose_capacitor, "diode": diagnose_diode}
    if kind not in handlers:
        raise ValueError("component_type must be resistor, capacitor, or diode")
    return handlers[kind](row)
