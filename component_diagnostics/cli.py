import argparse
from pathlib import Path

from .io import analyze_csv, write_reports
from .models import Status


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose common electronic component faults")
    parser.add_argument("input", type=Path, help="CSV measurement file")
    parser.add_argument("--output", type=Path, default=Path("results"), help="Report directory")
    args = parser.parse_args()
    results = analyze_csv(args.input)
    write_reports(results, args.output)
    for item in results:
        print(f"{item.reference:8} {item.status.value:7} {item.fault}")
    failed = sum(item.status is Status.FAIL for item in results)
    print(f"\nAnalyzed: {len(results)} | Failed: {failed} | Reports: {args.output}")
    raise SystemExit(1 if failed else 0)
