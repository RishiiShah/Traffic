"""Tests for the SMS sender's safe-by-default (mock) behaviour.

No Twilio network calls are made: with notifications disabled the sender must
never construct a client or send a message.
"""
import pytest

# sms_sender imports the twilio client at module load; skip if not installed.
SmsSender = pytest.importorskip("sms.sms_sender").SmsSender


def test_mock_mode_by_default(monkeypatch):
    monkeypatch.delenv("ENABLE_NOTIFICATIONS", raising=False)
    sender = SmsSender("sid", "token", "+10000000000")
    assert sender.enabled is False
    assert sender.client is None
    assert sender.send_sms("+19999999999", "hello") == "MOCK-SID"


def test_disabled_explicitly(monkeypatch):
    monkeypatch.setenv("ENABLE_NOTIFICATIONS", "false")
    sender = SmsSender("sid", "token", "+10000000000")
    assert sender.enabled is False
    assert sender.send_sms("+19999999999", "hi") == "MOCK-SID"


def test_enabled_but_missing_credentials_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("ENABLE_NOTIFICATIONS", "true")
    # Empty credentials should force mock mode rather than crash.
    sender = SmsSender("", "", "")
    assert sender.enabled is False
    assert sender.send_sms("+19999999999", "hi") == "MOCK-SID"
