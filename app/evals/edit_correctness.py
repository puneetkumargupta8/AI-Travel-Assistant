from app.state import TripState
from typing import Dict, Any


def evaluate_edit_correctness(
    before: TripState,
    after: TripState,
    intended_day: int
) -> Dict[str, Any]:

    before_dict = before.dict()
    after_dict = after.dict()

    changed_days = []
    unexpected_changes = []

    for i in range(len(before_dict["days"])):
        if before_dict["days"][i] != after_dict["days"][i]:
            changed_days.append(i + 1)

    for day in changed_days:
        if day != intended_day:
            unexpected_changes.append(day)

    status = "PASS" if not unexpected_changes else "FAIL"

    return {
        "changed_days": changed_days,
        "unexpected_changes": unexpected_changes,
        "status": status
    }