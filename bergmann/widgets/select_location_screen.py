import logging
from pathlib import Path
from typing import Iterable, cast

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container
from textual.logging import TextualHandler
from textual.screen import ModalScreen
from textual.types import DirEntry
from textual.widgets import Button, DirectoryTree, Footer, Input, Label

from bergmann.models.location import Location
from bergmann.validators.bmn_filename_validator import BmnFilenameValidator
from bergmann.validators.file_already_exists_validator import FileAlreadyExistsValidator

logging.basicConfig(level="NOTSET", handlers=[TextualHandler()])
"""
In [5]: [f"{item}:\\" for item in ascii_uppercase if os.path.isdir(f"{item}:\\")]
Out[5]: ['C:\\']
"""


class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        for path in paths:
            try:
                if self._is_bmn_file(path) or self._is_not_empty_dir(path):
                    yield path
            except PermissionError:
                logging.debug(f"permission error for {path}")

    def _is_not_empty_dir(self, path: Path) -> bool:
        if not path.is_dir():
            return False
        return bool(list(path.iterdir()))

    def _is_bmn_file(self, path: Path) -> bool:
        if not path.is_file():
            return False
        return path.name.endswith(".bmn")


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
    def save_file(self, event: Input.Submitted) -> None:
        try:
            validation_result = event.input.validate(event.input.value)
            if validation_result is not None:
                raise ValueError(
                    "- " + "\n- ".join(validation_result.failure_descriptions)
                )
            Path(event.value).touch(exist_ok=False)
            self.notify(f"file with path={event.value} created")
            self.dismiss(Path(event.value))
        except Exception as e:
            self.notify(
                f"file with path={event.value} not created due to:\n{e!s}",
                severity="error",
            )


class SelectFileModal(ModalScreen[Path]):
    AUTO_FOCUS = "#directory-tree"
    BINDINGS = (("n", "create_file", "Create new file"),)

    _path: Path = Path("/")

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Selected file:")
            yield Input(placeholder="filename", id="selected-file-input", disabled=True)
            yield FilteredDirectoryTree(Path("/"), id="directory-tree")
            yield Footer()

    @work
    async def action_create_file(self) -> None:
        path = await self.app.push_screen_wait(CreateFileModal(self._path))
        if path is None:
            self.notify("file not created", severity="warning")
            return
        self.query_one(Input).value = str(path)
        self.notify(f"file created: {path}")

        await self.query_one(FilteredDirectoryTree).reload()

    @on(Input.Submitted)
    def save_path(self, event: Input.Submitted) -> None:
        self.dismiss(Path(event.value))

    @on(DirectoryTree.NodeHighlighted)
    def update_selected_file(self, event: DirectoryTree.NodeHighlighted) -> None:
        dir_entry = cast(DirEntry, event.node.data)
        self.query_one(Input).value = str(dir_entry.path)
        self._path = dir_entry.path

    @on(DirectoryTree.FileSelected)
    def save_selected_file(self, event: DirectoryTree.FileSelected) -> None:
        self.query_one(Input).value = str(event.path)
        self.dismiss(event.path)

    @on(DirectoryTree.DirectorySelected)
    def update_selected_file_input(self, event: DirectoryTree.FileSelected) -> None:
        file_selected = event.path
        self.query_one(Input).value = str(file_selected)


class SelectLocationScreen(ModalScreen[Location]):
    def compose(self) -> ComposeResult:
        with Container():
            yield Button("file", id="file-button")
            yield Button("server (not implemented now)", disabled=True)

    @work
    @on(Button.Pressed, "#file-button")
    async def show_directory_tree(self) -> None:
        path = await self.app.push_screen_wait(SelectFileModal())
        self.dismiss(Location.path(path))
