from textual.app import App, ComposeResult
from textual.widgets import Footer

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

    def action_select_source(self) -> None:
        self.push_screen(SelectLocationScreen())
