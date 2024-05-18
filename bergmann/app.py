from textual.app import App, ComposeResult
from textual.widgets import Footer

from bergmann.widgets.welcome import WelcomeWidget


class Bergmann(App[None]):
    BINDINGS = [
        ("ctrl+l", "toggle_dark", "Toggle light/dark mode"),
    ]
    CSS_PATH = "bergmann.tcss"

    def compose(self) -> ComposeResult:
        yield WelcomeWidget()
        yield Footer()
