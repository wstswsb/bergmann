import platform
from pathlib import Path
from typing import cast

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.types import DirEntry
from textual.widgets import DirectoryTree, Footer, Input, Select

from bergmann.common.ru_keys import RU_T
from bergmann.widgets.select_file_modal.bmn_filtered_directory_tree import (
    BmnFilteredDirectoryTree,
)
from bergmann.widgets.select_file_modal.create_file_modal import CreateFileModal
from bergmann.widgets.select_file_modal.select_file_header import (
    SelectedFileUnixHeader,
    SelectedFileWindowsHeader,
)


class SelectFileModal(ModalScreen[Path | None]):
    AUTO_FOCUS = "BmnFilteredDirectoryTree"
    BINDINGS = (
        Binding(key="n", action="create_file", description="Create new file"),
        Binding(key=RU_T, action="create_file", show=False),
        Binding("escape", "cancel_select_file", ""),
    )
    DEFAULT_CSS = """
    SelectFileModal {
       padding: 1;
    }
    #select-file-modal__directory-tree {
        padding: 0 1;
    }
    """

    _path: Path = Path("/")

    def action_cancel_select_file(self) -> None:
        self.dismiss(None)

    @property
    def presented_path(self) -> str:
        return str(self._path).split(":\\")[-1]

    def compose(self) -> ComposeResult:
        match platform.system():
            case "Windows":
                yield SelectedFileWindowsHeader()
            case _:
                yield SelectedFileUnixHeader()
        with Container(id="select-file-modal__directory-tree"):
            yield BmnFilteredDirectoryTree(Path("/"), id="directory-tree")
        yield Footer()

    @on(Select.Changed)
    def changed_windows_volume(self, event: Select.Changed) -> None:
        self._path = Path(str(event.value))
        directory_tree = self.query_one(BmnFilteredDirectoryTree)
        directory_tree.path = self._path
        directory_tree.refresh()
        selected_file_input = self.query_one(Input)
        selected_file_input.value = self.presented_path

    @work
    async def action_create_file(self) -> None:
        path = await self.app.push_screen_wait(CreateFileModal(self._path))
        if path is None:
            self.notify("file not created", severity="warning")
            return
        self.query_one(Input).value = str(path)
        self.notify(f"file created: {path}")

        await self.query_one(BmnFilteredDirectoryTree).reload()

    @on(Input.Submitted)
    def save_path(self, event: Input.Submitted) -> None:
        self.dismiss(Path(event.value))

    @on(DirectoryTree.NodeHighlighted)
    def update_selected_file(self, event: DirectoryTree.NodeHighlighted) -> None:
        dir_entry = cast(DirEntry, event.node.data)
        self._path = dir_entry.path
        self.query_one(Input).value = self.presented_path

    @on(DirectoryTree.FileSelected)
    def save_selected_file(self, event: DirectoryTree.FileSelected) -> None:
        self._path = event.path
        self.query_one(Input).value = self.presented_path
        self.dismiss(self._path)

    @on(DirectoryTree.DirectorySelected)
    def update_selected_file_input(self, event: DirectoryTree.FileSelected) -> None:
        self._path = event.path
        self.query_one(Input).value = self.presented_path
