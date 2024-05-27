from collections.abc import Callable
from functools import cached_property

from textual.validation import ValidationResult

from bergmann import failures_presenter
from bergmann.files_helper import FilesHelper
from bergmann.gateway import Gateway
from bergmann.passwords_interactor import PasswordsInteractor

__all__ = ["di"]


class DI:
    @cached_property
    def passwords_interactor(self) -> PasswordsInteractor:
        return PasswordsInteractor()

    @cached_property
    def failures_presenter(self) -> Callable[[ValidationResult], str]:
        return failures_presenter.present

    @cached_property
    def files_helper(self) -> FilesHelper:
        return FilesHelper()

    @cached_property
    def gateway(self) -> Gateway:
        return Gateway(
            files_helper=self.files_helper,
        )


di = DI()
