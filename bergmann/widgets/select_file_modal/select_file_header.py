import os
from string import ascii_uppercase

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Input, Label, Select, Static


class SelectedFileUnixHeader(Static):
    DEFAULT_CSS = """
    #selected-file-info {
         height: auto;
    }
    #selected-file-label {
        padding-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="selected-file-info"):
            yield Label("Selected file:", id="selected-file-label")
            yield Input(
                placeholder="filename",
                id="selected-file-input",
                disabled=True,
            )


class SelectedFileWindowsHeader(Static):
    DEFAULT_CSS = """
    #selected-file-info {
        height: auto;
    }
    #selected-file-label {
        padding-bottom: 1;
    }
    #selected-file-horizontal {
        height: auto;
        padding-bottom: 1;
    }
    #select-container {
        width: 11;
        height: auto;
        padding: 0;
    }
    #input-container {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="selected-file-info"):
            yield Label("Selected file:", id="selected-file-label")
            with Horizontal(id="selected-file-horizontal"):
                with Container(id="select-container"):
                    items = [
                        (f"{item}:\\", f"{item}:\\")
                        for item in ascii_uppercase
                        if os.path.isdir(f"{item}:\\")
                    ]
                    select = Select(items, allow_blank=False, id="select-volume")
                    yield select
                with Container(id="input-container"):
                    yield Input(
                        placeholder="filename",
                        id="selected-file-input",
                        disabled=True,
                    )
