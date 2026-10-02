"""One-time sign-in codes: the part phone and email sign-in share.

Extracted from phone_auth.py (DIVASTRO-102) when email codes arrived
(DIVASTRO-104), because the dangerous half of an OTP flow — how codes are
generated, stored, rate-limited, compared and burned — must not exist in two
copies that can drift apart. What differs per channel stays in its own module:
how an address is normalised, how a code is delivered, the wording of errors,
and how a verified address becomes an account.

A ``CodeBook`` holds the pending codes and the limiter stores for one channel.
It refuses with ``Refused(status, reason, **info)`` rather than an
HTTPException so each channel can phrase the refusal itself (phone answers in
English, email in the visitor's language).

Everything is in memory: production is one process (`--workers 1`), and the
worst a restart does is make someone tap "resend". Codes are HMAC'd with
ASTRO_SECRET_KEY all the same, so a memory dump or a stray debug print never
shows one. If this ever scales past one worker, the pending codes and the
limiter stores have to move to the database together.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass, field
from typing import Callable

from . import auth


@dataclass
class Pending:
    digest: str
    sent_at: float
    expires_at: float
    attempts: int = 0


class Refused(Exception):
    """Why a send or a check was refused. ``reason`` is one of: cooldown
    (info: wait), ip_sends, key_sends, send_failed, ip_fails, expired,
    wrong (info: left), burned."""

    def __init__(self, status: int, reason: str, **info: int) -> None:
        super().__init__(reason)
        self.status, self.reason, self.info = status, reason, info


@dataclass
class CodeBook:
    ttl: int
    max_attempts: int
    cooldown: int
    per_key: tuple[int, float]           # (limit, window seconds)
    per_key_daily: tuple[int, float]
    per_ip: tuple[int, float]
    fails_per_ip: tuple[int, float]
    digits: int = 6

    pending: dict[str, Pending] = field(default_factory=dict)
    sends_by_key: dict[str, list[float]] = field(default_factory=dict)
    sends_by_key_daily: dict[str, list[float]] = field(default_factory=dict)
    sends_by_ip: dict[str, list[float]] = field(default_factory=dict)
    fails_by_ip: dict[str, list[float]] = field(default_factory=dict)

    def digest(self, key: str, code: str) -> str:
        return hmac.new(auth.SECRET.encode(), f"{key}|{code}".encode(),
                        hashlib.sha256).hexdigest()

    def issue(self, key: str, ip: str, deliver: Callable[[str], bool]) -> None:
        """Generate a code for ``key``, hand it to ``deliver``, remember its HMAC.

        Replaces any earlier unused code for the same key. ``deliver`` returns
        False on failure and must never raise.
        """
        now = time.monotonic()
        pending = self.pending.get(key)
        if pending and now - pending.sent_at < self.cooldown:
            raise Refused(429, "cooldown", wait=int(self.cooldown - (now - pending.sent_at)) + 1)
        if auth.throttled(self.sends_by_ip, ip, *self.per_ip):
            raise Refused(429, "ip_sends")
        if (auth.throttled(self.sends_by_key, key, *self.per_key)
                or auth.throttled(self.sends_by_key_daily, key, *self.per_key_daily)):
            raise Refused(429, "key_sends")

        # Counted before sending, and whether or not it succeeds: a failing
        # gateway must not become an unlimited retry loop at our expense.
        auth.note_hit(self.sends_by_ip, ip)
        auth.note_hit(self.sends_by_key, key)
        auth.note_hit(self.sends_by_key_daily, key)

        code = f"{secrets.randbelow(10 ** self.digits):0{self.digits}d}"
        if not deliver(code):
            raise Refused(502, "send_failed")
        self.pending[key] = Pending(digest=self.digest(key, code), sent_at=now,
                                    expires_at=now + self.ttl)

    def check(self, key: str, code: str, ip: str) -> None:
        """Return if ``code`` is right for ``key``; burn it. Else raise Refused.

        The caller has already checked the code's length: a typo in length is
        not a guess, so it must not reach here and use up an attempt.
        """
        if auth.throttled(self.fails_by_ip, ip, *self.fails_per_ip):
            raise Refused(429, "ip_fails")

        pending = self.pending.get(key)
        if pending is None or time.monotonic() >= pending.expires_at:
            self.pending.pop(key, None)
            raise Refused(400, "expired")

        if not hmac.compare_digest(pending.digest, self.digest(key, code)):
            pending.attempts += 1
            auth.note_hit(self.fails_by_ip, ip)
            left = self.max_attempts - pending.attempts
            if left <= 0:
                self.pending.pop(key, None)
                raise Refused(429, "burned")
            raise Refused(400, "wrong", left=left)

        self.pending.pop(key, None)

    def reset(self) -> None:
        """Forget every pending code and limiter hit. Tests only."""
        for store in (self.pending, self.sends_by_key, self.sends_by_key_daily,
                      self.sends_by_ip, self.fails_by_ip):
            store.clear()
