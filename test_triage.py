
import unittest

from triage import triage_logs, validate_report


VALID_REPORT = {
    "severity": "high",
    "summary": "Database requests are failing.",
    "likely_cause": "Database connection timeouts.",
    "evidence": ["ERROR Database connection failed"],
    "recommended_checks": ["Check database connectivity."],
}


class TestReportValidation(unittest.TestCase):

    def test_accepts_valid_report(self):
        report = validate_report(VALID_REPORT.copy())
        self.assertEqual(report["severity"], "high")

    def test_rejects_missing_field(self):
        report = VALID_REPORT.copy()
        del report["evidence"]

        with self.assertRaises(ValueError):
            validate_report(report)

    def test_rejects_invalid_severity(self):
        report = VALID_REPORT.copy()
        report["severity"] = "unknown"

        with self.assertRaises(ValueError):
            validate_report(report)

    def test_rejects_wrong_list_type(self):
        report = VALID_REPORT.copy()
        report["evidence"] = "This should be a list"

        with self.assertRaises(ValueError):
            validate_report(report)

    def test_rejects_empty_log(self):
        with self.assertRaises(ValueError):
            triage_logs("   ")


if __name__ == "__main__":
    unittest.main()
