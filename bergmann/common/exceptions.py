from typing import Literal


class InvalidHeader(Exception):
    def __init__(
        self,
        reason: Literal["magic-bytes", "alg", "salt", "iterations", "content-hash"],
        *args,
    ):
        self.reason = reason
        super().__init__(*args)


class IntegrityError(Exception):
    pass
