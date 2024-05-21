import os

from textual.validation import ValidationResult, Validator


class FileAlreadyExistsValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if os.path.exists(value):
            return self.failure("Already exists")
        return self.success()
