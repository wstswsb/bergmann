from textual.validation import ValidationResult


def present(entity: ValidationResult) -> str:
    return "- " + "\n- ".join(entity.failure_descriptions)
