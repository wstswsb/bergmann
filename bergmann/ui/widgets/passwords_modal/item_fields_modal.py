from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.validation import Length
from textual.widgets import Button, Footer, Input, Label

from bergmann.entities.item import Item


class ItemFieldsModal(ModalScreen[Item | None]):
    DEFAULT_CSS = """
    ItemFieldsModal Label {
        padding: 0 0 0 1;
    }
    #item-fields-modal__inputs-wrapper {
        height: 1fr;
        width: auto;
        padding: 0 5;
        align: center middle;
    }
    #item-fields-modal__description {
        height: auto;
    }
    #item-fields-modal__login {
        height: auto;
        margin: 1 0 0 0;
    }
    #item-fields-modal__password {
        height: auto;
        margin: 1 0 0 0;
     }
    #item-fields-modal__button {
        height: auto;
        align: center top;
        margin: 1 0 0 0;
    }
    """
    BINDINGS = (Binding(key="escape", action="quit", description="Quit"),)

    def __init__(
        self,
        description: str = "",
        login: str = "",
        password: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.default_description = description
        self.default_login = login
        self.default_password = password

    def action_quit(self):
        self.dismiss(None)

    def compose(self) -> ComposeResult:
        with Container():
            with Container(id="item-fields-modal__inputs-wrapper"):
                with Container(id="item-fields-modal__description"):
                    yield Label("Description:")
                    yield Input(
                        value=self.default_description,
                        placeholder="description",
                        id="description-input",
                        validators=Length(minimum=1),
                    )
                with Container(id="item-fields-modal__login"):
                    yield Label("Login:")
                    yield Input(
                        value=self.default_login,
                        placeholder="login",
                        id="login-input",
                        validators=Length(minimum=1),
                    )
                with Container(id="item-fields-modal__password"):
                    yield Label("Password:")
                    yield Input(
                        value=self.default_password,
                        placeholder="password",
                        id="password-input",
                        password=True,
                        validators=Length(minimum=1),
                    )
                with Container(id="item-fields-modal__button"):
                    yield Button("Save")
        yield Footer()

    @on(Button.Pressed)
    def handle_button_pressed(self) -> None:
        description_input = self.query_one("#description-input", Input)
        login_input = self.query_one("#login-input", Input)
        password_input = self.query_one("#password-input", Input)

        errors = []
        if not description_input.is_valid:
            errors.append("description cannot be empty")
        if not login_input.is_valid:
            errors.append("login cannot be empty")
        if not password_input.is_valid:
            errors.append("password cannot be empty")
        if errors:
            self.notify("- " + "\n- ".join(errors), severity="error")
            return
        self.dismiss(
            Item(description_input.value, login_input.value, password_input.value)
        )
