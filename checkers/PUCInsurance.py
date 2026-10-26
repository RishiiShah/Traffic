"""
RTO lookup + compliance (PUC / Insurance) checks.

Reads the RapidAPI credentials from the environment:
    X_RAPIDAPI_KEY
    X_RAPIDAPI_HOST

OCR'd license plates are written to `ocr results/ocr_results.txt`.
"""
import os
from enum import Enum
from datetime import datetime

import requests

# How long to wait on the RTO API before giving up (seconds).
RTO_API_TIMEOUT = 15


class ComplianceStatus(Enum):
    """Explicit result of a document (PUC / Insurance) check.

    Keeping these states distinct avoids treating "we don't know" the same as
    "expired" -- only VALID/EXPIRED should ever drive a penalty decision.
    """
    VALID = "valid"       # document found and not past its expiry date
    EXPIRED = "expired"   # document found and past its expiry date
    UNKNOWN = "unknown"   # no date available / vehicle not found
    ERROR = "error"       # lookup failed (network, parsing, etc.)


def details(license: str) -> dict:
    """Fetch RTO vehicle information for a plate.

    Returns the parsed JSON dict on success, or an empty dict on any failure
    so callers can fall back to an UNKNOWN compliance state rather than crash.
    """
    api_key = os.getenv("X_RAPIDAPI_KEY")
    api_host = os.getenv("X_RAPIDAPI_HOST")
    if not api_key or not api_host:
        # No credentials configured: behave as "lookup unavailable".
        return {}

    url = "https://rto-vehicle-information-india.p.rapidapi.com/getVehicleInfo"
    payload = {
        "vehicle_no": license,
        "consent": "Y",
        "consent_text": "I hereby give my consent for Eccentric Labs API to fetch my information",
    }
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host,
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(
            url, json=payload, headers=headers, timeout=RTO_API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:  # network error, timeout, bad JSON, etc.
        print(f"[!] RTO lookup failed for '{license}': {e}")
        return {}


def check_expiry(date_str: str) -> ComplianceStatus:
    """Classify a document expiry date into an explicit ComplianceStatus.

    `date_str` is expected in 'DD-MMM-YYYY' format (e.g. '05-Jun-2024').
    An empty/missing string -> UNKNOWN. An unparseable string -> ERROR.
    """
    if not date_str:
        return ComplianceStatus.UNKNOWN
    try:
        expiry = datetime.strptime(date_str, "%d-%b-%Y")
    except (ValueError, TypeError):
        return ComplianceStatus.ERROR
    return (
        ComplianceStatus.VALID
        if expiry >= datetime.today()
        else ComplianceStatus.EXPIRED
    )


def convert_check(date_str: str) -> bool:
    """Backwards-compatible boolean helper.

    Returns True only when the document is confirmed VALID. Any non-valid
    state (expired, unknown, error) returns False, so callers that have not
    yet migrated to ComplianceStatus keep their previous behaviour.
    Prefer `check_expiry` for new code.
    """
    return check_expiry(date_str) == ComplianceStatus.VALID
