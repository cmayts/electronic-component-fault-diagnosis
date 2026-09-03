import unittest

from component_diagnostics import Status, diagnose


class DiagnosticTests(unittest.TestCase):
    def test_resistor_passes_within_tolerance(self):
        result = diagnose({"reference":"R1","component_type":"resistor","nominal_value":"1000","measured_value":"1020","tolerance_percent":"5"})
        self.assertEqual(result.status, Status.PASS)

    def test_resistor_short_is_detected(self):
        result = diagnose({"reference":"R2","component_type":"resistor","nominal_value":"10000","measured_value":"0.2","tolerance_percent":"5"})
        self.assertEqual(result.fault, "SHORT_CIRCUIT")

    def test_capacitor_high_esr_warns(self):
        result = diagnose({"reference":"C1","component_type":"capacitor","nominal_value":"100","measured_value":"98","tolerance_percent":"10","esr_ohm":"2","max_esr_ohm":"0.5"})
        self.assertEqual(result.status, Status.WARNING)
        self.assertEqual(result.fault, "HIGH_ESR")

    def test_diode_open_is_detected(self):
        result = diagnose({"reference":"D1","component_type":"diode","forward_voltage_v":"3.2"})
        self.assertEqual(result.fault, "OPEN_CIRCUIT")

    def test_invalid_type_fails_validation(self):
        with self.assertRaises(ValueError):
            diagnose({"reference":"Q1","component_type":"transistor"})


if __name__ == "__main__":
    unittest.main()
