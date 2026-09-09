"""
Compliance rule engine — TCS ka "compliance checks" / "compliance alerts" wala requirement.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, date


def _parse_amount(raw: str | None) -> float | None:
    if not raw or raw == "N/A":
        return None
    cleaned = re.sub(r"[^\d.]", "", raw)
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def _parse_date(raw: str | None) -> date | None:
    if not raw or raw == "N/A":
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d %B %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


COMPLIANCE_RULES = [
    {
        "rule_id": "R-INV-001",
        "applies_to": "Invoice",
        "severity": "High",
        "description": "Invoice total exceeds the approval threshold (50,000)",
        "check": lambda v: (_parse_amount(v.get("total_amount")) or 0) > 50000,
    },
    {
        "rule_id": "R-INV-002",
        "applies_to": "Invoice",
        "severity": "Medium",
        "description": "Invoice is missing a GST/tax figure",
        "check": lambda v: v.get("gst", "N/A") == "N/A",
    },
    {
        "rule_id": "R-PO-001",
        "applies_to": "Purchase Order",
        "severity": "High",
        "description": "Purchase order amount exceeds the approval threshold (100,000)",
        "check": lambda v: (_parse_amount(v.get("amount")) or 0) > 100000,
    },
    {
        "rule_id": "R-CON-001",
        "applies_to": "Contract",
        "severity": "Medium",
        "description": "Contract has no signature information on file",
        "check": lambda v: v.get("signatures", "N/A") == "N/A",
    },
    {
        "rule_id": "R-CON-002",
        "applies_to": "Contract",
        "severity": "High",
        "description": "Contract expiry date is in the past (renewal overdue)",
        "check": lambda v: (
            (d := _parse_date(v.get("expiry_date"))) is not None and d < date.today()
        ),
    },
    {
        "rule_id": "R-POL-001",
        "applies_to": "Policy",
        "severity": "High",
        "description": "Policy expiry date is in the past",
        "check": lambda v: (
            (d := _parse_date(v.get("policy_expiry_date"))) is not None and d < date.today()
        ),
    },
    {
        "rule_id": "R-CERT-001",
        "applies_to": "Certificate",
        "severity": "Low",
        "description": "Certificate has no certificate number captured",
        "check": lambda v: v.get("certificate_number", "N/A") == "N/A",
    },
]


def evaluate_compliance(document_type: str, values: dict) -> str:
    """Har applicable rule chalao, triggered alerts ki JSON string return karo."""
    alerts = []
    for rule in COMPLIANCE_RULES:
        if rule["applies_to"] != document_type:
            continue
        try:
            triggered = rule["check"](values)
        except Exception:
            triggered = False
        if triggered:
            alerts.append({
                "rule_id": rule["rule_id"],
                "severity": rule["severity"],
                "description": rule["description"],
            })
    return json.dumps(alerts)