from textual.validation import ValidationResult, Validator


class BmnFilenameValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value.endswith(".bmn"):
            return self.failure("Missed .bmn extension")
        return self.success()
