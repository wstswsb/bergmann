from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class EncryptedItem:
    description: bytes
    login: bytes
    password: bytes

    def as_hex_tuple(self) -> tuple[str, str, str]:
        return self.description.hex(), self.login.hex(), self.password.hex()
