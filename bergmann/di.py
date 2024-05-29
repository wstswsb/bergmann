from collections.abc import Callable
from functools import cached_property

from textual.validation import ValidationResult

from bergmann import failures_presenter
from bergmann.files_helper import FilesHelper
from bergmann.interactor import Interactor
from bergmann.passwords_model import PasswordsModel

__all__ = ["di"]


class DI:
    @cached_property
    def passwords_interactor(self) -> PasswordsModel:
        return PasswordsModel()

    @cached_property
    def failures_presenter(self) -> Callable[[ValidationResult], str]:
        return failures_presenter.present

    @cached_property
    def files_helper(self) -> FilesHelper:
        return FilesHelper()

    @cached_property
    def gateway(self) -> Interactor:
        return Interactor(
            files_helper=self.files_helper,
            passwords_model=self.passwords_interactor,
        )


di = DI()
