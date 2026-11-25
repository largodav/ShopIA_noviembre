"""Genera un par de claves VAPID (pública y privada en base64url) para Web Push."""

import base64

from cryptography.hazmat.primitives import serialization
from py_vapid import Vapid02


def generate_keys() -> tuple[str, str]:
    vapid = Vapid02()
    vapid.generate_keys()

    raw_public = vapid.public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )
    raw_private = vapid.private_key.private_numbers().private_value.to_bytes(32, "big")

    public_b64 = base64.urlsafe_b64encode(raw_public).rstrip(b"=").decode("ascii")
    private_b64 = base64.urlsafe_b64encode(raw_private).rstrip(b"=").decode("ascii")
    return public_b64, private_b64


if __name__ == "__main__":
    pub, priv = generate_keys()
    print(f"VAPID_PUBLIC_KEY={pub}")
    print(f"VAPID_PRIVATE_KEY={priv}")
