from pathlib import Path

import pyperclip
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.coordinate import Coordinate
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Label

from bergmann.common.ru_keys import (
    RU_KEY_FOR_EN__D,
    RU_KEY_FOR_EN__E,
    RU_KEY_FOR_EN__N,
    RU_KEY_FOR_EN__P,
    RU_KEY_FOR_EN__U,
)
from bergmann.di import di
from bergmann.entities.item import Item
from bergmann.ui.widgets.passwords_modal.item_fields_modal import ItemFieldsModal
from bergmann.ui.widgets.passwords_modal.passwords_table import PasswordsTable


class PasswordsExplorer(ModalScreen[None]):
    DEFAULT_CSS = """
    #passwords-explorer__selected_file {
        height: auto;
        padding: 1 2 1 2;
    }
    #passwords-explorer__data-table {
        padding: 0 1 1 1;
        border: green;
    }
    """
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
        self._gateway = di.gateway
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
        self._gateway.update(self._path, self._content)
        dt.update_cell_at(login_coordinate, new_item.login)
        dt.update_cell_at(description_coordinate, new_item.description)

    def action_delete_item(self) -> None:
        dt = self.query_one(DataTable)
        if dt.row_count == 0:
            return
        row_key, _ = dt.coordinate_to_cell_key(dt.cursor_coordinate)
        row_index = dt.cursor_row
        self._content.pop(row_index)
        self._gateway.update(self._path, self._content)
        dt.remove_row(row_key)

    @work
    async def action_add_new_item(self) -> None:
        item = await self.app.push_screen_wait(ItemFieldsModal())
        if item is None:
            self.notify("no item created", severity="warning")
            return
        self._content.append(item)
        dt = self.query_one(DataTable)
        self._gateway.update(self._path, self._content)
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
