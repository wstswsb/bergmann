from pathlib import Path

from bergmann.entities.item import Item
from bergmann.files_helper import FilesHelper
from bergmann.passwords_model import PasswordsModel


class Interactor:
    def __init__(
        self,
        files_helper: FilesHelper,
        passwords_model: PasswordsModel,
    ):
        self._files_helper = files_helper
        self._passwords_model = passwords_model

    def is_store_initialized(self, path: Path) -> bool:
        return self._files_helper.is_emtpy(path)

    def init_new_store(self, path: Path, password: str) -> list[Item]:
        self._passwords_model.initialize_new_store()
        self._passwords_model.initialize_key_for_new_db(password)
        self._passwords_model.flush_encrypted_store(path)
        return self._passwords_model.get_items()

    def load_existent_store(self, path: Path, password: str) -> list[Item]:
        self._passwords_model.initialize_key(path, password)
        self._passwords_model.decrypt_store(path)
        return self._passwords_model.get_items()

    def update(self, path: Path, content: list[Item]) -> None:
        self._passwords_model.update_items(content)
        self._passwords_model.flush_encrypted_store(path)

    def clean(self) -> None:
        self._passwords_model.clean()
