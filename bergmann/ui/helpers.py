from textual.widgets import Input


def check_input_value_valid(input_: Input) -> None:
    validation_result = input_.validate(input_.value)
    if validation_result is None:
        return
    if not validation_result.is_valid:
        failures = "- " + "\n- ".join(validation_result.failure_descriptions)
        raise ValueError(failures)
