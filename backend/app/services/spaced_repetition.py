"""
A simplified SM-2 (SuperMemo 2) implementation, adapted for binary
correct/incorrect grading instead of the original 0-5 quality scale --
this fits a "did you play the right move or not" trainer better than
asking the user to self-rate how well they knew it.

Reference on the original algorithm: https://en.wikipedia.org/wiki/SuperMemo
"""

from datetime import datetime, timedelta, timezone

MIN_EASE_FACTOR = 1.3


def review(
    *,
    ease_factor: float,
    interval_days: float,
    repetitions: int,
    correct: bool,
) -> dict:
    """
    Given the current SRS state for a card and whether the user answered
    correctly, compute the next state.

    Returns a dict with the new ease_factor, interval_days, repetitions,
    and next_review_at -- ready to write straight into a TrainingStats row.
    """
    if correct:
        if repetitions == 0:
            new_interval = 1.0
        elif repetitions == 1:
            new_interval = 6.0
        else:
            new_interval = round(interval_days * ease_factor, 2)

        new_repetitions = repetitions + 1
        # Small ease bump on success, mirroring SM-2's quality=4 case.
        new_ease_factor = ease_factor + 0.1
    else:
        # Wrong answer: start the interval over, but don't fully reset
        # ease -- a card you've seen many times shouldn't punish as hard
        # as a brand new one for a single slip.
        new_repetitions = 0
        new_interval = 1.0
        new_ease_factor = max(MIN_EASE_FACTOR, ease_factor - 0.2)

    next_review_at = datetime.now(timezone.utc) + timedelta(days=new_interval)

    return {
        "ease_factor": new_ease_factor,
        "interval_days": new_interval,
        "repetitions": new_repetitions,
        "next_review_at": next_review_at,
        "last_result": "correct" if correct else "incorrect",
    }