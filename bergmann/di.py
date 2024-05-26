from collections.abc import Callable
from functools import cached_property

from textual.validation import ValidationResult

from bergmann import failures_presenter
from bergmann.passwords_interactor import PasswordsInteractor

__all__ = ["di"]


class DI:
    @cached_property
    def passwords_interactor(self) -> PasswordsInteractor:
        return PasswordsInteractor()

    @cached_property
    def failures_presenter(self) -> Callable[[ValidationResult], str]:
        return failures_presenter.present


di = DI()
