from pathlib import Path
from typing import cast

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.types import DirEntry
from textual.widgets import Button, DirectoryTree, Footer, Input, Label


class SelectFileModal(ModalScreen[Path]):
    AUTO_FOCUS = "#directory-tree"

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Selected file:")
            yield Input(placeholder="filename", id="selected-file-input", disabled=True)
            yield DirectoryTree("/", id="directory-tree")
            yield Footer()

    @on(Input.Submitted)
    def save_path(self, event: Input.Submitted) -> None:
        self.dismiss(Path(event.value))

    @on(DirectoryTree.NodeHighlighted)
    def update_selected_file(self, event: DirectoryTree.NodeHighlighted) -> None:
        dir_entry = cast(DirEntry, event.node.data)
        self.query_one(Input).value = str(dir_entry.path)

    @on(DirectoryTree.FileSelected)
    def save_selected_file(self, event: DirectoryTree.FileSelected) -> None:
        self.query_one(Input).value = str(event.path)
        self.dismiss(event.path)

    @on(DirectoryTree.DirectorySelected)
    def update_selected_file_input(self, event: DirectoryTree.FileSelected) -> None:
        file_selected = event.path
        self.query_one(Input).value = str(file_selected)


class SelectLocationScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        with Container():
            yield Button("file", id="file-button")
            yield Button("server (not implemented now)", disabled=True)

    @work
    @on(Button.Pressed, "#file-button")
    async def show_directory_tree(self) -> None:
        path = await self.app.push_screen_wait(SelectFileModal())
        self.app.notify(f"Selected path is {path}")
