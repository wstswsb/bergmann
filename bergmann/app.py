from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer

from bergmann.common.ru_keys import RU_A
from bergmann.widgets.passwords_modal.passwords_modal import PasswordsModal
from bergmann.widgets.select_file_modal.select_file_modal import SelectFileModal
from bergmann.widgets.welcome import WelcomeWidget


class Bergmann(App[None]):
    BINDINGS = [
        Binding(key="f", action="select_file", description="Select passwords file"),
        Binding(key=RU_A, action="select_file", show=False),
    ]
    CSS_PATH = "bergmann.tcss"

    def compose(self) -> ComposeResult:
        yield WelcomeWidget(select_source_binding="f")
        yield Footer()

    @work
    async def action_select_file(self) -> None:
        path = await self.app.push_screen_wait(SelectFileModal())
        match path:
            case None:
                self.notify("file not selected", severity="warning")
            case Path():
                await self.app.push_screen_wait(PasswordsModal(path))
