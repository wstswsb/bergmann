from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Markdown


class WelcomeWidget(Widget):
    _welcome_text = """Welcome to the `Bergmann` app!  
This app is designed for *securely* storing passwords.  
To select a location for saving your passwords, press **'{}'**.  
"""  # noqa: W291

    def __init__(self, select_source_binding: str, *children: Widget):
        super().__init__(*children)
        self._select_source_binding = select_source_binding

    def compose(self) -> ComposeResult:
        yield Markdown(self._welcome_text.format(self._select_source_binding))
