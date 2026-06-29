from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from hashlib import sha256
import hmac

from ECC import *
from log import timing
from config import GENERATORS, PATH_LENGTH

class ProtocolError(Exception):
    """Base protocol exception."""


class IntegrityError(ProtocolError):
    """Raised when packet integrity verification fails."""


class CredentialError(ProtocolError):
    """Raised when credential verification fails."""

@dataclass(slots=True)
class Header:
    alpha: G1
    beta: list[G1]
    gamma: G1
    next_hop: G1 | None = None

    # ========================================================
    # SERIALIZATION
    # ========================================================

    @classmethod
    def from_encoded(cls, message: list[Any]) -> "Header":
        alpha, *beta, gamma = [G1().deserialize(value) for value in message]
        return cls(alpha=alpha, beta=beta, gamma=gamma)

    def encode(self) -> list[bytes]:
        return [self.alpha.serialize(), *(value.serialize() for value in self.beta), self.gamma.serialize()]

    # ========================================================
    # PROCESSING
    # ========================================================

    @timing
    def process_header(self, secret_key: Fr) -> tuple[str, Header]:
        shared_secret = self.compute_shared_secret(secret_key)

        self.verify_integrity(shared_secret)
        self.decrypt_beta(shared_secret)
        self.update_alpha(shared_secret)

        return (decode_ip(self.next_hop), self)

    @timing
    def compute_shared_secret(self, secret_key: Fr) -> Fr:
        return (self.alpha * secret_key) >> Fr()    
    
    @timing
    def verify_integrity(self, shared_secret: Fr) -> None:
        concatenate_encoding = b"".join(beta.serialize() for beta in self.beta) 
        expected_gamma = G1().hash(hmac.new(shared_secret.serialize(), concatenate_encoding, sha256).digest())

        if self.gamma != expected_gamma:
            raise IntegrityError("Header integrity verification failed")

    @timing
    def decrypt_beta(self, shared_secret: Fr) -> None:
        header = [*self.beta, G1().clear(), G1().clear()]

        for index, value in enumerate(header):
            header[index] = value - GENERATORS[index] * shared_secret

        self.next_hop, self.gamma, *self.beta = header

    @timing
    def update_alpha(self, shared_secret: Fr) -> None:
        self.alpha *= shared_secret