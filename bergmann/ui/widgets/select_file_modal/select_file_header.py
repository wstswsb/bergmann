import os
from string import ascii_uppercase

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Input, Label, Select, Static


class SelectedFileUnixHeader(Static):
    DEFAULT_CSS = """
    #selected-file-unix-header__container {
         height: auto;
    }
    #selected-file-unix-header__label {
        padding-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="selected-file-unix-header__container"):
            yield Label("Selected file:", id="selected-file-unix-header__label")
            yield Input(
                placeholder="filename",
                disabled=True,
            )


class SelectedFileWindowsHeader(Static):
    DEFAULT_CSS = """
    #selected-file-windows-header__container {
        height: auto;
    }
    #selected-file-windows-header__label {
        padding-bottom: 1;
        padding-left: 1;
    }
    #selected-file-windows-header__horizontal {
        height: auto;
        padding-bottom: 1;
    }
    #selected-file-windows-header__select-container {
        width: 11;
        height: auto;
        padding: 0;
    }
    #selected-file-windows-header__input-container {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="selected-file-windows-header__container"):
            yield Label("Selected file:", id="selected-file-windows-header__label")
            with Horizontal(id="selected-file-windows-header__horizontal"):
                with Container(id="selected-file-windows-header__select-container"):
                    items = [
                        (f"{item}:\\", f"{item}:\\")
                        for item in ascii_uppercase
                        if os.path.isdir(f"{item}:\\")
                    ]
                    select = Select(items, allow_blank=False, id="select-volume")
                    yield select
                with Container(id="selected-file-windows-header__input-container"):
                    yield Input(
                        placeholder="filename",
                        disabled=True,
                    )
