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
        self._passwords_interactor.update(content, path)

    def clean(self) -> None:
        self._passwords_interactor.delete_key()

    def init_new_store(self, path: Path, password: str) -> list[Item]:
        self._passwords_interactor.initialize_key(password)
        self._passwords_interactor.initialize_new_db(path)
        return self._passwords_interactor.decrypt(path, password)

    def load_existent_store(self, path: Path, password: str) -> list[Item]:
        self._passwords_interactor.initialize_key(password)
        return self._passwords_interactor.decrypt(path, password)
