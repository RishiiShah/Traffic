import os

from twilio.rest import Client


def _notifications_enabled() -> bool:
    """SMS is opt-in. Set ENABLE_NOTIFICATIONS=true to send real messages."""
    return os.getenv("ENABLE_NOTIFICATIONS", "false").strip().lower() in (
        "1", "true", "yes", "on",
    )


class SmsSender:
    """Twilio SMS wrapper with a safe, mock-by-default mode.

    Unless ENABLE_NOTIFICATIONS is truthy in the environment, no Twilio client
    is created and `send_sms` only logs what *would* have been sent. This keeps
    a freshly cloned project from texting a real number during a demo/test run.
    """

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.enabled = _notifications_enabled()
        self.from_number = from_number
        self.client = None
        if self.enabled:
            if not (account_sid and auth_token and from_number):
                print(
                    "[!] ENABLE_NOTIFICATIONS is on but Twilio credentials are "
                    "incomplete; falling back to mock mode."
                )
                self.enabled = False
            else:
                self.client = Client(account_sid, auth_token)

    def send_sms(self, to_number: str, body: str) -> str:
        """Send `body` to `to_number` and return the Twilio message SID.

        In mock mode returns a 'MOCK-...' identifier instead of sending.
        """
        if not self.enabled or self.client is None:
            print(f"[MOCK SMS] to={to_number!r} body={body!r}")
            return "MOCK-SID"

        msg = self.client.messages.create(
            body=body,
            from_=self.from_number,
            to=to_number,
        )
        return msg.sid
