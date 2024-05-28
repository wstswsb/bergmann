from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer

from bergmann.common.ru_keys import RU_KEY_FOR_EN__F
from bergmann.di import di
from bergmann.entities.item import Item
from bergmann.entities.load_db_result import LoadDBResult
from bergmann.ui.widgets.passwords_modal.initialize_new_db_modal import (
    InitializeNewStoreModal,
)
from bergmann.ui.widgets.passwords_modal.load_db_modal import LoadDBModal
from bergmann.ui.widgets.passwords_modal.passwords_explorer import PasswordsExplorer
from bergmann.ui.widgets.select_file_modal.select_file_modal import SelectFileModal
from bergmann.ui.widgets.welcome import WelcomeWidget


class Bergmann(App[None]):
    BINDINGS = [
        Binding(key="f", action="select_file", description="Select passwords file"),
        Binding(key=RU_KEY_FOR_EN__F, action="select_file", show=False),
    ]

    def __init__(self, debug: bool):
        super().__init__()
        self._gateway = di.gateway
        self._debug = debug

    def compose(self) -> ComposeResult:
        yield WelcomeWidget(select_source_binding="f")
        yield Footer()

    @work
    async def action_select_file(self) -> None:
        path = await self._select_file()
        if path is None:
            self.notify("file not selected", severity="warning")
            return
        load_db_result = await self._load_db(path)
        if not load_db_result.content:
            self.notify("file not selected", severity="warning")
            return
        if load_db_result.new_db_initialized:
            self.notify(f"new db initialized: {path=}")
        await self._show_passwords_explorer(load_db_result.content, path)
        self._gateway.clean()

    async def _show_passwords_explorer(self, content: list[Item], path: Path) -> None:
        await self.app.push_screen_wait(PasswordsExplorer(content, path))

    async def _select_file(self) -> Path | None:
        return await self.app.push_screen_wait(SelectFileModal())

    async def _load_db(self, path: Path) -> LoadDBResult:
        if not self._gateway.is_file_empty(path):
            return LoadDBResult.existent_db(await self._load_existent_db(path))
        return LoadDBResult.new_db(await self._initialize_new_db(path))

    async def _initialize_new_db(self, path: Path) -> list[Item] | None:
        return await self.app.push_screen_wait(InitializeNewStoreModal(path))

    async def _load_existent_db(self, path: Path) -> list[Item] | None:
        return await self.app.push_screen_wait(LoadDBModal(path))

    def _handle_exception(self, error: Exception) -> None:
        if not self._debug:
            raise error
        super()._handle_exception(error)
