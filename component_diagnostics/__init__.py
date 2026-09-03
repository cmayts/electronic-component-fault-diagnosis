"""Electronic component fault diagnosis toolkit."""

from .models import DiagnosticResult, Status
from .diagnostics import diagnose

__all__ = ["DiagnosticResult", "Status", "diagnose"]
