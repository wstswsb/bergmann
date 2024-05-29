from pathlib import Path

from bergmann.entities.item import Item
from bergmann.files_helper import FilesHelper
from bergmann.passwords_interactor import PasswordsInteractor


class Gateway:
    def __init__(
        self,
        files_helper: FilesHelper,
        passwords_interactor: PasswordsInteractor,
    ):
        self._files_helper = files_helper
        self._passwords_interactor = passwords_interactor

    def is_file_empty(self, path: Path) -> bool:
        return self._files_helper.is_emtpy(path)

    def update(self, path: Path, content: list[Item]) -> None:
        self._passwords_interactor.update_items(content)
        self._passwords_interactor.flush_encrypted_store(path)

    def clean(self) -> None:
        self._passwords_interactor.clean()

    def init_new_store(self, path: Path, password: str) -> list[Item]:
        self._passwords_interactor.initialize_new_store()
        self._passwords_interactor.initialize_key_for_new_db(password)
        self._passwords_interactor.flush_encrypted_store(path)
        return self._passwords_interactor.get_items()

    def load_existent_store(self, path: Path, password: str) -> list[Item]:
        self._passwords_interactor.initialize_key(path, password)
        self._passwords_interactor.decrypt_store(path)
        return self._passwords_interactor.get_items()
