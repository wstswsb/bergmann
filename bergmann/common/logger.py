import logging

from textual.logging import TextualHandler

logging.basicConfig(level="NOTSET", handlers=[TextualHandler()])
logger = logging
