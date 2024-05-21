from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Footer

from bergmann.models.location import Location
from bergmann.widgets.select_location_screen import SelectLocationScreen
from bergmann.widgets.welcome import WelcomeWidget


class Bergmann(App[None]):
    BINDINGS = [
        ("ctrl+l", "toggle_dark", "Toggle light/dark mode"),
        ("s", "select_source", "Select passwords source"),
    ]
    CSS_PATH = "bergmann.tcss"

    def compose(self) -> ComposeResult:
        yield WelcomeWidget(select_source_binding="s")
        yield Footer()

    @work
    async def action_select_source(self) -> None:
        location = await self.push_screen_wait(SelectLocationScreen())
        match location:
            case Location("FS", _):
                self.notify(f"Filesystem location selected: {location.value}")
            case Location("WEB", _):
                self.notify(f"Web location selected: {location.value}")
