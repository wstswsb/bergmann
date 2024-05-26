from pathlib import Path

import pyperclip
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.coordinate import Coordinate
from textual.screen import ModalScreen
from textual.validation import Length
from textual.widgets import Button, DataTable, Footer, Input, Label

from bergmann.common.ru_keys import (
    RU_KEY_FOR_EN__D,
    RU_KEY_FOR_EN__E,
    RU_KEY_FOR_EN__H,
    RU_KEY_FOR_EN__J,
    RU_KEY_FOR_EN__K,
    RU_KEY_FOR_EN__L,
    RU_KEY_FOR_EN__N,
    RU_KEY_FOR_EN__P,
    RU_KEY_FOR_EN__U,
)
from bergmann.di import di
from bergmann.entities.item import Item


class ItemFieldsModal(ModalScreen[Item | None]):
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
            with Container(id="new-item-modal__inputs-wrapper"):
                with Container(id="new-item-modal__description"):
                    yield Label("Description:")
                    yield Input(
                        value=self.default_description,
                        placeholder="description",
                        id="description-input",
                        validators=Length(minimum=1),
                    )
                with Container(id="new-item-modal__login"):
                    yield Label("Login:")
                    yield Input(
                        value=self.default_login,
                        placeholder="login",
                        id="login-input",
                        validators=Length(minimum=1),
                    )
                with Container(id="new-item-modal__password"):
                    yield Label("Password:")
                    yield Input(
                        value=self.default_password,
                        placeholder="password",
                        id="password-input",
                        password=True,
                        validators=Length(minimum=1),
                    )
                with Container(id="new-item-modal__button"):
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


class PasswordsTable(DataTable):
    BINDINGS = [
        *DataTable.BINDINGS,
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("j", "cursor_down", "Cursor Down", show=False),
        Binding("l", "cursor_right", "Cursor Right", show=False),
        Binding("h", "cursor_left", "Cursor Left", show=False),
        Binding(RU_KEY_FOR_EN__K, "cursor_up", "Cursor Up", show=False),
        Binding(RU_KEY_FOR_EN__J, "cursor_down", "Cursor Down", show=False),
        Binding(RU_KEY_FOR_EN__L, "cursor_right", "Cursor Right", show=False),
        Binding(RU_KEY_FOR_EN__H, "cursor_left", "Cursor Left", show=False),
    ]


class PasswordsExplorer(ModalScreen[None]):
    BINDINGS = (
        Binding(key="escape", action="quit", description="Quit"),
        Binding(key="u", action="copy_login", description="Copy login"),
        Binding(key="p", action="copy_password", description="Copy password"),
        Binding(key="d", action="copy_description", description="Copy description"),
        Binding(key="n", action="add_new_item", description="New"),
        Binding(key="e", action="edit_item", description="Edit"),
        Binding(RU_KEY_FOR_EN__U, action="copy_login", show=False),
        Binding(RU_KEY_FOR_EN__P, action="copy_password", show=False),
        Binding(RU_KEY_FOR_EN__D, action="copy_description", show=False),
        Binding(RU_KEY_FOR_EN__N, action="add_new_item", show=False),
        Binding(RU_KEY_FOR_EN__E, action="edit_item", show=False),
        Binding(key="delete", action="delete_item", description="Delete"),
    )

    def __init__(
        self,
        content: list[Item],
        path: Path,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._interactor = di.passwords_interactor
        self._failures_presenter = di.failures_presenter
        self._content = content
        self._path = path

    @work
    async def action_edit_item(self) -> None:
        dt = self.query_one(DataTable)
        if dt.row_count == 0:
            return
        row_key, _ = dt.coordinate_to_cell_key(dt.cursor_coordinate)
        row_index = dt.cursor_row
        login_coordinate = Coordinate(row_index, 0)
        description_coordinate = Coordinate(row_index, 1)
        item = self._content[row_index]
        new_item = await self.app.push_screen_wait(
            ItemFieldsModal(
                description=item.description,
                login=item.login,
                password=item.password,
            )
        )
        if new_item is None:
            return
        self._content[row_index] = new_item
        self._interactor.update(self._content, self._path)
        dt.update_cell_at(login_coordinate, new_item.login)
        dt.update_cell_at(description_coordinate, new_item.description)

    def action_delete_item(self) -> None:
        dt = self.query_one(DataTable)
        if dt.row_count == 0:
            return
        row_key, _ = dt.coordinate_to_cell_key(dt.cursor_coordinate)
        row_index = dt.cursor_row
        self._content.pop(row_index)
        self._interactor.update(self._content, self._path)
        dt.remove_row(row_key)

    @work
    async def action_add_new_item(self) -> None:
        item = await self.app.push_screen_wait(ItemFieldsModal())
        if item is None:
            self.notify("no item created", severity="warning")
            return
        self._content.append(item)
        dt = self.query_one(DataTable)
        self._interactor.update(self._content, self._path)
        dt.add_row(item.login, item.description)

    def action_copy_login(self) -> None:
        item = self.get_current_item()
        pyperclip.copy(item.login)
        self.notify("Login copied to clipboard", timeout=1)

    def action_copy_password(self) -> None:
        item = self.get_current_item()
        pyperclip.copy(item.password)
        self.notify("Password copied to clipboard")

    def action_copy_description(self) -> None:
        item = self.get_current_item()
        pyperclip.copy(item.description)
        self.notify("Description copied to clipboard")

    def get_current_item(self) -> Item:
        dt = self.query_one(DataTable)
        row_item = dt.cursor_row
        item = self._content[row_item]
        return item

    def compose(self) -> ComposeResult:
        with Container(id="passwords-explorer__selected_file"):
            yield Label(f"Path: {self._path}")
        with Container(id="passwords-explorer__data-table"):
            yield PasswordsTable()

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "cell"
        table.zebra_stripes = True
        table.add_columns("login", "description")
        table.add_rows((item.login, item.description) for item in self._content)

    def action_quit(self) -> None:
        self.dismiss(None)
