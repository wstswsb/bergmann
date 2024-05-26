from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer

from bergmann.common.ru_keys import RU_A
from bergmann.di import di
from bergmann.file_db_helper import FileDBHelper
from bergmann.widgets.passwords_modal.initialize_new_db_modal import (
    InitializeNewDBModal,
)
from bergmann.widgets.passwords_modal.load_db_modal import LoadDBModal
from bergmann.widgets.passwords_modal.passwords_explorer import PasswordsExplorer
from bergmann.widgets.select_file_modal.select_file_modal import SelectFileModal
from bergmann.widgets.welcome import WelcomeWidget


class Bergmann(App[None]):
    BINDINGS = [
        Binding(key="f", action="select_file", description="Select passwords file"),
        Binding(key=RU_A, action="select_file", show=False),
    ]
    CSS_PATH = "bergmann.tcss"

    def __init__(self):
        super().__init__()
        self._file_db_helper = FileDBHelper()
        self._passwords_interactor = di.passwords_interactor

    def compose(self) -> ComposeResult:
        yield WelcomeWidget(select_source_binding="f")
        yield Footer()

    @work
    async def action_select_file(self) -> None:
        path = await self.app.push_screen_wait(SelectFileModal())
        if path is None:
            self.notify("file not selected", severity="warning")
            return
        if self._file_db_helper.is_emtpy(path):
            content = await self.app.push_screen_wait(InitializeNewDBModal(path))

            self.notify(f"new db initialized: {path=}")
        else:
            # self._passwords_interactor.check_header(path)
            content = await self.app.push_screen_wait(LoadDBModal(path))
        if content is None:
            self.notify("file not selected", severity="warning")
            return
        await self.app.push_screen_wait(PasswordsExplorer(content, path))
