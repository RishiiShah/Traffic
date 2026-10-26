"""Tests for the PUC/Insurance compliance checker.

These run fully offline: `check_expiry` does no network I/O.
"""
from datetime import datetime, timedelta

import pytest

# PUCInsurance imports `requests` at module load; skip if it's not installed.
_puc = pytest.importorskip("checkers.PUCInsurance")
check_expiry = _puc.check_expiry
convert_check = _puc.convert_check
ComplianceStatus = _puc.ComplianceStatus


def _fmt(dt: datetime) -> str:
    # Matches the 'DD-MMM-YYYY' format the checker expects (e.g. 05-Jun-2024).
    return dt.strftime("%d-%b-%Y")


def test_future_date_is_valid():
    future = datetime.today() + timedelta(days=30)
    assert check_expiry(_fmt(future)) == ComplianceStatus.VALID


def test_past_date_is_expired():
    past = datetime.today() - timedelta(days=30)
    assert check_expiry(_fmt(past)) == ComplianceStatus.EXPIRED


def test_today_is_valid_whole_day():
    # A document expiring today should remain VALID for all of today.
    today = _fmt(datetime.today())
    assert check_expiry(today) == ComplianceStatus.VALID


def test_empty_is_unknown():
    assert check_expiry("") == ComplianceStatus.UNKNOWN
    assert check_expiry(None) == ComplianceStatus.UNKNOWN


def test_unparseable_is_error():
    assert check_expiry("not-a-date") == ComplianceStatus.ERROR
    assert check_expiry("2024-06-15") == ComplianceStatus.ERROR  # wrong format


def test_convert_check_true_only_when_valid():
    future = _fmt(datetime.today() + timedelta(days=5))
    past = _fmt(datetime.today() - timedelta(days=5))
    assert convert_check(future) is True
    assert convert_check(past) is False
    assert convert_check("") is False          # unknown -> not valid
    assert convert_check("garbage") is False   # error -> not valid
