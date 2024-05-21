from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.validation import ValidationResult
from textual.widgets import Input, Label

from bergmann.validators.bmn_filename_validator import BmnFilenameValidator
from bergmann.validators.file_already_exists_validator import FileAlreadyExistsValidator


class CreateFileModal(ModalScreen[Path | None]):
    BINDINGS = (("escape", "cancel_creation", ""),)

    def __init__(self, default_path: Path):
        self.default_path = default_path
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Filename:")
            yield Input(
                placeholder="filename",
                value=str(self.default_path),
                validators=[
                    FileAlreadyExistsValidator(),
                    BmnFilenameValidator(),
                ],
            )

    def action_cancel_creation(self) -> None:
        self.dismiss(None)

    @on(Input.Submitted)
    def handle_input_submitted(self, event: Input.Submitted) -> None:
        try:
            self.__check_input_value_valid(event.input)
            self._create_file(event.value)
            self.dismiss(Path(event.value))
        except Exception as e:
            self.notify(
                message=f"file with path={event.value} not created due to:\n{e!s}",
                severity="error",
            )

    def _create_file(self, path: str) -> None:
        Path(path).touch(exist_ok=False)

    def __check_input_value_valid(self, input_: Input) -> None:
        validation_result = input_.validate(input_.value)
        if not validation_result.is_valid:
            failures = self.__present_failures(validation_result)
            raise ValueError(failures)

    def __present_failures(self, validation_result: ValidationResult) -> str:
        return "- " + "\n- ".join(validation_result.failure_descriptions)
