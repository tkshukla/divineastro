"""Print a fresh VAPID key pair for the daily web push (DIVASTRO-112).

    python -m app.push_keys

Paste the three lines into the production env file (.env.production), never
into the repo. The public key is what browsers subscribe with; the private
key signs every push. Rotating them invalidates every existing subscription
(browsers must subscribe again), so generate once and keep them.
"""

from __future__ import annotations

import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def generate() -> tuple[str, str]:
    """(public, private): the uncompressed P-256 point and the raw 32-byte
    scalar, both base64url without padding — the forms browsers'
    `applicationServerKey` and py_vapid's `from_string` take."""
    key = ec.generate_private_key(ec.SECP256R1())
    private = key.private_numbers().private_value.to_bytes(32, "big")
    public = key.public_key().public_bytes(serialization.Encoding.X962,
                                           serialization.PublicFormat.UncompressedPoint)
    return _b64url(public), _b64url(private)


if __name__ == "__main__":
    pub, priv = generate()
    print(f"ASTRO_VAPID_PUBLIC_KEY={pub}")
    print(f"ASTRO_VAPID_PRIVATE_KEY={priv}")
    print("ASTRO_VAPID_SUBJECT=mailto:support@divineastro.org")
