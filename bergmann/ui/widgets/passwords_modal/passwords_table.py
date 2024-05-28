from textual.binding import Binding
from textual.widgets import DataTable

from bergmann.common.ru_keys import (
    RU_KEY_FOR_EN__H,
    RU_KEY_FOR_EN__J,
    RU_KEY_FOR_EN__K,
    RU_KEY_FOR_EN__L,
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
