from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Markdown


class WelcomeWidget(Widget):
    _welcome_text = """Welcome to the `Bergmann` app!  
This app is designed for *securely* storing passwords.  
To select a location for saving your passwords, press 'd'.  
"""  # noqa: W291

    def compose(self) -> ComposeResult:
        yield Markdown(self._welcome_text)
