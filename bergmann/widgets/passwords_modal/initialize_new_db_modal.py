from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.validation import Length
from textual.widgets import Button, Footer, Input, Label

from bergmann.di import di
from bergmann.entities.item import Item


class InitializeNewDBModal(ModalScreen[list[Item] | None]):
    DEFAULT_CSS = """
    #initialize-new-db-modal__text-wrapper {
        padding: 0 5;
        width: 1fr;
        height:1fr;
        align: center middle;
    }
    #initialize-new-db-modal__title {
        padding: 0 1;
        width: 100%;
        height: auto;
        text-align: left;
    }
    #initialize-new-db-modal__input-wrapper {
        height: auto;
        margin: 1 0 0 0;
        align: left top;
    }
    #initialize-new-db-modal__label {
        padding: 0 1;
    }
    #initialize-new-db-modal__input {
        margin: 1 0 0 0;
    }
    #initialize-new-db-modal__button {
        height: auto;
        align: center top;
    }
    #initialize-new-db-modal__init-db-button {
        margin: 1 0 0 0;
    }
    """
    BINDINGS = (Binding(key="escape", action="quit", description="Quit"),)

    def __init__(
        self,
        path: Path,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._interactor = di.passwords_interactor
        self._failures_presenter = di.failures_presenter
        self._path = path

    def action_quit(self) -> None:
        self.dismiss(None)

    def compose(self) -> ComposeResult:
        with Container():
            with Container(id="initialize-new-db-modal__text-wrapper"):
                yield Label(
                    renderable=(
                        "The file: "
                        f"[italic bold red]{self._path.name}[/italic bold red] "
                        "is empty. \n"
                        "To initialize the database, enter a new master password."
                    ),
                    id="initialize-new-db-modal__title",
                )
                with Container(id="initialize-new-db-modal__input-wrapper"):
                    yield Label(
                        "Master password:",
                        id="initialize-new-db-modal__label",
                    )
                    yield Input(
                        placeholder="master-password",
                        id="initialize-new-db-modal__input",
                        password=True,
                        validators=[Length(minimum=8)],
                    )
                with Container(id="initialize-new-db-modal__button"):
                    yield Button(
                        "Set password",
                        id="initialize-new-db-modal__init-db-button",
                    )
        yield Footer()

    @on(Button.Pressed)
    def handle_button_pressed(self, event: Button.Pressed) -> None:
        master_password_input = self.query_one(Input)
        self.handle_password_submit(master_password_input)

    @on(Input.Submitted, selector="#initialize-new-db-modal__input")
    def handle_input_submitted(self, event: Input.Submitted) -> None:
        self.handle_password_submit(event.input)

    def handle_password_submit(self, input_: Input) -> None:
        try:
            self.__check_input_value_valid(input_)
            master_password = input_.value
            self._interactor.initialize_key(master_password)
            self._interactor.initialize_new_db(self._path)
            content = self._interactor.decrypt(self._path, master_password)
            self.dismiss(content)
        except Exception as e:
            self.notify(
                message=f"password invalid:\n{e!s}",
                severity="error",
            )

    def __check_input_value_valid(self, input_: Input) -> None:
        validation_result = input_.validate(input_.value)
        if validation_result is None:
            return
        if not validation_result.is_valid:
            raise ValueError(self._failures_presenter(validation_result))
