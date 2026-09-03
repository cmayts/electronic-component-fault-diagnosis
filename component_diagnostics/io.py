import csv
import html
import json
from collections import Counter
from pathlib import Path

from .diagnostics import diagnose
from .models import DiagnosticResult, Status


def analyze_csv(path: Path) -> list[DiagnosticResult]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            raise ValueError("Input file has no header")
        results = []
        for line, row in enumerate(reader, start=2):
            try:
                results.append(diagnose(row))
            except ValueError as error:
                reference = row.get("reference", "").strip() or f"line-{line}"
                results.append(DiagnosticResult(reference, row.get("component_type", "").strip(), Status.FAIL, "INVALID_INPUT", None, str(error)))
        return results


def write_reports(results: list[DiagnosticResult], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    rows = [item.as_dict() for item in results]
    with (output / "diagnostic_results.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=rows[0].keys() if rows else DiagnosticResult.__dataclass_fields__.keys())
        writer.writeheader()
        writer.writerows(rows)
    counts = Counter(item.status.value for item in results)
    summary = {"total": len(results), "counts": dict(counts), "results": rows}
    (output / "diagnostic_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    cards = "".join(f'<div class="card {key.lower()}"><strong>{value}</strong><span>{key}</span></div>' for key, value in (("PASS", counts["PASS"]), ("WARNING", counts["WARNING"]), ("FAIL", counts["FAIL"])))
    table_rows = "".join(f"<tr><td>{html.escape(r.reference)}</td><td>{html.escape(r.component_type)}</td><td><span class='badge {r.status.value.lower()}'>{r.status.value}</span></td><td>{html.escape(r.fault)}</td><td>{html.escape(r.message)}</td></tr>" for r in results)
    report = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Component Diagnostic Report</title><style>body{{font:15px system-ui;margin:0;background:#f4f7fb;color:#182230}}main{{max-width:1100px;margin:auto;padding:40px 20px}}h1{{margin-bottom:4px}}.summary{{display:flex;gap:16px;margin:28px 0}}.card{{background:white;border-radius:12px;padding:20px;min-width:120px;box-shadow:0 3px 16px #18223012}}.card strong{{display:block;font-size:30px}}.card span{{font-size:12px;letter-spacing:.08em}}.pass strong{{color:#16803c}}.warning strong{{color:#a15c00}}.fail strong{{color:#c22b2b}}table{{width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #e8edf3}}th{{background:#172a46;color:white}}.badge{{font-weight:700;font-size:12px}}.badge.pass{{color:#16803c}}.badge.warning{{color:#a15c00}}.badge.fail{{color:#c22b2b}}@media(max-width:700px){{.summary{{flex-wrap:wrap}}table{{font-size:12px}}}}</style></head><body><main><h1>Electronic Component Diagnostic Report</h1><p>Measurement-based screening summary</p><section class='summary'>{cards}</section><table><thead><tr><th>Reference</th><th>Type</th><th>Status</th><th>Finding</th><th>Details</th></tr></thead><tbody>{table_rows}</tbody></table></main></body></html>"""
    (output / "diagnostic_report.html").write_text(report, encoding="utf-8")
