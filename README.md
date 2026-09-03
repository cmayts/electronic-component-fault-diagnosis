# Electronic Component Fault Diagnosis

A privacy-safe Python toolkit for evaluating electronic component measurements against nominal values, tolerances, and configurable test limits. It classifies resistor, capacitor, and diode test results and generates CSV, JSON, and standalone HTML reports.

## Features

- Resistor tolerance, open-circuit, and short-circuit checks
- Capacitor tolerance, open-circuit, short-circuit, and excessive-ESR checks
- Diode forward-voltage, reverse-leakage, open-circuit, and short-circuit checks
- Clear `PASS`, `WARNING`, and `FAIL` classifications
- CSV input with strict validation
- CSV, JSON, and visual HTML output
- Synthetic example measurements with no customer or production data
- Unit tests and GitHub Actions CI

## Installation

Python 3.10 or newer is recommended. The analyzer itself uses only the Python standard library.

```bash
git clone https://github.com/cmayts/electronic-component-fault-diagnosis.git
cd electronic-component-fault-diagnosis
python -m venv .venv
source .venv/bin/activate
```

## Usage

```bash
python -m component_diagnostics examples/synthetic_measurements.csv --output results
```

Generated files:

- `diagnostic_results.csv` — row-level classifications
- `diagnostic_summary.json` — machine-readable summary
- `diagnostic_report.html` — standalone visual report

The command exits with code `1` when at least one failed component is detected, which makes it suitable for automated test workflows.

## Input format

| Column | Required | Description |
| --- | --- | --- |
| `reference` | Yes | Component reference, such as `R1` or `D2` |
| `component_type` | Yes | `resistor`, `capacitor`, or `diode` |
| `nominal_value` | Resistor/capacitor | Nominal value in ohms or microfarads |
| `measured_value` | Resistor/capacitor | Measured value in the same unit |
| `tolerance_percent` | Resistor/capacitor | Allowed percentage deviation |
| `esr_ohm` | Optional capacitor | Measured equivalent series resistance |
| `max_esr_ohm` | Optional capacitor | ESR warning limit |
| `forward_voltage_v` | Diode | Measured forward voltage |
| `reverse_leakage_ua` | Optional diode | Measured reverse leakage current |

## Diagnostic scope

This project supports engineering screening and educational analysis. Results depend on the measurement method, test conditions, circuit topology, instrument accuracy, and component datasheets. Components should be isolated from surrounding circuitry when required, and safety procedures must be followed for energized or high-voltage equipment.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Privacy

Only synthetic example data is included. Raw production data, customer identifiers, equipment serial numbers, databases, environment files, and local paths are excluded through `.gitignore`.

## License

Released under the MIT License.
