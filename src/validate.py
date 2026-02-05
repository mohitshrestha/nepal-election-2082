# validate.py

from src.models import CandidateResult


def validate_entries(raw_entries: list[dict]) -> list[dict]:
    validated = []

    for entry in raw_entries:
        try:
            candidate = CandidateResult.model_validate(entry)
            validated.append(candidate.model_dump(mode="json"))
        except Exception as e:
            print(f"Validation error: {e}")

    return validated
