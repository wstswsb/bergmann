import os
from dataclasses import dataclass
from typing import Self


@dataclass(slots=True)
class Item:
    description: str
    login: str
    password: str

    def as_tuple(self) -> tuple[str, str, str]:
        return self.description, self.login, self.password

    @classmethod
    def example(cls) -> Self:
        return cls(
            description=f"site: vk.com: {os.urandom(6)}",
            login=f"example login: {os.urandom(6)}",
            password=f"example password: {os.urandom(6)}",
        )
