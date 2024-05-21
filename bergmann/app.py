from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Footer

from bergmann.widgets.select_file_modal.select_file_modal import SelectFileModal
from bergmann.widgets.welcome import WelcomeWidget


class Bergmann(App[None]):
    BINDINGS = [
        ("f", "select_file", "Select passwords file"),
    ]
    CSS_PATH = "bergmann.tcss"

    def compose(self) -> ComposeResult:
        yield WelcomeWidget(select_source_binding="f")
        yield Footer()

    @work
    async def action_select_file(self) -> None:
        path = await self.app.push_screen_wait(SelectFileModal())
        self.notify(f"file selected: {path}")
