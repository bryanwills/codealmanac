from codealmanac.core.errors import ValidationFailed


def parse_positive_int(value: str, raw: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise ValidationFailed(f"source number must be positive: {raw}") from error
    if parsed < 1:
        raise ValidationFailed(f"source number must be positive: {raw}")
    return parsed
