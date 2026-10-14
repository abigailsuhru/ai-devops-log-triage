
import argparse
import json
import sys
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

REQUIRED_FIELDS = {
    "severity",
    "summary",
    "likely_cause",
    "evidence",
    "recommended_checks",
}

ALLOWED_SEVERITIES = {"low", "medium", "high", "critical"}


def validate_report(report):
    """Check the structure and basic types of an AI-generated report."""
    if not isinstance(report, dict):
        raise ValueError("Report must be a JSON object")

    missing = REQUIRED_FIELDS - report.keys()
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")

    if report["severity"] not in ALLOWED_SEVERITIES:
        raise ValueError("Invalid severity")

    for field in ("summary", "likely_cause"):
        if not isinstance(report[field], str) or not report[field].strip():
            raise ValueError(f"{field} must be a non-empty string")

    for field in ("evidence", "recommended_checks"):
        if not isinstance(report[field], list):
            raise ValueError(f"{field} must be a list")
        if not all(isinstance(item, str) for item in report[field]):
            raise ValueError(f"{field} must contain only strings")

    return report


def triage_logs(log_text):
    """Ask a local LLM to analyse logs and return a validated report."""
    if not log_text.strip():
        raise ValueError("Log file is empty")

    prompt = f"""
You are a cautious DevOps incident triage assistant.

Analyse the log excerpt below. Use only evidence in the logs.
Do not invent infrastructure details or claim a root cause is confirmed.
Distinguish observations from hypotheses.
Do not execute commands or recommend exposing secrets.

Return ONLY a valid JSON object with exactly these fields:
{{
  "severity": "low|medium|high|critical",
  "summary": "Short incident summary",
  "likely_cause": "Evidence-based hypothesis",
  "evidence": ["Relevant log lines or observations"],
  "recommended_checks": ["Safe investigation step"]
}}

Logs begin:
---LOGS---
{log_text}
---END LOGS---
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }

    request = Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))

    report = json.loads(result["response"])
    return validate_report(report)


def main():
    parser = argparse.ArgumentParser(
        description="Summarise application logs with a local LLM."
    )
    parser.add_argument("logfile", help="Path to a text log file")
    args = parser.parse_args()

    try:
        log_text = Path(args.logfile).read_text(encoding="utf-8")
        report = triage_logs(log_text)
        print(json.dumps(report, indent=2, ensure_ascii=False))
    except (OSError, ValueError, KeyError, json.JSONDecodeError,
            HTTPError, URLError, TimeoutError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
